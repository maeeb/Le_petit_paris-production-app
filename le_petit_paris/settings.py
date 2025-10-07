import os
from pathlib import Path
import dj_database_url

# -----------------------
# BASE
# -----------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------
# SECURITY
# -----------------------
SECRET_KEY = os.environ.get('SECRET_KEY', 'votre-cle-secrete-dev')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',          # pour Render
    'le-petit-paris.onrender.com',  # futur domaine
]

# -----------------------
# APPS
# -----------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'production',  # ton app principale
]

# -----------------------
# MIDDLEWARE
# -----------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'production.middleware.ShiftAccessMiddleware',
]

# -----------------------
# URLS & TEMPLATES
# -----------------------
ROOT_URLCONF = 'le_petit_paris.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # ajouter si tu as des templates global
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

WSGI_APPLICATION = 'le_petit_paris.wsgi.application'

# -----------------------
# DATABASES
# -----------------------
if os.environ.get('DATABASE_URL'):
    # Production / Render
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # Développement local
    DATABASES = {
        'default': {
            # Tu peux basculer entre SQLite ou PostgreSQL local
            # SQLite local simple
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',

            # Pour PostgreSQL local, décommente et remplis USER/PASSWORD
            # 'ENGINE': 'django.db.backends.postgresql',
            # 'NAME': 'le_petit_paris_db',
            # 'USER': 'votre_user',
            # 'PASSWORD': 'votre_password',
            # 'HOST': 'localhost',
            # 'PORT': '5432',
        }
    }

# -----------------------
# PASSWORD VALIDATION
# -----------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# -----------------------
# INTERNATIONALIZATION
# -----------------------
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Tunis'
USE_I18N = True
USE_TZ = True

# -----------------------
# STATIC & MEDIA FILES
# -----------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -----------------------
# AUTH REDIRECTS
# -----------------------
LOGIN_URL = '/production/login/'
LOGIN_REDIRECT_URL = '/production/dashboard/'
LOGOUT_REDIRECT_URL = '/production/login/'

# -----------------------
# AUTO FIELD
# -----------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
