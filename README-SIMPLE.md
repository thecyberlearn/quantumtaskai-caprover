# Quantum Tasks AI - Simple CapRover Deployment

A basic Django AI agent marketplace for CapRover deployment.

## Quick Start

```bash
# Install dependencies
pip install -r requirements-simple.txt

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## CapRover Deployment

1. **Upload to CapRover**: Use `captain-definition-simple` 
2. **Set Environment Variables**:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=false
   ALLOWED_HOSTS=yourdomain.com
   DATABASE_URL=postgres://user:pass@host/db
   ```
3. **Deploy**: Force build in CapRover dashboard

## Project Structure

- `agents/` - AI agent marketplace
- `authentication/` - User registration/login  
- `wallet/` - Basic Stripe payments
- `core/` - Homepage and utilities

## Adding Agents

Add JSON files to `agents/configs/agents/`:

```json
{
  "name": "My Agent",
  "category": "productivity",
  "price": 5,
  "description": "Simple agent description",
  "webhook_url": "https://your-webhook.com",
  "form_schema": {
    "fields": [{"name": "input", "type": "text", "label": "Input"}]
  }
}
```

## Documentation

- `CLAUDE-SIMPLE.md` - Detailed setup guide
- `CAPROVER_DEPLOYMENT_GUIDE.md` - Basic deployment steps
- `CAPROVER_DEPLOYMENT_COMPLETE_GUIDE.md` - Complete setup