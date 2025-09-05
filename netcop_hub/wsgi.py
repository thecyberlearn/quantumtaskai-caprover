"""
WSGI config for netcop_hub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import traceback

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netcop_hub.settings')

try:
    application = get_wsgi_application()
    print("Django WSGI application loaded successfully!")
except Exception as e:
    print(f"FATAL ERROR during Django startup: {e}")
    print("Full traceback:")
    traceback.print_exc()
    sys.exit(1)
