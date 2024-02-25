from pathlib import Path

import queryhunter
from queryhunter.reporting import LoggingOptions

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'queryhunter',
    # Install the tests as an app so that we can make test models
    'queryhunter.tests',
]


# settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

ROOT_URLCONF = 'queryhunter.tests.urls'
SECRET_KEY = '1234'


MIDDLEWARE = ['queryhunter.middleware.QueryHunterMiddleware',]

QUERYHUNTER_BASE_DIR = queryhunter.default_base_dir(__file__)
# QUERYHUNTER_REPORTING_OPTIONS = LoggingOptions(logger_name='queryhunter', sort_by='-count', count_threshold=5)
#
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'standard': {
#             'format': '%(asctime)s - %(message)s'
#         },
#     },
#     'handlers': {
#         'queryhunter_file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': QUERYHUNTER_BASE_DIR + '/django-queryhunter/queryhunter.log',
#             'formatter': 'standard',
#         },
#     },
#     'loggers': {
#         QUERYHUNTER_REPORTING_OPTIONS.logger_name: {
#             'handlers': ['queryhunter_file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }
