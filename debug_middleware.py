"""
Debug middleware for troubleshooting Dokploy 404 issues
"""
import logging

logger = logging.getLogger(__name__)

class DebugRequestMiddleware:
    """Middleware to log all incoming requests for debugging"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log incoming request details
        logger.info(f"🌐 INCOMING REQUEST:")
        logger.info(f"  - Method: {request.method}")
        logger.info(f"  - Path: {request.path}")
        logger.info(f"  - Full Path: {request.get_full_path()}")
        logger.info(f"  - Host: {request.get_host()}")
        logger.info(f"  - User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')[:100]}")
        logger.info(f"  - Remote IP: {request.META.get('REMOTE_ADDR', 'Unknown')}")
        logger.info(f"  - Headers: {dict(request.headers)}")
        
        # Process request
        response = self.get_response(request)
        
        # Log response
        logger.info(f"📤 RESPONSE:")
        logger.info(f"  - Status Code: {response.status_code}")
        logger.info(f"  - Content Type: {response.get('Content-Type', 'Unknown')}")
        
        return response
