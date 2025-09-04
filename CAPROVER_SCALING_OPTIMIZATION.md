# CapRover Auto-scaling and Resource Optimization

## 1. Container Resource Limits

### Update captain-definition for Resource Management
```json
{
  "schemaVersion": 2,
  "dockerfilePath": "./Dockerfile.captain",
  "containerHttpPort": 80,
  "resources": {
    "memory": "512m",
    "memoryReservation": "256m",
    "cpu": 0.5,
    "cpuReservation": 0.25
  },
  "healthcheck": {
    "test": ["CMD", "python", "manage.py", "check"],
    "interval": "30s",
    "timeout": "10s",
    "retries": 3,
    "startPeriod": "40s"
  }
}
```

### CapRover App Configuration
1. **CapRover Dashboard** → **Apps** → **quantumtaskai** → **App Configs**
2. **Resources** section:
   - **Memory Limit**: 512MB
   - **Memory Reservation**: 256MB
   - **CPU Limit**: 0.5 (50% of one CPU core)
   - **CPU Reservation**: 0.25 (25% guaranteed)

## 2. Horizontal Scaling (Multiple Instances)

### Load Balancing Setup
1. **App Configs** → **Enable** "Load Balancer"
2. **Set** "Instance Count" to 2-3 instances
3. **Configure** "Health Check Path" to `/health/`

### Session Affinity (Important for Django)
Since you're using Redis for sessions, sticky sessions aren't needed:
- **Disable** session affinity
- **Enable** Redis session storage (already configured)
- **Sessions persist** across all instances

### Database Connection Pooling
Update database settings for multiple instances:
```python
# In settings.py
if config('CAPROVER_GIT_COMMIT_SHA', default=''):
    # CapRover environment - optimize for multiple instances
    DATABASES['default']['CONN_MAX_AGE'] = 300  # Shorter connection lifetime
    DATABASES['default']['OPTIONS']['MAX_CONNS'] = 10  # Fewer connections per instance
```

## 3. Vertical Scaling (Resource Monitoring)

### Memory Optimization
```python
# Add to Django settings
if not DEBUG:
    # Production memory optimizations
    MIDDLEWARE = [
        'django.middleware.gzip.GZipMiddleware',  # Compress responses
    ] + MIDDLEWARE
    
    # Enable template caching
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]
```

### Database Query Optimization
```python
# Add to apps/core/middleware.py
class DatabaseOptimizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.db import connection, reset_queries
        
        # Reset queries for this request
        reset_queries()
        
        response = self.get_response(request)
        
        # Log slow or numerous queries in production
        if not settings.DEBUG and len(connection.queries) > 10:
            logger.warning(f"High query count: {len(connection.queries)} queries for {request.path}")
        
        return response
```

## 4. Auto-scaling Triggers

### CPU-based Scaling
```bash
# Monitor CPU usage
docker stats [container-id]

# Scale up when CPU > 70% for 5 minutes
# Scale down when CPU < 30% for 10 minutes
```

### Memory-based Scaling
```bash
# Monitor memory usage  
docker exec [container-id] free -m

# Scale up when memory > 80% for 5 minutes
# Scale down when memory < 40% for 10 minutes
```

### Custom Metrics Scaling
Monitor application-specific metrics:
- **Active user sessions** (Redis keys)
- **Agent execution queue length**
- **Database connection pool usage**
- **Response time averages**

## 5. Performance Monitoring Scripts

### Create Monitoring Script
```bash
#!/bin/bash
# monitoring.sh

CONTAINER_ID=$(docker ps | grep quantumtaskai | awk '{print $1}')

# Get resource usage
CPU_USAGE=$(docker stats --no-stream $CONTAINER_ID | tail -1 | awk '{print $3}' | sed 's/%//')
MEM_USAGE=$(docker stats --no-stream $CONTAINER_ID | tail -1 | awk '{print $4}' | sed 's/%//')

echo "CPU Usage: $CPU_USAGE%"
echo "Memory Usage: $MEM_USAGE%"

# Alert if high usage
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo "HIGH CPU ALERT: $CPU_USAGE%"
    # Send notification (email, webhook, etc.)
fi

if (( $(echo "$MEM_USAGE > 85" | bc -l) )); then
    echo "HIGH MEMORY ALERT: $MEM_USAGE%"
    # Send notification (email, webhook, etc.)
fi

# Check application health
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://quantumtaskai.captain.your-domain.com/health/)
if [ "$HEALTH_CHECK" != "200" ]; then
    echo "APPLICATION HEALTH ALERT: HTTP $HEALTH_CHECK"
    # Send notification
fi
```

