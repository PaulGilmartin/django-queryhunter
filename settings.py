from pathlib import Path

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


QUERYHUNTER_BASE_DIR = str(Path(__file__).resolve().parent.parent)
