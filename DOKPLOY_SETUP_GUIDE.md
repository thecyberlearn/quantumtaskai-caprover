# Complete Dokploy Configuration Guide
## Hosting Quantum Tasks AI on ai.quantumtaskai.com

This guide walks you through the exact steps to configure your project in Dokploy.

---

## 🔧 Step 1: Access Dokploy Dashboard

1. **Open your browser** and navigate to your Dokploy dashboard:
   ```
   https://your-dokploy-server.com
   ```

2. **Login** with your Dokploy credentials

---

## 🆕 Step 2: Create New Project

1. **Click "Create Project"** or the **"+"** button in the dashboard

2. **Choose Project Type**:
   - Select **"Docker Compose"** (this is important!)
   - NOT "Application" or "Database" - we need Compose for multiple services

3. **Project Configuration**:
   ```
   Project Name: quantumtasks-ai
   Description: Quantum Tasks AI Marketplace
   ```

---

## 📁 Step 3: Connect Git Repository

1. **Repository Source**: Choose **"Git Repository"**

2. **Repository URL**: Enter your repository URL:
   ```
   https://github.com/your-username/quantumtaskai-caprover.git
   ```
   
3. **Branch**: Set to `main` or `master` (whatever your default branch is)

4. **Authentication** (if private repo):
   - Use **Personal Access Token** or **SSH Key**
   - For GitHub: Settings → Developer settings → Personal access tokens

5. **Build Path**: Leave as `.` (root directory)

---

## 🐳 Step 4: Docker Compose Configuration

1. **Compose File Path**: Set to `docker-compose.yml`

2. **Build Context**: Set to `.` (root directory)

3. **Auto Deploy**: Enable this for automatic deployments on git push

---

## 🌐 Step 5: Domain Configuration

1. **Go to "Domains" tab** in your project

2. **Add Domain**:
   ```
   Domain: ai.quantumtaskai.com
   Port: 80 (nginx service will handle SSL)
   ```

3. **SSL Certificate**:
   - Enable **"Generate SSL Certificate"**
   - Choose **"Let's Encrypt"**
   - This will automatically handle HTTPS

---

## ⚙️ Step 6: Environment Variables

**Go to "Environment" tab** and add these variables:

### 🔑 Essential Variables (REQUIRED)
```env
SECRET_KEY=your-django-secret-key-50-characters-minimum
DEBUG=false
ALLOWED_HOSTS=ai.quantumtaskai.com,*.quantumtaskai.com,quantumtaskai.com
CSRF_TRUSTED_ORIGINS=https://ai.quantumtaskai.com,https://quantumtaskai.com
```

### 🗄️ Neon Database Variable
```env
NEON_DATABASE_URL=postgresql://your_username:your_password@your_endpoint.neon.tech/quantumtasks_ai?sslmode=require
```
**📝 Get this from your Neon dashboard**: Project → Dashboard → Connection Details → Connection String

### 📧 Email Configuration (Required for user accounts)
```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=Quantum Tasks AI <noreply@ai.quantumtaskai.com>
REQUIRE_EMAIL_VERIFICATION=true
```

### 💳 Payment Integration (Optional but recommended)
```env
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### 🤖 AI API Keys (Optional but needed for AI features)
```env
OPENAI_API_KEY=sk-your_openai_api_key_here
GROQ_API_KEY=gsk_your_groq_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here
OPENWEATHER_API_KEY=your_weather_api_key_here
```

### 🔒 Security Settings
```env
SECURE_SSL_REDIRECT=true
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
COMPOSE_PROJECT_NAME=quantumtasks-ai
```

---

## 🚀 Step 7: Deploy the Project

1. **Review Configuration**:
   - ✅ Docker Compose file: `docker-compose.yml`
   - ✅ Domain: `ai.quantumtaskai.com`
   - ✅ Environment variables set
   - ✅ SSL enabled

2. **Click "Deploy"** button

3. **Monitor the Build Process**:
   - Watch the logs in real-time
   - Build process will:
     - Clone your repository
     - Build the Docker image
     - Start all services (nginx, web, db)
     - Run health checks

4. **Wait for "Healthy" Status**:
   - All services should show green/healthy status
   - This may take 3-5 minutes

---

## ✅ Step 8: Post-Deployment Configuration

### Initialize Database
Once deployment is complete, you need to set up the database:

1. **Access Container Terminal** in Dokploy:
   - Go to your project → Services → web service
   - Click "Terminal" or "Console"

2. **Run Database Migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```
   - Enter username, email, and password when prompted

