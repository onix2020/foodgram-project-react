import os

from decouple import Csv, config

#from pathlib import Path


# Eсли true то будет использована прилагаемая база SQLite c записанными данными
REVIEW = False

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = True

#BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = ['.localhost', '127.0.0.1', '[::1],', '84.201.177.196', 'backend']
#ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

CSRF_TRUSTED_ORIGINS = ['http://backend','http://localhost', 'http://127.0.0.1', '84.201.177.196']
#CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', default='*')

ROOT_URLCONF = 'foodgram.urls'

WSGI_APPLICATION = 'foodgram.wsgi.application'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_filters',
    'django_extensions',
    'api.apps.ApiConfig',
    'recipes.apps.RecipesConfig',
    'users.apps.UsersConfig',
    
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

DATABASES = {
    'default': {
        'ENGINE': os.getenv(
            'DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': os.getenv(
            'DB_NAME', default='postgres'),
        'USER': os.getenv(
            'POSTGRES_USER', default='postgres'),
        'PASSWORD': os.getenv(
            'POSTGRES_PASSWORD', default='postgres'),
        'HOST': os.getenv(
            'DB_HOST', default='db'),
        'PORT': os.getenv(
            'DB_PORT', default='5432'),
    }
}

AUTH_USER_MODEL = 'users.MyUser'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME':
     'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME':
     'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME':
     'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME':
     'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES':
    ['rest_framework.authentication.TokenAuthentication', ],

    'DEFAULT_PERMISSION_CLASSES':
    ['rest_framework.permissions.IsAuthenticatedOrReadOnly', ],
}

DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'resipe': ('api.permissions.AuthorStaffOrReadOnly,',),
        'recipe_list': ('api.permissions.AuthorStaffOrReadOnly',),
        #check it
        'user': ('api.permissions.OwnerUserOrReadOnly',),
        'user_list': ('api.permissions.OwnerUserOrReadOnly',),
    },
    'SERIALIZERS': {
        'user': 'api.serializers.UserSerializer',
        'user_list': 'api.serializers.UserSerializer',
        'current_user': 'api.serializers.UserSerializer',
        'user_create': 'api.serializers.UserSerializer',
    },
}

LANGUAGE_CODE = 'ru'
#TIME_ZONE = os.getenv('TIME_ZONE')
USE_I18N = True
USE_TZ = True
TIME_ZONE = 'UTC'

STATIC_URL = 'static/'
# STATIC_ROOT = BASE_DIR / STATIC_URL
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = 'media/'
# MEDIA_ROOT = BASE_DIR / MEDIA_URL
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PASSWORD_RESET_TIMEOUT = 60 * 60

# for review
if REVIEW:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'db.sqlite3'),
        }
    }
