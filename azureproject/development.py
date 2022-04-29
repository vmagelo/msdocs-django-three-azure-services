import os
from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

STATICFILES_DIRS = (str(BASE_DIR.joinpath('static')),)
STATIC_URL = 'static/'

# Configure Postgres database for local development
#   Set these environment variables in the .env file for this project.  
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DBNAME'],
        'HOST': os.environ['DBHOST'],
        'USER': os.environ['DBUSER'],
        'PASSWORD': 'set with get_token()'
    }
}
get_token()