4. **Collect Static Files** (if needed):
   ```bash
   python manage.py collectstatic --noinput
   ```

---

## 🔍 Step 9: Verify Deployment

### Test Your Application:

1. **Health Check**:
   ```
   https://ai.quantumtaskai.com/health/
   ```
   Should return: `{"status": "healthy", ...}`

2. **Main Website**:
   ```
   https://ai.quantumtaskai.com/
   ```
   Should load your marketplace

3. **Admin Panel**:
   ```
   https://ai.quantumtaskai.com/admin/
   ```
   Login with your superuser credentials

4. **Check HTTPS Redirect**:
   ```
   http://ai.quantumtaskai.com/
   ```
   Should automatically redirect to HTTPS

---

## 🔧 Step 10: Configure DNS (If Not Done)

If your domain isn't pointing to Dokploy server yet:

1. **Get Your Server IP**:
   - From your Dokploy dashboard or server provider

2. **Add DNS Record**:
   ```
   Type: A
   Name: ai
   Value: YOUR_DOKPLOY_SERVER_IP
   TTL: 300 (5 minutes)
   ```

3. **Wait for Propagation** (can take up to 24 hours, usually 5-10 minutes)

---

## 📊 Monitoring & Logs

### View Logs in Dokploy:
1. **Project Dashboard** → **Logs**
2. **Individual Service Logs**:
   - `nginx`: Web server logs
   - `web`: Django application logs

### Check Service Health:
- All services should show **"Healthy"** status
- If any service is unhealthy, check its logs

---

## 🚨 Common Issues & Solutions

### Issue 1: Build Fails
**Solution**:
- Check if all files are committed to git
- Verify `docker-compose.yml` is in repository root
- Check environment variables are set

### Issue 2: Domain Not Working
**Solution**:
- Verify DNS settings
- Check domain configuration in Dokploy
- Ensure SSL certificate generated successfully

### Issue 3: Database Connection Error
**Solution**:
- Verify `NEON_DATABASE_URL` is correctly formatted
- Check Neon database is running (visit neon.tech dashboard)
- Ensure connection string includes `?sslmode=require`
- Test connection from Neon dashboard SQL editor

### Issue 4: Static Files Not Loading
**Solution**:
- Run `python manage.py collectstatic --noinput` in container
- Check nginx service logs
- Verify volumes are properly mounted

---

## 🎯 Quick Checklist

Before deployment:
- [ ] Repository contains all required files
- [ ] Domain points to Dokploy server
- [ ] All environment variables configured
- [ ] Gmail app password created (for email)
- [ ] API keys obtained (OpenAI, Stripe, etc.)

After deployment:
- [ ] All services show "Healthy" status
- [ ] Database migrations completed
- [ ] Superuser account created
- [ ] Health check returns success
- [ ] Website loads correctly
- [ ] HTTPS redirect works
- [ ] Admin panel accessible

---

## 📞 Need Help?

If you encounter issues:

1. **Check Dokploy logs** first
2. **Verify all environment variables** are set correctly  
3. **Test database connectivity** from web container
4. **Check domain DNS** propagation
5. **Review nginx configuration** for any errors

---

**Target URL**: https://ai.quantumtaskai.com  
**Deployment Status**: Ready to Deploy ✅

Your Quantum Tasks AI marketplace will be live and accessible once these steps are completed!
