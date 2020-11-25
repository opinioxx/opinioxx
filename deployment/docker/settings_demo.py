"""
Django demo settings for opinioxx project.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'kcc8fir5s54deu8qnl)-5-^*kz1kna43)8lk3(u_4pf5k#4mq0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# add hosts in your setup
ALLOWED_HOSTS = ['demo.opinioxx.de', '127.0.0.1']

# url for the installation
BASE_URL = 'https://demo.opinioxx.de'

# Application definition
INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'opinioxx.base.apps.OpinioxxBaseConfig',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'opinioxx.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'opinioxx.base.context_processors.common_variables'
            ],
        },
    },
]
WSGI_APPLICATION = 'opinioxx.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
LANGUAGE_CODE = 'de'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = '/static/'

# Authentication
AUTH_USER_MODEL = 'base.User'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login'

# email settings
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
EMAIL_HOST = 'example.com'
EMAIL_PORT = '25'
EMAIL_HOST_USER = 'noreply@example.com'
EMAIL_HOST_PASSWORD = '1234password'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'noreply@example.com'
SERVER_EMAIL = 'noreply@example.com'

# version
version_file = 'version.txt'
if os.path.isfile(version_file):
    with open(version_file) as file:
        VERSION_NUMBER = file.read()
else:
    VERSION_NUMBER = '-debug'

# session
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 129600  # 36h in seconds
SESSION_COOKIE_SECURE = not DEBUG

# General settings
TITLE = 'Opinioxx'  # title shown on the website and used
ALLOW_NEW_PROJECTS = True  # is every registered user able to create new projects or only the site-administrator?
ALLOW_USER_REGISTRATION = False  # is the registration public or can only the site-administrator create new users?
