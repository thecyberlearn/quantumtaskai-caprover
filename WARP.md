# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**Quantum Tasks AI** is a Django-based AI agent marketplace that allows users to browse, execute, and interact with various AI-powered tools and services. The application is designed for deployment on container platforms like CapRover and Dokploy.

### Core Architecture

- **Framework**: Django 5.2.4 with Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)  
- **Static Files**: WhiteNoise for production serving
- **Agent System**: File-based JSON configuration system
- **Authentication**: Custom User model with email verification
- **Payments**: Stripe integration for agent execution fees
- **Deployment**: Containerized with Docker, optimized for CapRover/Dokploy

### Application Structure

```
├── agents/           # AI agent marketplace and execution system
├── authentication/   # User management and authentication
├── core/            # Homepage, health checks, and utilities
├── wallet/          # Stripe payment integration
├── netcop_hub/      # Django project settings and configuration
├── static/          # Static assets (CSS, JS, images)
├── templates/       # Django HTML templates
└── agents/configs/  # File-based agent configurations
    ├── agents/      # Individual agent JSON files
    └── categories/  # Agent categories configuration
```

## Development Commands

### Local Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Database setup
python manage.py migrate
python manage.py createsuperuser

# Development server
python manage.py runserver
# OR use the development script
./run_dev.sh
```

### Testing and Quality

```bash
# Run Django checks
python manage.py check

# Test database connection
python manage.py check --database default

# Clear agent cache (useful during development)
python manage.py shell -c "from agents.services import AgentFileService; AgentFileService.clear_cache()"
```

### Static Files and Assets

```bash
# Collect static files for production
python manage.py collectstatic --noinput

# Clear cache table
python manage.py createcachetable
```

## Agent System Architecture

### File-Based Configuration
The application uses a file-based agent system instead of database models for agent configurations:

- **Agent configs**: `agents/configs/agents/*.json`
- **Categories**: `agents/configs/categories/categories.json`
- **Service class**: `AgentFileService` handles loading and caching

### Agent Configuration Format
```json
{
  "slug": "agent-identifier",
  "name": "Human Readable Name", 
  "description": "Detailed description",
  "category": "category-slug",
  "price": 0.0,
  "agent_type": "form",
  "system_type": "webhook",
  "webhook_url": "https://external-service.com/webhook",
  "form_schema": {
    "fields": [
      {"name": "input", "type": "text", "label": "Input Field"}
    ]
  }
}
```

### Agent Execution Flow
1. User selects agent from marketplace (`/agents/`)
2. Fills out dynamic form based on `form_schema` 
3. Payment processed via Stripe (if price > 0)
4. Request sent to agent's `webhook_url`
5. Response stored in `AgentExecution` model
6. Results displayed to user

## Deployment Configurations

### CapRover Deployment
- **Docker file**: `Dockerfile.captain`
- **Configuration**: `captain-definition`
- **Port**: 80
- **Startup**: Direct gunicorn execution

### Dokploy Deployment  
- **Docker file**: `Dockerfile.dokploy`
- **Configuration**: `dokploy.json`
- **Port**: 3000
- **Startup**: `start-dokploy.sh` script with migrations

### Environment Variables

**Required for Production:**
```env
SECRET_KEY=your-secret-key-here
DEBUG=false
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

**Optional:**
```env
DATABASE_URL=postgres://user:pass@host:5432/db
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
STRIPE_SECRET_KEY=sk_live_your_stripe_key
```

**Platform-Specific:**
```env
# CapRover auto-detection
CAPROVER_GIT_COMMIT_SHA=auto-set-by-caprover

# Dokploy auto-detection  
DOKPLOY_PROJECT_NAME=your-project-name
```

## Key Application Features

### Authentication System
- Custom User model with email verification
- Password reset functionality
- User wallet balance tracking
- Session management with security headers

### Payment Integration
- Stripe checkout for agent executions
- Wallet balance system
- Transaction logging
- Webhook handling for payment confirmations

### Agent Marketplace
- Category-based organization
- Search and filtering capabilities
- Dynamic form generation based on agent schemas
- Execution history tracking

### Security Features
- CSRF protection with trusted origins
- Rate limiting on critical endpoints
- Security headers (CSP, XSS protection)
- Input validation and sanitization
- Error handling with custom error pages

## Troubleshooting Common Issues

### Dokploy 404 Errors
If getting 404 errors on Dokploy:
1. Ensure `ALLOWED_HOSTS` includes the Dokploy domain
2. Check that port 3000 is correctly configured  
3. Verify health check endpoint `/health/` is accessible
4. Use debug configuration temporarily: `Dockerfile.dokploy.debug`

### Database Issues
- SQLite is used for development (no setup required)
- PostgreSQL for production (requires `DATABASE_URL`)
- Run migrations after deployment: `python manage.py migrate`

### Static Files Problems
- Ensure `python manage.py collectstatic` runs during build
- WhiteNoise handles static file serving in production
- Check `STATIC_ROOT` and `STATICFILES_DIRS` configuration

### Agent Loading Issues
- Agent configs are cached for performance
- Clear cache during development: `AgentFileService.clear_cache()`
- Check JSON syntax in agent configuration files
- Ensure required fields are present in agent schemas

## Important File Locations

- **Main settings**: `netcop_hub/settings.py`
- **URL configuration**: `netcop_hub/urls.py`  
- **Agent service**: `agents/services.py`
- **Health check**: `core/views.py` (health_check_view)
- **Error handlers**: `core/error_views.py`
- **Production startup**: `start-dokploy.sh`

This Django application is optimized for containerized deployment with focus on AI agent marketplace functionality, file-based configuration management, and production-ready security features.
