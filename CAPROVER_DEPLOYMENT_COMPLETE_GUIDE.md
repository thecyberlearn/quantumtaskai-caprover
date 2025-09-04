# Complete CapRover Deployment Guide - Quantum Tasks AI

## Overview
This is the complete, tested deployment guide for deploying the Quantum Tasks AI Django application on CapRover, based on successful deployment experience.

---

## Prerequisites
- CapRover installed and running on your VPS
- PostgreSQL database already deployed in CapRover  
- GitHub repository with the Django project
- GitHub Personal Access Token for private repository access

---

## Part 1: Repository Preparation

### 1.1 Required Files (Already Created)
Your repository should contain these CapRover-specific files:

```
quantum_render/
├── captain-definition          # CapRover configuration
├── Dockerfile.captain         # Production Docker configuration  
├── .dockerignore              # Docker build optimization
├── CAPROVER_DEPLOYMENT_GUIDE.md # This documentation
└── netcop_hub/settings.py     # Django settings with CapRover support
```

### 1.2 Key Configuration Files

**captain-definition:**
```json
{
  "schemaVersion": 2,
  "dockerfilePath": "./Dockerfile.captain"
}
```

**Dockerfile.captain:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set a dummy SECRET_KEY for build time only
ENV SECRET_KEY="build-time-dummy-key-not-for-production"

# Collect static files
RUN python manage.py collectstatic --noinput

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 80

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:80", "netcop_hub.wsgi:application"]
```

### 1.3 Django Settings Configuration
**Key settings for CapRover compatibility:**

```python
# CapRover auto-detection
if config('CAPROVER_GIT_COMMIT_SHA', default=''):
    ALLOWED_HOSTS = ['*']  # Allow all hosts in CapRover environment

# Build-time compatible SECRET_KEY
SECRET_KEY = config('SECRET_KEY', default='build-time-dummy-key-change-in-production')

# Smart database configuration with CapRover support
database_url = config('DATABASE_URL', default='')
if database_url:
    DATABASES = {
        'default': dj_database_url.parse(database_url, conn_max_age=600)
    }
