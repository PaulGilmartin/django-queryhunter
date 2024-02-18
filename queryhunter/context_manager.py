import contextlib

from django.conf import settings
from django.db import connection

from .queryhunter import QueryHunter
from queryhunter.reporting import ReportingOptions, QueryHunterReporter, PrintingOptions


class queryhunter(contextlib.ContextDecorator):
    def __init__(self, reporting_options: ReportingOptions = None, meta_data: dict[str, str] = None):
        if not hasattr(settings, 'QUERYHUNTER_BASE_DIR'):
            raise ValueError('QUERYHUNTER_BASE_DIR setting is required')

        self.meta_data = meta_data

        if reporting_options is None:
            try:
                self._reporting_options = settings.QUERYHUNTER_REPORTING_OPTIONS
            except AttributeError:
                self._reporting_options = PrintingOptions()
        else:
            self._reporting_options = reporting_options

        self._query_hunter = QueryHunter(reporting_options=self._reporting_options, meta_data=self.meta_data)
        self.query_info = self._query_hunter.query_info
        self.reporter = QueryHunterReporter.create(queryhunter=self._query_hunter)
        self._pre_execute_hook = connection.execute_wrapper(self._query_hunter)

    def __enter__(self):
        self._pre_execute_hook.__enter__()
        return self

    def __exit__(self, *exc):
        self.reporter.report()
        self._pre_execute_hook.__exit__(*exc)
