# Redis Setup for CapRover Optimization

## Deploy Redis in CapRover

### Step 1: Deploy Redis
1. **CapRover Dashboard** → **Apps** → **One-Click Apps/Databases**
2. **Search**: `Redis`
3. **Configure**:
   - App Name: `quantum-tasks-redis`
   - Version: `7-alpine` (recommended)
   - Password: `your-secure-redis-password`
4. **Deploy**

### Step 2: Update Environment Variables
Add to your quantum_render app environment variables:

```env
REDIS_URL=redis://:your-secure-redis-password@srv-captain--quantum-tasks-redis:6379/1
CACHE_TTL=300
SESSION_COOKIE_AGE=7200
```

### Step 3: Redis Configuration Benefits
- **Session Storage**: Store user sessions in Redis instead of database
- **Database Query Caching**: Cache expensive database queries
- **Agent Execution Caching**: Cache agent results temporarily
- **User Balance Caching**: Cache wallet balances for faster access

### Step 4: Monitor Redis Usage
Access Redis via CapRover logs or connect with Redis CLI:
```bash
# Via container
docker exec -it [redis-container] redis-cli
# Check memory usage
INFO memory
# Check key statistics
INFO keyspace
```