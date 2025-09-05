# Debug settings for Dokploy troubleshooting
from netcop_hub.settings import *

# Enable debug mode
DEBUG = True

# Add debug middleware at the top
MIDDLEWARE = ['debug_middleware.DebugRequestMiddleware'] + MIDDLEWARE

# Enhanced logging
LOGGING['loggers']['root']['level'] = 'DEBUG'
LOGGING['handlers']['console']['level'] = 'DEBUG'

# Print all URLs at startup
print("🔗 Available URL patterns:")
try:
    from django.urls import get_resolver
    resolver = get_resolver()
    url_patterns = []
    
    def extract_patterns(patterns, prefix=''):
        for pattern in patterns:
            if hasattr(pattern, 'url_patterns'):
                extract_patterns(pattern.url_patterns, prefix + str(pattern.pattern))
            else:
                url_patterns.append(prefix + str(pattern.pattern))
    
    extract_patterns(resolver.url_patterns)
    for pattern in url_patterns[:20]:  # Show first 20
        print(f"  - {pattern}")
except Exception as e:
    print(f"  - Error loading URL patterns: {e}")
