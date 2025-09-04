# CapRover Security and Backup Optimization

## 1. Enhanced Security Configuration

### SSL/TLS Optimization
1. **CapRover Dashboard** → **Apps** → **quantumtaskai** → **HTTP Settings**
2. **Enable**: Force HTTPS
3. **Enable**: HTTP Strict Transport Security (HSTS)
4. **Set**: HSTS Max Age to 31536000 (1 year)

### Security Headers (Already Implemented)
Your Django settings already include excellent security headers:
- Content Security Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options  
- Referrer-Policy

### Additional Security Environment Variables
Add these to your CapRover environment variables:

```env
# Security Settings
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true

# Rate Limiting
RATELIMIT_ENABLE=true
RATELIMIT_USE_CACHE=default

# Additional Security
ALLOWED_HOSTS=quantumtaskai.captain.your-domain.com,your-custom-domain.com
CSRF_TRUSTED_ORIGINS=https://quantumtaskai.captain.your-domain.com,https://your-custom-domain.com
```

## 2. Database Security

### PostgreSQL Security Hardening
1. **Access pgAdmin** → **quantum-digital-db**
2. **Create specific user** for quantum_render:
```sql
-- Create dedicated user for quantum_render
CREATE USER quantum_render_user WITH PASSWORD 'secure-unique-password';
GRANT CONNECT ON DATABASE quantum-tasks-db TO quantum_render_user;
GRANT USAGE ON SCHEMA public TO quantum_render_user;
GRANT CREATE ON SCHEMA public TO quantum_render_user;

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO quantum_render_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO quantum_render_user;
```

3. **Update DATABASE_URL**:
```env
DATABASE_URL=postgres://quantum_render_user:secure-unique-password@srv-captain--quantum-digital-db:5432/quantum-tasks-db
```

### Database Connection Security
- Use connection pooling (already configured)
- Enable SSL connections if supported
- Regular password rotation

## 3. Backup Strategy

### Automated Database Backups

#### Option A: CapRover Cron Jobs
Create a backup container that runs scheduled backups:

**Dockerfile.backup:**
```dockerfile
FROM postgres:15-alpine

RUN apk add --no-cache aws-cli

COPY backup-script.sh /backup-script.sh
RUN chmod +x /backup-script.sh

ENTRYPOINT ["/backup-script.sh"]
```

**backup-script.sh:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="quantum-tasks-db-backup-$DATE.sql"

# Create backup
pg_dump -h srv-captain--quantum-digital-db -U quantum_user -d quantum-tasks-db > /tmp/$BACKUP_FILE

# Compress backup
gzip /tmp/$BACKUP_FILE

# Upload to cloud storage (optional)
# aws s3 cp /tmp/$BACKUP_FILE.gz s3://your-backup-bucket/

# Keep local copy for quick restore
cp /tmp/$BACKUP_FILE.gz /backups/

# Clean old backups (keep last 7 days)
find /backups -name "*.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

#### Option B: Manual Backup Commands
```bash
# Create manual backup
docker exec [postgres-container] pg_dump -U quantum_user quantum-tasks-db > backup_$(date +%Y%m%d).sql

# Restore from backup
docker exec -i [postgres-container] psql -U quantum_user quantum-tasks-db < backup_file.sql
```

### Application Data Backup

#### Media Files Backup
```bash
# Backup media files
docker exec [app-container] tar -czf /tmp/media-backup-$(date +%Y%m%d).tar.gz /app/media/

# Copy to host
docker cp [app-container]:/tmp/media-backup-$(date +%Y%m%d).tar.gz ./backups/
```

#### Configuration Backup
```bash
# Backup CapRover configuration
# From CapRover server
cp -r /captain/data ./caprover-config-backup-$(date +%Y%m%d)
```

### Cloud Backup Integration

#### AWS S3 Integration
```env
# Add to environment variables
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
BACKUP_BUCKET=quantum-tasks-backups
```

#### Google Cloud Storage
```env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

## 4. Security Monitoring

### Log Monitoring for Security Events
```python
# Add to Django settings
SECURITY_EVENTS_TO_LOG = [
    'authentication_failed',
    'permission_denied', 
    'suspicious_operation',
    'rate_limit_exceeded'
]

# Custom logging for security events
LOGGING['loggers']['security'] = {
    'handlers': ['security_file'],
    'level': 'WARNING',
    'propagate': False,
}
```

### Intrusion Detection
- Monitor failed login attempts
- Track unusual API usage patterns
- Alert on multiple failed authentication attempts
- Log all admin actions

### Automated Security Updates
```bash
# Regular security updates (run on host)
apt update && apt upgrade -y

# Docker image updates (rebuild regularly)
# CapRover → Apps → quantumtaskai → Deployment → Force Build
```

## 5. Disaster Recovery Plan

### Recovery Time Objectives (RTO)
- **Database**: < 1 hour
- **Application**: < 30 minutes
- **Full System**: < 2 hours

### Recovery Steps
1. **Database Recovery**:
   ```bash
   # Restore database from latest backup
   docker exec -i [postgres-container] psql -U quantum_user quantum-tasks-db < latest_backup.sql
   ```

2. **Application Recovery**:
   ```bash
   # Redeploy application
   # CapRover → Apps → quantumtaskai → Force Build
   # Run migrations if needed
   docker exec [app-container] python manage.py migrate
   ```

3. **Configuration Recovery**:
   - Restore environment variables from backup
   - Verify DNS and domain settings
   - Test all integrations (Stripe, email, APIs)

### Testing Recovery Procedures
- Monthly backup restoration tests
- Quarterly disaster recovery drills
- Document all procedures and update regularly

## 6. Security Best Practices

### Environment Variables Security
- Use strong, unique passwords
- Rotate secrets regularly (every 90 days)
- Never commit secrets to Git
- Use different keys for staging/production

### Network Security
- Restrict database access to application containers only
- Use CapRover's internal network for inter-container communication
- Configure firewall rules on the host server

### Application Security
- Keep Django and dependencies updated
- Regular security audits with `python -m pip audit`
- Monitor security advisories for used packages
- Implement proper input validation and sanitization

### Access Control
- Use strong passwords for CapRover admin
- Enable two-factor authentication where possible
- Regular access reviews and permission audits
- Separate staging and production environments