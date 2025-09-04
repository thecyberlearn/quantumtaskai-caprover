# CapRover Monitoring and Logging Optimization

## 1. Enhanced Logging Configuration

### Django Logging (Already Optimized)
Your current logging setup in settings.py is good. Additional optimizations:

```python
# Add to settings.py
LOGGING_LEVEL = config('LOGGING_LEVEL', default='INFO')

# Performance monitoring
PERFORMANCE_MONITORING = {
    'SLOW_QUERY_THRESHOLD': 1.0,  # Log queries slower than 1 second
    'MEMORY_THRESHOLD': 100,       # MB
}
```

## 2. Application Performance Monitoring (APM)

### Option A: Django Debug Toolbar (Development)
Already configured for DEBUG=True environments.

### Option B: Simple Performance Middleware
Add custom middleware for production monitoring:

```python
# In core/middleware.py
class PerformanceMonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import time
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        if duration > 2.0:  # Log slow requests
            logger.warning(f"Slow request: {request.path} took {duration:.2f}s")
        
        response['X-Response-Time'] = f"{duration:.3f}"
        return response
```

## 3. CapRover Native Monitoring

### Enable App Monitoring
1. **CapRover Dashboard** → **Apps** → **quantumtaskai** → **App Configs**
2. **Enable**: "Log Rotation" 
3. **Set**: "Max Log Size" to 100MB
4. **Set**: "Max Files" to 5

### Resource Limits
```yaml
# In captain-definition (advanced)
{
  "schemaVersion": 2,
  "dockerfilePath": "./Dockerfile.captain",
  "containerHttpPort": 80,
  "resources": {
    "memory": "512m",
    "cpu": "0.5"
  }
}
```

## 4. External Monitoring Options

### Option A: Netdata (Lightweight)
1. **One-Click Apps** → Search "Netdata"
2. **Deploy** with default settings
3. **Access**: Monitor system resources in real-time

### Option B: Grafana + Prometheus (Advanced)
1. **Deploy Prometheus** from One-Click Apps
2. **Deploy Grafana** from One-Click Apps
3. **Configure** Django metrics export

## 5. Health Checks and Uptime Monitoring

### Application Health Endpoint
Create a health check endpoint in Django:

```python
# In core/views.py
from django.http import JsonResponse
from django.core.cache import cache
from django.db import connection

def health_check(request):
    """Application health check endpoint"""
    try:
        # Test database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Test Redis
        cache.set('health_check', 'ok', 10)
        cache_status = cache.get('health_check') == 'ok'
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'ok',
            'cache': 'ok' if cache_status else 'error',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)
```

### External Uptime Monitoring
- **UptimeRobot** (Free tier available)
- **Pingdom** 
- **StatusCake**

Monitor: `https://quantumtaskai.captain.your-domain.com/health/`

## 6. Log Analysis

### Centralized Logging (Optional)
1. **Deploy ELK Stack** (Elasticsearch, Logstash, Kibana)
2. **Configure** Django to send logs to Logstash
3. **Analyze** logs in Kibana dashboard

### Simple Log Analysis
```bash
# Monitor application logs
docker logs -f [container-id]

# Search for errors
docker logs [container-id] 2>&1 | grep -i error

# Monitor performance
docker logs [container-id] 2>&1 | grep "Slow request"
```

## 7. Alerts and Notifications

### Webhook Notifications
Set up webhooks for critical alerts:
- **High memory usage**
- **Database connection failures**  
- **Application errors**
- **Long response times**

### Email Notifications
Configure Django to send email alerts for critical issues using your existing email setup.