```

---

## Part 2: Database Setup (Shared PostgreSQL)

### 2.1 Existing PostgreSQL Configuration
**Our setup uses a shared PostgreSQL instance:**

```
PostgreSQL App: "quantum-digital-db"
├── postgres (used by quantum-digital app)
└── quantum-tasks-db (used by quantum_render app)
```

### 2.2 Database Connection Details
**From CapRover PostgreSQL environment variables:**
- **Username**: `quantum_user`
- **Password**: `7e9f4e144881879c`  
- **Host**: `srv-captain--quantum-digital-db:5432`
- **Database**: `quantum-tasks-db`

**Complete DATABASE_URL:**
```
postgres://quantum_user:7e9f4e144881879c@srv-captain--quantum-digital-db:5432/quantum-tasks-db
```

---

## Part 3: CapRover Application Deployment

### 3.1 Create CapRover App
1. **CapRover Dashboard** → **Apps** → **Create New App**
2. **App Name**: `quantumtaskai` (or your preferred name)
3. **Check**: "Has Persistent Data" (for media files)
4. **Click**: "Create New App"

### 3.2 Configure Git Deployment

#### 3.2.1 Repository Configuration
1. **Go to your app** → **Deployment tab**
2. **Select**: "Method 3: Deploy from Github/Bitbucket/Gitlab"

#### 3.2.2 Private Repository Authentication (Working Solution)
**Repository URL:**
```
https://github.com/quantumtaskai/qunatum-render.git
```

**Authentication (Method B - Tested and Working):**
- **Username**: `quantumtaskai` (your GitHub username)
- **Password**: `ghp_your_github_personal_access_token` (GitHub Personal Access Token)
- **Branch**: `main`

**Note:** The username/password method proved more reliable than embedding tokens in the URL.

### 3.3 Environment Variables Configuration

**Go to:** App Configs → Environment Variables → Bulk Edit

**Complete Environment Variables:**
```env
DATABASE_URL=postgres://quantum_user:7e9f4e144881879c@srv-captain--quantum-digital-db:5432/quantum-tasks-db
SECRET_KEY=d)3s=sh(^gijpjoo^=0y-0(c23j%$*b8=vb4yo&p_(xr(17tt1
DEBUG=false
ALLOWED_HOSTS=quantumtaskai.captain.your-domain.com
DEPLOYMENT_ENVIRONMENT=production

# Email Configuration
EMAIL_HOST_USER=thecyberlearn@gmail.com
EMAIL_HOST_PASSWORD=ueqd ulan xcwl cfrr

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_test_key
STRIPE_WEBHOOK_SECRET=whsec_3IbdUV75ljx5TdHdDGnEgGLRSvOopYyy

# AI API Keys
OPENAI_API_KEY=sk-proj-your_openai_api_key
GROQ_API_KEY=gsk_your_groq_api_key
SERPAPI_API_KEY=2b8a90c1f2e3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7g8h9i0
```

### 3.4 Deploy Application
1. **Deployment tab** → **Force Build**
2. **Monitor build logs** for successful completion
3. **Build should complete without errors** (SECRET_KEY issue resolved)

---

## Part 4: Post-Deployment Configuration

### 4.1 Database Migrations and Setup

**Methods to run Django management commands:**

#### Method A: SSH into CapRover Server
```bash
# SSH into your CapRover server
ssh root@your-server-ip

# Find your container
docker ps | grep quantumtaskai

# Run Django commands
docker exec -it [container-id] python manage.py migrate
docker exec -it [container-id] python manage.py createsuperuser
docker exec -it [container-id] python manage.py check
```

#### Method B: Portainer Console (if available)
1. **Access Portainer**: `https://portainer.captain.your-domain.com`
2. **Containers** → Find your Django container
3. **Console** → `/bin/bash` → **Connect**
4. **Run commands**:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py check
```

### 4.2 Required Management Commands
```bash
# Apply database migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Verify application health
python manage.py check

# Test agent system (optional)
python manage.py shell -c "from agents.services import AgentFileService; print('Agents:', AgentFileService.get_agent_stats())"
```

---

## Part 5: Application Testing and Verification

### 5.1 Access Points
- **Main Application**: `https://quantumtaskai.captain.your-domain.com`
- **Admin Interface**: `https://quantumtaskai.captain.your-domain.com/admin/`
- **Agent Marketplace**: `https://quantumtaskai.captain.your-domain.com/agents/`
- **API Endpoints**: `https://quantumtaskai.captain.your-domain.com/agents/api/`

### 5.2 Verification Checklist
- [ ] **Homepage loads** without errors
- [ ] **Database connection** working (no connection errors in logs)
- [ ] **Admin interface** accessible with superuser
- [ ] **Agent marketplace** displays available agents
- [ ] **Static files** loading properly (CSS, JS, images)
- [ ] **Agent execution** works (test with one agent)
- [ ] **Stripe integration** functional (if using payments)
- [ ] **Email system** working (registration, password reset)

---

## Part 6: Production Optimizations

### 6.1 HTTPS Configuration
1. **Your app** → **HTTP Settings**
2. **Enable**: Force HTTPS
3. **Enable**: Websocket Support (if needed for real-time features)

### 6.2 Custom Domain Setup
1. **Your app** → **HTTP Settings**  
2. **Add**: Custom Domain
3. **Update**: `ALLOWED_HOSTS` environment variable with new domain

### 6.3 Monitoring and Logging
- **App Logs**: CapRover Dashboard → Your App → App Logs
- **Container Logs**: Portainer → Containers → Your Container → Logs
- **Database Monitoring**: pgAdmin access for database health

---

## Part 7: Troubleshooting Common Issues

### 7.1 Build Issues

**SECRET_KEY Error During Build:**
- **Fixed in our setup** with dummy key in Dockerfile.captain
- Environment variables override dummy key at runtime

**Git Authentication Failures:**
- **Use Method B**: Username + Personal Access Token
- Ensure token has `repo` scope permissions

### 7.2 Runtime Issues

**Database Connection Errors:**
- Verify `DATABASE_URL` format and credentials
- Check PostgreSQL container is running
- Confirm database `quantum-tasks-db` exists

**Static Files Not Loading:**
- WhiteNoise is configured in settings
- `collectstatic` runs during Docker build
- Check STATIC_ROOT and STATIC_URL settings

**Agent System Issues:**
- Verify N8N webhook URLs in environment variables
- Check API key configurations
- Test agent JSON configurations

### 7.3 Useful Debugging Commands
```bash
# Check container logs
docker logs [container-id]

# Test database connection
docker exec [container-id] python manage.py check_db

# Check Django configuration
docker exec [container-id] python manage.py check

# Test agent system
docker exec [container-id] python manage.py shell -c "from agents.services import AgentFileService; print(AgentFileService.list_agents())"
```

---

## Part 8: Architecture Overview

### 8.1 Deployment Architecture
```
CapRover Server
├── quantum-digital-db (PostgreSQL)
│   ├── postgres (quantum-digital database)
│   └── quantum-tasks-db (quantum_render database)
├── quantumtaskai (Django App)
│   ├── Static Files (WhiteNoise)
│   ├── Media Files (Persistent Volume)
│   └── Application Code
└── portainer (Container Management)
```

### 8.2 Key Features Enabled
- **Agent Marketplace**: File-based agent system with dual integrations
- **Stripe Payments**: Wallet system with transaction tracking
- **Email Verification**: SMTP integration for user authentication
- **N8N Webhooks**: External AI processing integrations
- **Security Middleware**: Comprehensive security headers and CSP
- **Static File Serving**: WhiteNoise for production static files
- **Database Optimization**: Connection pooling and query optimization

---

## Part 9: Maintenance and Updates

### 9.1 Updating the Application
1. **Push changes** to GitHub repository
2. **CapRover Dashboard** → **Apps** → **quantumtaskai** → **Deployment**
3. **Force Build** to deploy latest changes
4. **Run migrations** if database schema changed

### 9.2 Database Backups
```bash
# Create backup
docker exec [postgres-container] pg_dump -U quantum_user quantum-tasks-db > backup_$(date +%Y%m%d).sql

# Restore backup
docker exec -i [postgres-container] psql -U quantum_user quantum-tasks-db < backup_file.sql
```

### 9.3 Monitoring Application Health
- **Regular log monitoring** for errors
- **Database performance** checks via pgAdmin
- **Agent execution** success rates
- **User registration** and email delivery
- **Payment processing** status

---

## Summary

This guide documents the complete, tested deployment process for Quantum Tasks AI on CapRover. The key success factors were:

1. **Proper Docker configuration** with build-time SECRET_KEY handling
2. **Shared PostgreSQL strategy** for resource efficiency
3. **GitHub authentication** using username/token method
4. **Comprehensive environment variable setup**
5. **Post-deployment migration** via SSH/container access

The deployment supports all application features including the agent marketplace, payment system, email verification, and AI integrations, while maintaining security and performance best practices.

**Deployment Status**: ✅ **Successfully Deployed and Tested**