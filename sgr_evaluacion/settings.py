"""
Django settings for sgr_evaluacion project — Evaluación Sumativa 2.

Cambios respecto a la Evaluación 1:
- Se agregan django.contrib.admin / auth / sessions / messages / contenttypes
  (necesarios para Django Admin y CRUD con base de datos).
- La configuración sensible (SECRET_KEY, DEBUG, ALLOWED_HOSTS, credenciales
  de base de datos) ya NO está escrita en este archivo: se carga desde un
  archivo .env mediante python-decouple (requisito de "Variables de Entorno").

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/
"""

from pathlib import Path

from decouple import Csv, config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Seguridad / variables de entorno
# ---------------------------------------------------------------------------
# Todas estas variables se definen en un archivo .env (no versionado, ver
# .gitignore) a partir de la plantilla .env.example incluida en el proyecto.

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cuentas',
    'delegaciones',
    'gestion',
    'cargos',
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

ROOT_URLCONF = 'sgr_evaluacion.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sgr_evaluacion.wsgi.application'


# ---------------------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------------------
# Requisito de la Evaluación 2: persistencia en base de datos relacional
# (MySQL en la instancia EC2, administrable desde phpMyAdmin).
#
# DB_ENGINE controla el motor y se define en el .env:
#   - "mysql"  -> producción / EC2 (MySQL + phpMyAdmin). Requiere las
#                 variables DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT.
#   - "sqlite" -> desarrollo local rápido, sin instalar MySQL (por defecto).
#
# PyMySQL se usa como driver puro-Python de MySQL (se registra como
# reemplazo de mysqlclient en sgr_evaluacion/__init__.py), porque es más
# simple de instalar en Windows/EC2 que compilar mysqlclient.

DB_ENGINE = config('DB_ENGINE', default='sqlite')

if DB_ENGINE == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ---------------------------------------------------------------------------
# Autenticación y sesiones (Evaluación 3)
# ---------------------------------------------------------------------------
LOGIN_URL = 'cuentas:login'
LOGIN_REDIRECT_URL = 'cuentas:panel'
LOGOUT_REDIRECT_URL = 'cuentas:login'

# Vigencia del enlace de recuperación de contraseña, en segundos (1 hora).
PASSWORD_RESET_TIMEOUT = 3600


# ---------------------------------------------------------------------------
# Correo electrónico (recuperación de contraseña - Evaluación 3)
# ---------------------------------------------------------------------------
# Se usa una cuenta de Gmail con "contraseña de aplicación" como remitente
# (ver .env.example para la guía de cómo generarla). Todas las credenciales
# se leen desde el .env, igual que las de la base de datos.
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Archivos subidos por los usuarios (fotos de "Mi perfil").
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
