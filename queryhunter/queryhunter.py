from __future__ import annotations

import linecache
import os
import time
import traceback
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from django.conf import settings

if TYPE_CHECKING:
    from queryhunter import QueryHunterReportingOptions

"""
TODO Functionality for MVP:
- Middleware
- Ability to pass in custom context meta data. Middleware should pass in URL and username by default.
- Ability to somehow highlight rows with high duration or count. Maybe just print in red?
"""


@dataclass
class Line:
    line_no: int
    code: str
    sql: str
    count: int
    duration: float
    meta_data: Optional[dict[str, str]] = None

    def __str__(self):
        string = (
            f'Line no: {self.line_no} | Code: {self.code} | '
            f'Num. Queries: {self.count} | SQL: {self.sql} | Duration: {self.duration}'
        )
        if self.meta_data:
            for key, value in self.meta_data.items():
                string += f' | {key}: {value}'
        return string


@dataclass
class Module:
    name: str
    lines: list[Line]

    def __str__(self):
        data = ''
        for line_data in self.lines:
            data += f'Module: {self.name} | {line_data} \n'
        data.rstrip('\n')
        return data


class QueryHunter:
    def __init__(self, reporting_options: QueryHunterReportingOptions, meta_data: dict[str, str] = None):
        self.reporting_options = reporting_options
        self.query_info: dict[str, Module] = {}
        self.meta_data = meta_data

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

            if self.reporting_options.modules is not None:
                if relative_path not in self.reporting_options.modules:
                    return execute(sql, params, many, context)

            module = self.query_info.get(relative_path, Module(relative_path, lines=[]))
            line_no = app_frame.lineno
            code = self.get_code_from_line(filename, line_no)
            start = time.monotonic()
            result = execute(sql, params, many, context)
            duration = time.monotonic() - start

            if (max_length := self.reporting_options.max_sql_length) is not None:
                reportable_sql = sql[:max_length]
            else:
                reportable_sql = sql

            try:
                line = next(line for line in module.lines if line.line_no == line_no)
            except StopIteration:
                line = Line(
                    line_no=line_no,
                    code=code,
                    sql=reportable_sql,
                    count=1,
                    duration=duration,
                    meta_data=self.meta_data,
                )
                module.lines.append(line)
            else:
                line.count += 1
                line.duration += duration

            reverse = self.reporting_options.sort_by.startswith('-')
            sort_by = self.reporting_options.sort_by[1:] if reverse else self.reporting_options.sort_by
            module.lines = sorted(module.lines, key=lambda x: getattr(x, sort_by), reverse=reverse)

            self.query_info[relative_path] = module
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