### Cron Job for Monitoring
```bash
# Add to crontab
*/5 * * * * /path/to/monitoring.sh >> /var/log/quantum-monitor.log 2>&1
```

## 6. Caching Strategy for Scale

### Multi-layer Caching
```python
# In views.py - example caching strategy
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@method_decorator(cache_page(60 * 5), name='dispatch')  # 5 minutes
class AgentListView(ListView):
    model = Agent
    
    def get_queryset(self):
        cache_key = f"agents_list_{self.request.user.id}"
        queryset = cache.get(cache_key)
        
        if queryset is None:
            queryset = Agent.objects.select_related().prefetch_related('category')
            cache.set(cache_key, queryset, 60 * 10)  # 10 minutes
        
        return queryset
```

### Redis Cluster for High Availability (Advanced)
For very high load, consider Redis Cluster:
1. **Deploy multiple Redis instances**
2. **Configure Redis Cluster**
3. **Update Django Redis settings** for cluster mode

## 7. Load Testing and Optimization

### Load Testing Tools
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test with concurrent users
ab -n 1000 -c 10 https://quantumtaskai.captain.your-domain.com/

# Test specific endpoints
ab -n 500 -c 5 https://quantumtaskai.captain.your-domain.com/agents/

# Load test with POST data
ab -n 100 -c 5 -p post_data.json -T application/json https://quantumtaskai.captain.your-domain.com/agents/api/execute/
```

### Performance Benchmarks
Target performance metrics:
- **Response time**: < 200ms for cached pages
- **Database queries**: < 50ms per query
- **Memory usage**: < 400MB per instance
- **CPU usage**: < 60% average
- **Concurrent users**: 100+ simultaneous users

## 8. Auto-scaling Scripts

### Simple Auto-scaler Script
```bash
#!/bin/bash
# auto-scaler.sh

APP_NAME="quantumtaskai"
MIN_INSTANCES=1
MAX_INSTANCES=5
CPU_THRESHOLD_UP=70
CPU_THRESHOLD_DOWN=30

# Get current instance count
CURRENT_INSTANCES=$(docker ps | grep $APP_NAME | wc -l)

# Get average CPU usage
AVG_CPU=$(docker stats --no-stream $(docker ps -q --filter name=$APP_NAME) | awk 'NR>1 {sum += $3; count++} END {print sum/count}' | sed 's/%//')

echo "Current instances: $CURRENT_INSTANCES"
echo "Average CPU: $AVG_CPU%"

# Scale up logic
if (( $(echo "$AVG_CPU > $CPU_THRESHOLD_UP" | bc -l) )) && [ $CURRENT_INSTANCES -lt $MAX_INSTANCES ]; then
    echo "Scaling UP: CPU at $AVG_CPU%"
    # Implement scaling up logic (CapRover API call)
    curl -X POST https://captain.your-domain.com/api/v2/user/apps/appData/quantumtaskai \
         -H "x-captain-auth: $CAPTAIN_TOKEN" \
         -d '{"instanceCount": '$((CURRENT_INSTANCES + 1))'}'
fi

# Scale down logic  
if (( $(echo "$AVG_CPU < $CPU_THRESHOLD_DOWN" | bc -l) )) && [ $CURRENT_INSTANCES -gt $MIN_INSTANCES ]; then
    echo "Scaling DOWN: CPU at $AVG_CPU%"
    # Implement scaling down logic (CapRover API call)
    curl -X POST https://captain.your-domain.com/api/v2/user/apps/appData/quantumtaskai \
         -H "x-captain-auth: $CAPTAIN_TOKEN" \
         -d '{"instanceCount": '$((CURRENT_INSTANCES - 1))'}'
fi
```

## 9. Cost Optimization

### Resource Right-sizing
- **Start small**: 512MB RAM, 0.5 CPU
- **Monitor usage**: Scale up only when needed
- **Regular reviews**: Monthly resource usage analysis

### Efficient Resource Usage
- **Shared services**: Use shared PostgreSQL and Redis
- **Image optimization**: Multi-stage Docker builds
- **Caching**: Reduce database load with strategic caching
- **Compression**: Enable gzip compression

### Schedule-based Scaling
```bash
# Scale up during peak hours (9 AM - 6 PM)
0 9 * * 1-5 /scripts/scale-up.sh

# Scale down during off-hours  
0 18 * * 1-5 /scripts/scale-down.sh
0 0 * * 6-7 /scripts/scale-down.sh
```

This comprehensive scaling strategy ensures your Quantum Tasks AI application can handle varying loads efficiently while maintaining cost-effectiveness.