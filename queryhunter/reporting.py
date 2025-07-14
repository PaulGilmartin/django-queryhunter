from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from queryhunter.queryhunter import QueryHunter

SORT_BY_OPTIONS = ['line_no', '-line_no', 'count', '-count', 'duration', '-duration']


@dataclass
class ReportingOptions:
    sort_by: str = 'line_no'
    modules: Optional[list[str]] = None
    max_sql_length: Optional[int] = None
    count_threshold: int = 1
    duration_threshold: float = 0.0

    def __post_init__(self):
        if self.sort_by not in SORT_BY_OPTIONS:
            raise ValueError(f'sort_by must be one of {SORT_BY_OPTIONS}')


@dataclass
class PrintingOptions(ReportingOptions):
    count_highlighting_threshold: int = 5
    duration_highlighting_threshold: float = 0.5


@dataclass
class LoggingOptions(ReportingOptions):
    logger_name: str = 'queryhunter'


@dataclass
class RaisingOptions(ReportingOptions):
    count_highlighting_threshold: int = 5
    duration_highlighting_threshold: float = 0.5


class QueryHunterException(Exception):
    pass


class QueryHunterReporter:
    def __init__(self, query_hunter: QueryHunter):
        self.query_hunter = query_hunter
        self.query_info = query_hunter.query_info
        self.options = query_hunter.reporting_options

    @classmethod
    def create(
        cls, queryhunter: QueryHunter
    ) -> PrintingQueryHunterReporter | LoggingQueryHunterReporter | RaisingQueryHunterReporter:
        reporting_options = queryhunter.reporting_options
        if isinstance(reporting_options, PrintingOptions):
            return PrintingQueryHunterReporter(queryhunter)
        elif isinstance(reporting_options, LoggingOptions):
            return LoggingQueryHunterReporter(queryhunter)
        elif isinstance(reporting_options, RaisingOptions):
            return RaisingQueryHunterReporter(queryhunter)


class PrintingQueryHunterReporter(QueryHunterReporter):
    def report(self):
        RED = "\033[31m"
        GREEN = "\033[32m"
        BOLD = "\033[1m"
        for name, module in self.query_info.items():
            print(f'{BOLD}{name}')
            print('=' * 2 * len(name))
            for line in module.lines:
                if line.duration < self.options.duration_threshold or line.count < self.options.count_threshold:
                    continue
                if line.duration >= self.options.duration_highlighting_threshold:
                    print(f'   {RED}{line}')
                elif line.count >= self.options.count_highlighting_threshold:
                    print(f'   {RED}{line}')
                else:
                    print(f'   {GREEN}{line}')
            print('\n')


class LoggingQueryHunterReporter(QueryHunterReporter):
    def report(self):
        logger_name = self.options.logger_name
        logger = logging.getLogger(logger_name)
        for _name, module in self.query_info.items():
            for line in module.lines:
                if line.duration < self.options.duration_threshold or line.count < self.options.count_threshold:
                    continue
                logger.info(f'Module: {module.name} | {line}')


class RaisingQueryHunterReporter(QueryHunterReporter):
    def report(self):
        for name, module in self.query_info.items():
            for line in module.lines:
                if line.duration < self.options.duration_threshold or line.count < self.options.count_threshold:
                    continue
                if line.duration >= self.options.duration_highlighting_threshold:
                    raise QueryHunterException(f'Excessive time spent in module: {name} | {line}')
                elif line.count >= self.options.count_highlighting_threshold:
                    raise QueryHunterException(f'Excessive repeated queries in module: {name} | {line}')
