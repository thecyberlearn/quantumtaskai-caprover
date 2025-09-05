# Coolify Deployment Guide

## Quick Setup Steps

### 1. Create New Project in Coolify
- Go to your Coolify dashboard
- Create a new project
- Choose "Deploy from Git Repository"
- Connect your GitHub repository

### 2. Configure Environment Variables
Set these in Coolify's environment variables section:

```env
SECRET_KEY=your-secret-key-here-generate-50-random-characters
DEBUG=false
ALLOWED_HOSTS=your-coolify-domain.com
DATABASE_URL=postgresql://postgres:password@db:5432/quantumtasks
POSTGRES_DB=quantumtasks
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
```

Optional variables:
```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
STRIPE_SECRET_KEY=sk_test_your_stripe_key
```

### 3. Database Setup
Coolify will automatically create a PostgreSQL database using the docker-compose.yml configuration.

### 4. Deploy
- Push your code to the connected repository
- Coolify will automatically build and deploy
- The app will be available on port 3000

## File Structure Created
- `Dockerfile` - Main container configuration
- `docker-compose.yml` - Multi-service setup with PostgreSQL
- `.env.example` - Updated environment variable template

## Features Included
- ✅ PostgreSQL database
- ✅ Static file serving with WhiteNoise
- ✅ Automatic migrations on startup
- ✅ Gunicorn production server
- ✅ Volume persistence for media files

## Post-Deployment
1. Create superuser: Access the container and run `python manage.py createsuperuser`
2. Configure domain in Coolify dashboard
3. Set up SSL certificate (Coolify handles this automatically)

Your Django app will be ready at your configured Coolify domain!