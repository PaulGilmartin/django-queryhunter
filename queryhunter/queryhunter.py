import contextlib
import linecache
import os
import time
import traceback
from dataclasses import dataclass

from django.conf import settings
from django.db import connection


@dataclass
class LineData:
    line_no: int
    code: str
    sql: str
    count: int
    duration: float

    def __str__(self):
        return (f'Line no: {self.line_no} Code: {self.code} '
                f'Num. Queries: {self.count} SQL: {self.sql} Duration: {self.duration}')


@dataclass
class FileData:
    filename: str
    line_data: dict[int, LineData]

    def __str__(self):
        data = ''
        for line_data in self.line_data.values():
            data += f'Module: {self.filename} {line_data} \n'
        data.rstrip('\n')
        return data


class QueryHunter:
    def __init__(self):
        self.query_info: dict[str, FileData] = {}

    def __call__(self, execute, sql, params, many, context):
        # Capture traceback at the point of SQL execution
        stack_trace = traceback.extract_stack()[:-1]  # Exclude the current frame

        # Iterate through the traceback to find the relevant application frame
        app_frame = None

        for frame in reversed(stack_trace):
            filename = frame.filename
            if self.is_application_code(filename):
                app_frame = frame
                break

        if app_frame:
            filename = app_frame.filename
            relative_path = str(os.path.relpath(app_frame.filename, settings.QUERYHUNTER_BASE_DIR))
            file_data = self.query_info.get(relative_path, FileData(relative_path, line_data={}))

            line_no = app_frame.lineno
            code = self.get_code_from_line(filename, line_no)
            start = time.monotonic()
            result = execute(sql, params, many, context)
            duration = time.monotonic() - start

            try:
                line_data = file_data.line_data[line_no]
            except KeyError:
                line_data = LineData(line_no=line_no, code=code, sql=sql, count=1, duration=duration)
                file_data.line_data[line_no] = line_data
            else:
                line_data.count += 1
                line_data.duration += duration

            self.query_info[relative_path] = file_data
            return result
        else:
            raise ValueError("Unable to determine application frame for SQL execution")

    @staticmethod
    def is_application_code(filename: str) -> bool:
        try:
            base_dir = settings.QUERYHUNTER_BASE_DIR
        except AttributeError:
            raise ValueError(
                "QUERYHUNTER_BASE_DIR not set in settings. "
                "Define manually or use the built in queryhunter.base_dir function",
            )
        return filename.startswith(base_dir)

    @staticmethod
    def get_code_from_line(filename: str, lineno: int) -> str:
        return linecache.getline(filename, lineno).strip()


class query_hunter(contextlib.ContextDecorator):
    def __init__(self, **metadata):
        self.metadata = metadata
        self._query_hunter = QueryHunter()
        self._pre_execute_hook = connection.execute_wrapper(self._query_hunter)
        self.query_info = self._query_hunter.query_info

    def __enter__(self):
        self._pre_execute_hook.__enter__()
        return self

    def __exit__(self, *exc):
        for _filename, file_data in self._query_hunter.query_info.items():
            print(file_data)
        self._pre_execute_hook.__exit__(*exc)
