from pathlib import Path
import os
from decouple import config
import dj_database_url
from django.contrib.messages import constants as messages

# ============================================================
# BASE
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔑 Clé secrète
SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-default-key-for-local"
)

# ⚙️ Mode DEBUG
DEBUG = config("DEBUG", default=True, cast=bool)

# 🌐 Hôtes autorisés
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,.loca.lt",
    cast=lambda v: [s.strip() for s in v.split(",")]
)

# Ajouter automatiquement le host fourni par Render
render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME") or os.environ.get("RENDER_EXTERNAL_URL")
if render_host:
    render_host = render_host.replace("https://", "").replace("http://", "").split("/")[0]
    if render_host and render_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(render_host)

# 🔒 CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    "https://*.loca.lt",
]

# ============================================================
# APPLICATIONS
# ============================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'eglise.apps.EgliseConfig',
    'channels',
    'django_extensions',
]

# ============================================================
# MIDDLEWARE
# ============================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # pour static files sur Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================================
# URLS, WSGI & ASGI
# ============================================================
ROOT_URLCONF = 'ModApp.urls'
WSGI_APPLICATION = 'ModApp.wsgi.application'
ASGI_APPLICATION = 'ModApp.asgi.application'

# ============================================================
# TEMPLATES
# ============================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'eglise' / 'templates',
        ],
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

# ============================================================
# BASE DE DONNÉES
# ============================================================
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

# ============================================================
# MOT DE PASSE
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================
# INTERNATIONALISATION
# ============================================================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Kinshasa'
USE_I18N = True
USE_TZ = True

# ============================================================
# STATIC & MEDIA
# ============================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "eglise" / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

if DEBUG:
    print("⚠️ DEBUG actif — fichiers media servis en local")

# ============================================================
# AUTH
# ============================================================
AUTH_USER_MODEL = 'eglise.CustomUser'
LOGIN_URL = 'eglise:connexion'
LOGIN_REDIRECT_URL = 'eglise:accueil'
LOGOUT_REDIRECT_URL = '/'

# ============================================================
# MESSAGES
# ============================================================
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}

# ============================================================
# CHANNELS
# ============================================================
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
}

# ============================================================
# HTTPS & CORS
# ============================================================
SECURE_SSL_REDIRECT = False  # Render et PythonAnywhere gèrent SSL
CORS_ALLOW_ALL_ORIGINS = True

# ✅ Pour tunnels HTTPS (LocalTunnel)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# ============================================================
# ORANGE MONEY / ADS / AUTRES VARIABLES
# ============================================================
ORANGE_MONEY_RECEIVER = config("ORANGE_MONEY_RECEIVER", default="")
ORANGE_MONEY_MIN_MONTANT = config("ORANGE_MONEY_MIN_MONTANT", cast=int, default=0)
ORANGE_MONEY_API_KEY = config("ORANGE_MONEY_API_KEY", default="")

ADSENSE_CLIENT_ID = config("ADSENSE_CLIENT_ID", default="")
ADMOB_APP_ID = config("ADMOB_APP_ID", default="")
META_AUDIENCE_PLACEMENT_ID = config("META_AUDIENCE_PLACEMENT_ID", default="")

# ============================================================
# AUTO FIELD
# ============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
