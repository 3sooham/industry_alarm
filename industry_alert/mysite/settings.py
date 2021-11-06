"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# env = environ.Env()
# environ.Env.read_env(os.path.join(BASE_DIR, 'mysite', '.env'))

# load .env
# load_dotenv(os.path.join(BASE_DIR, 'mysite', '.env'))
load_dotenv()

# celery
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#ALLOWED_HOSTS = ['127.0.0.1', '.pythonanywhere.com', '3.34.122.127']
ALLOWED_HOSTS = ['*']

# 파일들
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog', # blog 사용한다고 알려줘야함
    'account',
    # drf login
    "rest_framework",
    "rest_framework.authtoken",
	# drf-spectacular
	'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
# sqlite3
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# mysql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('INDUSTRY_ALERT_DB_NAME'),
        'USER': os.getenv('INDUSTRY_ALERT_DB_USER'),
        'PASSWORD': os.getenv('INDUSTRY_ALERT_DB_PASSWORD'),
        'HOST': os.getenv('INDUSTRY_ALERT_DB_HOST'),
        'PORT': os.getenv('INDUSTRY_ALERT_DB_PORT'),
    }
}
print(DATABASES)


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# LoginView에서 
#   def get_default_redirect_url(self):
#        """Return the default redirect URL."""
#        return resolve_url(self.next_page or settings.LOGIN_REDIRECT_URL)

LOGIN_REDIRECT_URL = '/'

# LOGOUT_REDIRECT_URL = '/'

# drf login
# defines the default authentication class to be Token Authentication
# Default permission class to be IsAuthenticated
# ->meaning no API can be accessed by an unauthenticated user unless either he has a token or the permission class for that API has been defined to be AllowAny.
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
	# drf-spectacular
	'DEFAULT_SCHEMA_CLASS' : 'drf_spectacular.openapi.AutoSchema',
}

# drf-spectacular
SPECTACULAR_SETTINGS = {
	'TITLE': 'Job Finished API',
	'DESCRIPTION': 'personal toy project',
	'VERSION': '0.1.2',
}

# drf
# Django allows you to override the default user model by providing a value for the AUTH_USER_MODEL setting that references a custom model:
# 앱이름.모델이름
# 모델 바꾸면 makemigrations 해야함 migrate랑
# 내가 설정한 User를 사용하겠다임
# class User보면
# swappable = 'AUTH_USER_MODEL'있는데 이거에 의해 바뀔수있다는 거임
# shell에서 
# from django.contrib.auth import get_user_model
# get_user_model() 하면 내가 정의한 Users로 User모델이 바뀐게 보일거임
# https://han-py.tistory.com/353
AUTH_USER_MODEL='account.User'
