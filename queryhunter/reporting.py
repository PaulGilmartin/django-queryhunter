import logging
from dataclasses import dataclass
from typing import Optional

from queryhunter.queryhunter import QueryHunter


SORT_BY_OPTIONS = ['line_no', '-line_no', 'count', '-count', 'duration', '-duration']
REPORT_TYPE_OPTIONS = ['print', 'log', 'html']


@dataclass
class QueryHunterReportingOptions:
    report_type: str = 'print'
    sort_by: str = 'line_no'
    modules: Optional[list[str]] = None
    max_sql_length: Optional[int] = None

    def __post_init__(self):
        if self.sort_by not in SORT_BY_OPTIONS:
            raise ValueError(f'sort_by must be one of {SORT_BY_OPTIONS}')
        if self.report_type not in REPORT_TYPE_OPTIONS:
            raise ValueError('report_type must be one of "print", "log", "html"')


@dataclass
class QueryHunterPrintingOptions(QueryHunterReportingOptions):
    report_type: str = 'print'


@dataclass
class QueryHunterLoggingOptions(QueryHunterReportingOptions):
    report_type: str = 'log'
    log_file: Optional[str] = None

    def __post_init__(self):
        if self.log_file is None:
            self.log_file = 'queryhunter.log'


class QueryHunterHTMLOptions(QueryHunterReportingOptions):
    report_type: str = 'html'
    count_highlighting_threshold: Optional[int] = 5
    duration_highlighting_threshold: Optional[float] = 0.5


class QueryHunterReporter:
    def __init__(self, query_hunter: QueryHunter):
        self.query_hunter = query_hunter
        self.query_info = query_hunter.query_info
        self.options = query_hunter.reporting_options

    def report(self):
        if self.options.report_type == 'print':
            self.print_report()
        elif self.options.report_type == 'log':
            self.log_report()
        elif self.options.report_type == 'html':
            self.html_report()
        else:
            raise ValueError(f'Invalid report_type: {self.options.report_type}')

    def print_report(self):
        for name, module in self.query_info.items():
            print(name)
            print('=' * 2 * len(name))
            for line in module.lines:
                print(f'   {line}')

    def log_report(self):
        logging.basicConfig(filename=self.options.log_file, level=logging.DEBUG, format='%(message)s')
        logger = logging.getLogger()
        for name, module in self.query_info.items():
            logger.debug(module)

    def html_report(self):
        raise NotImplementedError('html_report is not yet implemented')
