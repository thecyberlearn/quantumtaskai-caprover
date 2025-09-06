# Dokploy Deployment Guide for Quantum Tasks AI

Deploy Quantum Tasks AI to **ai.quantumtaskai.com** using Dokploy with PostgreSQL database.

## 🚀 Quick Deployment Steps

### 1. Prerequisites

- Dokploy server installed and running
- Domain `ai.quantumtaskai.com` pointing to your Dokploy server
- SSL certificate for the domain (Dokploy can handle Let's Encrypt automatically)

### 2. Create New Project in Dokploy

1. Log into your Dokploy dashboard
2. Click "Create New Project"
3. Choose "Compose" deployment type
4. Name: `quantumtasks-ai`
5. Repository: Connect your Git repository

### 3. Upload Configuration Files

Make sure these files are in your repository root:
- ✅ `docker-compose.yml` (created)
- ✅ `Dockerfile` (created)  
- ✅ `nginx.conf` (created)
- ✅ `.env.dokploy` (template created)

### 4. Environment Configuration

In Dokploy, set these environment variables:

#### Essential Variables (Required)
```env
# Django Core
SECRET_KEY=your-super-secret-key-here-50-chars-minimum
DEBUG=false
ALLOWED_HOSTS=ai.quantumtaskai.com,*.quantumtaskai.com
CSRF_TRUSTED_ORIGINS=https://ai.quantumtaskai.com

# Database  
POSTGRES_DB=quantumtasks_ai
POSTGRES_PASSWORD=your-strong-postgres-password
DATABASE_URL=postgresql://postgres:your-password@db:5432/quantumtasks_ai

# Email (Required for user verification)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

#### Optional Variables (Recommended)
```env
# Payment Processing
STRIPE_SECRET_KEY=sk_live_your_stripe_key

# AI APIs
OPENAI_API_KEY=sk-your_openai_key
GROQ_API_KEY=gsk_your_groq_key
SERPAPI_API_KEY=your_serpapi_key

# Weather API
OPENWEATHER_API_KEY=your_weather_key
```

### 5. Domain Configuration

1. In Dokploy project settings:
   - **Domain**: `ai.quantumtaskai.com`
   - **SSL**: Enable (Let's Encrypt)
   - **Port**: 80 (nginx will handle SSL redirect)

2. DNS Setup:
   ```
   A    ai.quantumtaskai.com    -> YOUR_DOKPLOY_SERVER_IP
   ```

### 6. Deploy

1. Click "Deploy" in Dokploy dashboard
2. Monitor the build process
3. Wait for all services to be healthy

## 🏗️ Architecture Overview

```
Internet -> Nginx (SSL/Proxy) -> Django App -> PostgreSQL
```

### Services:
- **nginx**: Reverse proxy with SSL termination, static files serving
- **web**: Django application (Gunicorn)
- **db**: PostgreSQL 15 database

### Volumes:
- `postgres_data`: Database persistence
- `static_volume`: Static files (CSS, JS, images)  
- `media_volume`: User uploaded files

## 🔧 Post-Deployment Tasks

### 1. Database Initialization
```bash
# Access your Dokploy server and run:
docker exec -it quantumtasks-ai_web_1 python manage.py migrate
docker exec -it quantumtasks-ai_web_1 python manage.py createsuperuser
```

### 2. Collect Static Files (if needed)
```bash
docker exec -it quantumtasks-ai_web_1 python manage.py collectstatic --noinput
```

### 3. Test the Deployment
- Visit: https://ai.quantumtaskai.com/health/
- Expected response: `{"status": "healthy", ...}`

## 🔍 Monitoring & Troubleshooting

### Health Checks
- **Application**: https://ai.quantumtaskai.com/health/
- **Admin Panel**: https://ai.quantumtaskai.com/admin/

### Log Access
```bash
# View application logs
docker logs quantumtasks-ai_web_1 -f

# View database logs  
docker logs quantumtasks-ai_db_1 -f

# View nginx logs
docker logs quantumtasks-ai_nginx_1 -f
```

### Common Issues

#### SSL Certificate Issues
- Ensure domain is correctly pointing to server
- Check Dokploy SSL configuration
- Verify Let's Encrypt rate limits

#### Database Connection Issues
- Check PostgreSQL logs
- Verify DATABASE_URL format
- Ensure database container is healthy

#### Static Files Not Loading
- Check nginx configuration
- Verify static volume mounting
- Run collectstatic if needed

## 🔐 Security Features

- **HTTPS Only**: Automatic HTTP to HTTPS redirect
- **Security Headers**: XSS, CSRF, Content-Type protection
- **Rate Limiting**: API and web request throttling
- **Database Security**: Isolated database container
- **Secrets Management**: Environment variables only

## 📊 Performance Features

- **Nginx Caching**: Static files cached for 1 year
- **Gzip Compression**: Text content compressed
- **Database Connection Pooling**: Optimized DB connections
- **Health Checks**: Automatic service monitoring

## 🔄 Updates & Maintenance

### Updating the Application
1. Push code changes to your Git repository
2. In Dokploy dashboard, click "Redeploy"
3. Monitor deployment process

### Database Backups
```bash
# Create backup
docker exec quantumtasks-ai_db_1 pg_dump -U postgres quantumtasks_ai > backup.sql

# Restore backup
docker exec -i quantumtasks-ai_db_1 psql -U postgres quantumtasks_ai < backup.sql
```

### Scaling
- **Horizontal**: Add more web service replicas in docker-compose.yml
- **Vertical**: Increase container resource limits in Dokploy

## 🌟 Production Checklist

Before going live:

- [ ] Set strong SECRET_KEY (50+ random characters)
- [ ] Configure email settings (Gmail App Password recommended)
- [ ] Set up Stripe payment keys (live keys for production)
- [ ] Configure AI API keys (OpenAI, Groq, etc.)
- [ ] Test all core functionality
- [ ] Set up database backups
- [ ] Monitor error logs
- [ ] Configure domain SSL certificate

## 📞 Support

If you encounter issues:

1. Check application logs first
2. Verify environment variables
3. Test database connectivity
4. Check domain DNS settings
5. Review nginx configuration

---

**Deployment Target**: https://ai.quantumtaskai.com
**Last Updated**: 2025-09-06
**Status**: Ready for Production
