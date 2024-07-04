"""
Django settings for edutech_payment_engine project.

Generated by 'django-admin startproject' using Django 3.2.10.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path
import dj_database_url
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = 'media/'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587

# Username and password for authentication
EMAIL_HOST_USER = 'edu2024tech@gmail.com'
EMAIL_HOST_PASSWORD = 'xglu fvkr zfzi wqyy'

# Additional properties for SMTP
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False  # If you use TLS, SSL should be False

# Debug email sending in Django (similar to logging level in Spring Boot)
import logging

logger = logging.getLogger('django')
logger.setLevel(logging.DEBUG)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-b5prd^t6_@jdhb=n9d0yo4=!sy9_5qs@3!%%nu@tc((bv)5%!b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
inProd = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    "http://localhost:8000",
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:4200',
]

# Application definition


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'rest_framework',
    'rest_framework_jwt',
    'corsheaders',
    'drf_yasg',
    'usergroup',
    'account',
    'users',
    'students',
    'studentsschools',
    'parents',
    'studentsparents',
    'authuser',
    'paymentgroups',
    'paymentmodes',
    'feecategories',
    'feepayments',
    'feeextensions',
    'expensetypes',
    'expenses',
    'expensepayment',
    'suppliers',
    'supplierspayment',
    'fee',
    'feecollections',
    # 'notifications',
    'uniqueids',
    'schools',
    # 'virtualaccounts',
    'payfee',
    'inquiries'

]

# JWT_AUTH = {
#     'JWT_SECRET_KEY': '!q6r5u+&cfrpik7ipmfgw)k*4vrm@yiah1yr8%kb)yk1qti7e-',
#     'JWT_EXPIRATION_DELTA': timedelta(days=1),
#     'JWT_ALLOW_REFRESH': True,
#     'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
# }


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'edutech_payment_engine.urls'

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

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # # or allow read-only access for unauthenticated users.
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    # ],
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10

}
WSGI_APPLICATION = 'edutech_payment_engine.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


if inProd:
    DATABASES = {
        'default': dj_database_url.config(
            # Replace this value with your local database's connection string.
            default='postgres://edutech_s1pi_user:RPaUbLjei1XXW6gI4EQS1ZzaKLYGRunU@dpg-cnio1q7jbltc73c6k4d0-a.oregon-postgres.render.com/edutech_s1pi',
            conn_max_age=600
        )

    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'edutech_payments_db',
            'USER': 'root',
            'PASSWORD': "",
            'HOST': '127.0.0.1',
            'PORT': '3306',
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
if not DEBUG:
    # Tell Django to copy static assets into a path called staticfiles (this is specific to Render)
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    # Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
    # and renames the files with unique names for each version to support long-term caching
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CONSUMER_KEY = "nk16Y74eSbTaGQgc9WF8j6FigApqOMWr"
CONSUMER_SECRET = "40fD1vRXCq90XFaU"
BSS_SHORT_CODE = "174379"
PASS_KEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
ACCESS_TOKEN_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
INITIATE_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
CALL_BACK_URL = "https://3db4-102-210-244-74.ngrok-free.app /MpesaCallBackURL.php"

# Jenga API credentials
api_key = 'WAH5yH10p0J9V3q+r8sDmZBFG7y/P28/CBzMRFL7eAsRYoKh8OA/o0jqbyp/cRonjWITTBTlFcsPl7HTTqpb0w=='
api_secret = 'LU48y4cm8VX5aReR3eNlL5O6cb7En1'

JENGA_CLIENT_ID = '7738920625'
JENGA_CLIENT_SECRET = 'LU48y4cm8VX5aReR3eNlL5O6cb7En1'
JENGA_BANK_TO_BANK_URL = 'https://uat.finserve.africa/v3-apis/transaction-api/v3.0/remittance/pesalinkacc'
JENGA_BANK_TO_MOBILE_URL = 'https://api.finserve.africa/v3-apis/transaction-api/v3.0/remittance/pesalinkMobile'
# Signature Formulae
# transfer.amount+transfer.currencyCode+transfer.reference+destination.name+source.accountNumber

