
from regapp.config.env import ENV, PROJECT_ROOT

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = PROJECT_ROOT()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV.str('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV.bool('DEBUG', default=False)

ALLOWED_HOSTS = ENV.list('ALLOWED_HOSTS', default=['*'])


# ------------------------------------------------------------------------------
# Django Apps
# ------------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Additional third-party
INSTALLED_APPS += [
    'crispy_forms'
]

# NERC REGAPP Apps
INSTALLED_APPS += [
    'regapp.apps.regapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'regapp.apps.regapp.oidcinfo_mw.OIDCMiddleware',
]

ROOT_URLCONF = 'regapp.config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [PROJECT_ROOT("jinja2")],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'regapp.config.jinja2env.environment',
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]

WSGI_APPLICATION = 'regapp.config.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
LANGUAGE_CODE = ENV.str('LANGUAGE_CODE', default='en-us')
TIME_ZONE = ENV.str('TIME_ZONE', default='America/New_York')
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_URL = ENV.str('STATIC_URL', '/static/')
STATIC_ROOT = ENV.str('STATIC_ROOT', default=PROJECT_ROOT('/static/'))

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = ENV.str("REGAPP_EMAIL_HOST")
EMAIL_USE_TLS = ENV.bool('REGAPP_EMAIL_USE_TLS')
EMAIL_PORT = ENV.int("REGAPP_EMAIL_PORT")
EMAIL_HOST_USER = ENV.str("REGAPP_EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = ENV.str("REGAPP_EMAIL_HOST_PASSWORD")

REGAPP_REAPER_MAX_AGE = ENV.int('REGAPP_REAPER_MAX_AGE', 86400)
