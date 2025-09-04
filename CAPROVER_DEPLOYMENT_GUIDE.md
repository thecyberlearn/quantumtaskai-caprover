# CapRover Deployment Guide for Quantum Tasks AI

## Overview
This guide provides step-by-step instructions for deploying the Quantum Tasks AI Django application on CapRover.

## Prerequisites
- CapRover installed and running on your VPS
- Git repository with the Quantum Tasks AI project
- Basic understanding of Django and CapRover

---

## Part 1: Project Files Overview

The project includes the following CapRover-specific files:

### Required Files
```
quantum_render/
├── captain-definition          # CapRover configuration
├── Dockerfile.captain         # Production Docker configuration
├── .dockerignore              # Docker build optimization
├── requirements.txt           # Python dependencies (production-ready)
└── netcop_hub/settings.py     # Django settings with CapRover support
```

### Key Configuration Features
- **CapRover Auto-detection**: Automatic host configuration via `CAPROVER_GIT_COMMIT_SHA`
- **Database Flexibility**: Supports SQLite (dev), PostgreSQL (production)
- **Static Files**: WhiteNoise configuration for production
- **Security**: Comprehensive security headers and middleware
- **Environment Variables**: Production-ready configuration

---

## Part 2: Deploy PostgreSQL Database

### 2.1 Deploy PostgreSQL
1. **CapRover Dashboard** → **Apps** → **One-Click Apps/Databases**
2. **Search:** `PostgreSQL`
3. **Configure:**
   - App Name: `quantum-ai-db`
   - Version: `14.5` (recommended)
   - Username: `quantum_user`
   - Password: `secure_password_123`
   - Default Database: `quantum_ai`
4. **Click Deploy**

### 2.2 Note Connection Details
After deployment, note the internal hostname:
- Format: `srv-captain--quantum-ai-db:5432`
- Full URL: `postgres://quantum_user:secure_password_123@srv-captain--quantum-ai-db:5432/quantum_ai`

---

## Part 3: Deploy Quantum Tasks AI Application

### 3.1 Create Django App
1. **CapRover Dashboard** → **Apps** → **Create New App**
2. **App Name:** `quantum-tasks-ai`
3. **Check:** "Has Persistent Data" (for media files)
4. **Click:** "Create New App"

### 3.2 Configure Git Deployment
1. **Go to your app** → **Deployment tab**
2. **Select:** "Method 3: Deploy from Github/Bitbucket/Gitlab"
3. **Repository URL:** `https://github.com/yourusername/quantum_render.git`
4. **Branch:** `main`
5. **Click:** "Save & Update"

### 3.3 Set Environment Variables
**Go to:** App Configs → Environment Variables

**Required Variables:**
```env
SECRET_KEY=your-generated-secret-key
DEBUG=false
ALLOWED_HOSTS=quantum-tasks-ai.captain.your-domain.com
DATABASE_URL=postgres://quantum_user:secure_password_123@srv-captain--quantum-ai-db:5432/quantum_ai

# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# AI API Keys
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key

# Webhook URLs for N8N integrations
N8N_WEBHOOK_DATA_ANALYZER=https://your-n8n-instance.com/webhook/data-analyzer
N8N_WEBHOOK_FIVE_WHYS=https://your-n8n-instance.com/webhook/five-whys
N8N_WEBHOOK_JOB_POSTING=https://your-n8n-instance.com/webhook/job-posting
N8N_WEBHOOK_SOCIAL_ADS=https://your-n8n-instance.com/webhook/social-ads

# Optional: Redis for caching
REDIS_URL=redis://srv-captain--redis:6379/1
```

**Generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3.4 Deploy Application
1. **Deployment tab** → **Force Build**
2. **Monitor logs** for successful deployment

---

## Part 4: Post-Deployment Setup

### 4.1 Install Portainer (For Container Management)
1. **Apps** → **One-Click Apps** → Search `Portainer`
2. **Deploy** with default settings
3. **Access:** `https://portainer.captain.your-domain.com`
4. **Create admin account**

### 4.2 Run Django Management Commands

#### Via Portainer Console:
1. **Containers** → Find your Django container
2. **Console** → `/bin/bash` → **Connect**
3. **Run commands:**

```bash
# Apply database migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Test the application
python manage.py check

# Collect static files (if needed)
python manage.py collectstatic --noinput
```

#### Via SSH (Alternative):
```bash
# SSH into your server
ssh root@your-server-ip

# Find container ID
docker ps | grep quantum-tasks-ai

# Run management commands
docker exec -it [container-id] python manage.py migrate
docker exec -it [container-id] python manage.py createsuperuser
```

### 4.3 Install pgAdmin (Database Management)
1. **Apps** → **One-Click Apps** → Search `pgAdmin`
2. **Configure:**
   - Email: `admin@example.com`
   - Password: `secure_password`
