# Production HTTPS settings for Dokploy deployment
from netcop_hub.settings import *

# Force HTTPS in production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Additional security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Trust Dokploy/Traefik proxy headers
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# CSRF trusted origins for HTTPS
CSRF_TRUSTED_ORIGINS = [
    'https://website-quantumtaskai-wrczik-cc50ac-31-97-62-205.traefik.me',
    'http://website-quantumtaskai-wrczik-cc50ac-31-97-62-205.traefik.me',  # For testing
    'https://localhost:3000',
    'http://localhost:3000',
]

print("🔒 HTTPS Production Settings Loaded")
print(f"   - SSL Redirect: {SECURE_SSL_REDIRECT}")
print(f"   - HSTS: {SECURE_HSTS_SECONDS} seconds")
print(f"   - Trusted Origins: {len(CSRF_TRUSTED_ORIGINS)} configured")
