"""
Production settings for netcop_hub project.
"""

from .settings import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Parse ALLOWED_HOSTS from environment
allowed_hosts_str = os.environ.get('ALLOWED_HOSTS', '')
if allowed_hosts_str and allowed_hosts_str != '*':
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',') if host.strip()]
elif allowed_hosts_str == '*':
    ALLOWED_HOSTS = ['*']
else:
    # Default fallback
    domain = os.environ.get('DOMAIN', 'localhost')
    ALLOWED_HOSTS = [domain, 'localhost', '127.0.0.1']

print(f"🌐 ALLOWED_HOSTS configured: {ALLOWED_HOSTS}")

# Database - use PostgreSQL if DATABASE_URL is provided, otherwise SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Parse DATABASE_URL for PostgreSQL
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Use SQLite for simple deployments
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Security settings - respect environment variables for Dokploy compatibility
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'true').lower() == 'true'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Only enable secure cookies and HSTS if SSL redirect is enabled
if SECURE_SSL_REDIRECT:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Trust proxy headers for Dokploy/Traefik
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# CSRF trusted origins from environment
csrf_origins_str = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins_str:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins_str.split(',') if origin.strip()]
else:
    # Default CSRF origins based on domain
    domain = os.environ.get('DOMAIN', 'localhost')
    CSRF_TRUSTED_ORIGINS = [
        f'https://{domain}',
        f'http://{domain}',
        'https://localhost',
        'http://localhost'
    ]

print(f"🔒 CSRF_TRUSTED_ORIGINS configured: {CSRF_TRUSTED_ORIGINS}")
print(f"🔒 SSL Redirect enabled: {SECURE_SSL_REDIRECT}")
print(f"📊 Database: {'PostgreSQL' if DATABASE_URL else 'SQLite'}")

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/netcop_hub.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}