3. **Deploy**
4. **Access:** `https://pgadmin.captain.your-domain.com`

### 4.4 Connect pgAdmin to PostgreSQL
1. **Login to pgAdmin**
2. **Add Server:**
   - Name: `Quantum AI DB`
   - Host: `srv-captain--quantum-ai-db`
   - Port: `5432`
   - Username: `quantum_user`
   - Password: `secure_password_123`

---

## Part 5: Production Optimization

### 5.1 Enable HTTPS
1. **Your app** → **HTTP Settings**
2. **Enable:** Force HTTPS
3. **Enable:** Websocket Support (if needed)

### 5.2 Configure Custom Domain
1. **Your app** → **HTTP Settings**
2. **Add:** Custom Domain
3. **Update ALLOWED_HOSTS** environment variable

### 5.3 Set up Redis (Optional - For Performance)
1. **Apps** → **One-Click Apps** → Search `Redis`
2. **Deploy** with app name: `quantum-ai-redis`
3. **Update environment variable:** `REDIS_URL=redis://srv-captain--quantum-ai-redis:6379/1`

---

## Part 6: Application-Specific Configuration

### 6.1 Agent System Configuration
The Quantum Tasks AI platform uses a file-based agent system with dual integrations:

**Webhook Agents (N8N):**
- Configure N8N webhook URLs in environment variables
- Test agent execution through the marketplace interface

**Direct Access Agents:**
- Configure external form URLs in agent JSON files
- Test payment flow and form redirection

### 6.2 Stripe Integration Setup
1. **Configure Stripe webhook endpoint:** `https://your-domain.com/wallet/stripe/webhook/`
2. **Set webhook events:**
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

### 6.3 Email Verification Setup
1. **Configure email settings** in environment variables
2. **Test email delivery** from Django admin
3. **Set REQUIRE_EMAIL_VERIFICATION=true** for production

---

## Part 7: Monitoring and Maintenance

### 7.1 Health Checks
The application includes built-in health monitoring:
- **Health endpoint:** `/admin/` (requires authentication)
- **Agent marketplace:** `/agents/` (public)
- **API endpoints:** `/agents/api/` (for execution)

### 7.2 Log Management
Monitor application logs via:
- **CapRover Dashboard:** App logs
- **Portainer:** Container logs
- **File logs:** `/app/logs/` in container

### 7.3 Database Backups
```bash
# Create backup
docker exec [postgres-container] pg_dump -U quantum_user quantum_ai > backup_$(date +%Y%m%d).sql

# Restore backup
docker exec -i [postgres-container] psql -U quantum_user quantum_ai < backup_file.sql
```

---

## Part 8: Troubleshooting

### 8.1 Common Issues

**Build Failures:**
- Check `Dockerfile.captain` syntax
- Verify `requirements.txt` dependencies
- Check `captain-definition` format

**Database Connection Errors:**
- Verify `DATABASE_URL` format
- Check PostgreSQL container is running
- Confirm environment variables

**Agent Execution Issues:**
- Verify N8N webhook URLs
- Check API keys configuration
- Monitor execution logs in Django admin

**Email Issues:**
- Test SMTP configuration
- Check email credentials
- Verify firewall settings

### 8.2 Useful Commands

```bash
# Check container logs
docker logs [container-id]

# Database connection test
docker exec [container-id] python manage.py check_db

# Agent system test
docker exec [container-id] python manage.py shell -c "from agents.services import AgentFileService; print(AgentFileService.get_agent_stats())"

# Test webhooks
curl -X POST https://your-domain.com/agents/api/execute/ \
  -H "Content-Type: application/json" \
  -d '{"agent_slug": "test-agent", "form_data": {}}'
```

---

## Security Best Practices

### Environment Variables
- Never commit secrets to Git
- Use strong passwords for all services
- Rotate SECRET_KEY regularly
- Use separate API keys for production

### Database Security
- Use specific database users per app
- Restrict database permissions
- Enable connection encryption
- Regular backups

### Application Security
- Keep Django updated
- Use HTTPS in production
- Configure proper ALLOWED_HOSTS
- Monitor security logs

---

## Quick Reference

### Essential URLs
- **CapRover:** `https://captain.your-domain.com`
- **Quantum Tasks AI:** `https://quantum-tasks-ai.captain.your-domain.com`
- **Portainer:** `https://portainer.captain.your-domain.com`
- **pgAdmin:** `https://pgadmin.captain.your-domain.com`

### Key Management Commands
```bash
# Django management
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
python manage.py check_db

# Agent system
python manage.py shell -c "from agents.services import AgentFileService; print('Agents:', AgentFileService.list_agents())"

# Docker
docker ps
docker logs [container-id]
docker exec -it [container-id] /bin/bash
```

This guide provides a complete deployment process for the Quantum Tasks AI platform on CapRover, taking advantage of the application's production-ready configuration and dual agent integration system.