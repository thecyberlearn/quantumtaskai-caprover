# CLAUDE-SIMPLE.md

This file provides simplified guidance for CapRover deployment of Quantum Tasks AI.

## Simplified Project Overview

Quantum Tasks AI is a basic Django AI agent marketplace. Users can browse agents and execute them through simple web forms.

**Core Architecture:**
- **Django Framework**: Basic Django 5.2.4 setup
- **Agent System**: File-based JSON agent configs with simple execution
- **Authentication**: Basic Django user authentication
- **Payments**: Simple Stripe integration
- **Database**: SQLite for development, PostgreSQL for production

## Quick Development Setup

```bash
# Use virtual environment
source venv/bin/activate

# Install minimal dependencies
pip install -r requirements-simple.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

## Simple CapRover Deployment

### 1. Use Simplified Configuration

Update your Django settings to use the simplified version:

```python
# In manage.py, wsgi.py, etc., change:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netcop_hub.simple_settings')
```

### 2. Environment Variables (Minimal)

```env
SECRET_KEY=your-secret-key-here
DEBUG=false
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgres://user:pass@host:5432/dbname

# Optional - for email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Optional - for payments
STRIPE_SECRET_KEY=sk_test_your_stripe_key
```

### 3. Captain Definition

```json
{
  "schemaVersion": 2,
  "dockerfilePath": "./Dockerfile.simple"
}
```

### 4. Simple Dockerfile

Create `Dockerfile.simple`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-simple.txt .
RUN pip install -r requirements-simple.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 3000
CMD ["gunicorn", "netcop_hub.wsgi:application", "--bind", "0.0.0.0:3000"]
```

## Core Features

### Agent Management
- JSON file-based agents in `agents/configs/agents/`
- Simple categories in `agents/configs/categories/categories.json`
- Basic execution through web forms

### Apps Structure
- **core/**: Homepage and basic views
- **authentication/**: User registration/login
- **agents/**: Agent marketplace and execution
- **wallet/**: Basic Stripe payments

### Simple Agent System

Use `agents.simple_services.SimpleAgentService` instead of the complex caching system:

```python
from agents.simple_services import SimpleAgentService

# Get all agents
agents = SimpleAgentService.get_all_agents()

# Get specific agent
agent = SimpleAgentService.get_agent('agent-slug')

# Get categories
categories = SimpleAgentService.get_categories()
```

## Deployment Commands

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start with gunicorn
gunicorn netcop_hub.wsgi:application --bind 0.0.0.0:3000
```

## What Was Removed

- Complex security middleware and CSP
- Advanced caching systems
- Performance optimizations
- Complex validation systems
- Advanced logging and monitoring
- Redis dependencies
- Rate limiting
- Security scanning
- Emergency rollback systems

## Simple Architecture Status

- ✅ **Basic Django Setup** - Standard Django configuration
- ✅ **File-based Agents** - Simple JSON agent configs
- ✅ **Basic Authentication** - Django's built-in auth
- ✅ **Simple Payments** - Basic Stripe integration
- ✅ **Static Files** - WhiteNoise for production
- ✅ **Database** - SQLite/PostgreSQL support
- ✅ **Minimal Dependencies** - Only essential packages

This version focuses on core functionality for CapRover deployment without enterprise-grade optimizations.

---
Last updated: 2025-09-04 (Simplified for CapRover)