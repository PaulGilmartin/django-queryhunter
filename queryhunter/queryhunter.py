import contextlib
import linecache
import os
import time
import traceback
from collections import defaultdict
from pprint import pprint

from django.conf import settings
from django.db import connection


class QueryHunter:
    def __init__(self):
        self.file_query_info = defaultdict(dict)

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
            lineno = app_frame.lineno
            code = self.get_code_from_line(filename, lineno)
            start = time.monotonic()
            result = execute(sql, params, many, context)
            duration = time.monotonic() - start

            current_line_data = self.file_query_info.get(filename, {}).get(lineno, {})

            current_count = current_line_data.get("count", 0)
            updated_count = current_count + 1

            current_sql = current_line_data.get("sql", set())
            updated_sql = current_sql | {sql}

            current_duration = current_line_data.get("duration", 0)
            updated_duration = current_duration + duration

            relative_path = os.path.relpath(
                app_frame.filename, settings.QUERYHUNTER_BASE_DIR)

            self.file_query_info[relative_path][lineno] = {
                "code": code,
                "sql": updated_sql,
                "count": updated_count,
                "duration": updated_duration,
            }
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

    def __enter__(self):
        return self._pre_execute_hook.__enter__()

    def __exit__(self, *exc):
        pprint(self._query_hunter.file_query_info)
        self._pre_execute_hook.__exit__(*exc)
