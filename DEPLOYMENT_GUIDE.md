# CapRover Deployment Guide - Quantum Tasks AI

## Overview
Step-by-step guide for deploying the Quantum Tasks AI Django application on CapRover.

## Prerequisites
- CapRover installed and running on your VPS
- GitHub repository with the project
- Basic understanding of Django and CapRover

---

## Part 1: Project Setup

### Required Files
Your repository contains these CapRover-ready files:
```
quantumtaskai-caprover/
├── captain-definition          # CapRover configuration  
├── Dockerfile.captain         # Production Docker setup
├── requirements.txt           # Essential Python dependencies
├── .dockerignore              # Docker build optimization
└── netcop_hub/settings.py     # Django settings with production support
```

### Key Features
- **Database**: Supports SQLite (dev), PostgreSQL (production)
- **Static Files**: WhiteNoise for production serving
- **Environment Variables**: Production-ready configuration

---

## Part 2: CapRover Deployment

### Step 1: Create New App
1. **Open CapRover Dashboard**
2. **Apps → Create New App**
3. **App Name**: `quantumtaskai` (or your preferred name)
4. **Click "Create New App"**

### Step 2: Configure GitHub Deployment
1. **Go to**: App → Deployment Tab
2. **Method**: Deploy from GitHub
3. **Repository**: `https://github.com/thecyberlearn/quantumtaskai-caprover.git`
4. **Branch**: `main`
5. **Authentication**: Use GitHub Personal Access Token

### Step 3: Environment Variables
**Go to**: App Configs → Environment Variables → Bulk Edit

**Essential Variables:**
```env
SECRET_KEY=your-unique-secret-key-here
DEBUG=false
ALLOWED_HOSTS=yourapp.yourdomain.com
DATABASE_URL=postgres://user:password@host:5432/database
```

**Optional Variables:**
```env
# Email Configuration (for notifications)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Stripe Configuration (for payments)
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

### Step 4: Deploy Application
1. **Deployment Tab** → **Deploy Now**
2. **Monitor build logs** for successful completion
3. **Check App URL** after deployment completes

---

## Part 3: Database Setup (Optional)

If you need PostgreSQL database:

### Option A: CapRover PostgreSQL
1. **One-Click Apps** → **PostgreSQL**
2. **Create database instance**
3. **Get connection details** from app configs
4. **Add DATABASE_URL** to your app environment variables

### Option B: External Database
1. **Use Railway, Neon, or other PostgreSQL provider**
2. **Get connection string**
3. **Add to environment variables**

---

## Part 4: Custom Domain (Optional)

1. **App Settings** → **HTTP Settings**
2. **Add your domain**: `yourdomain.com`
3. **Enable HTTPS**: Force HTTPS redirect
4. **Update DNS**: Point your domain to CapRover server IP

---

## Part 5: Post-Deployment

### Create Admin User
1. **App → Web Terminal**
2. **Run commands**:
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Verify Deployment
1. **Visit your app URL**
2. **Check admin panel**: `/admin/`
3. **Test agent marketplace**: `/agents/`

---

## Troubleshooting

### Build Failures
- **Check logs** in Deployment tab
- **Verify environment variables** are set
- **Ensure SECRET_KEY** is properly set

### Runtime Issues
- **Check App Logs** in CapRover dashboard
- **Verify DATABASE_URL** format
- **Check ALLOWED_HOSTS** includes your domain

### Database Issues
- **Run migrations**: `python manage.py migrate`
- **Check database connectivity**
- **Verify PostgreSQL is running** (if using)

---

## Environment Variable Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | Yes | Set to `false` for production |
| `ALLOWED_HOSTS` | Yes | Your domain name |
| `DATABASE_URL` | Optional | PostgreSQL connection string |
| `EMAIL_HOST_USER` | Optional | SMTP email username |
| `EMAIL_HOST_PASSWORD` | Optional | SMTP email password |
| `STRIPE_SECRET_KEY` | Optional | Stripe API key |

---

## Success Checklist

- [ ] App builds successfully in CapRover
- [ ] Environment variables configured
- [ ] Database migrations completed
- [ ] Admin user created
- [ ] App accessible via URL
- [ ] Static files loading correctly
- [ ] Agent marketplace functional

Your Quantum Tasks AI application should now be live and ready to use!

---

## Support

For issues with:
- **CapRover deployment**: Check CapRover documentation
- **Django configuration**: Review `netcop_hub/settings.py`
- **Agent system**: See `agents/` directory structure