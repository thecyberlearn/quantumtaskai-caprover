#!/usr/bin/env python3
"""
Environment Variable Generator for Quantum Tasks AI Dokploy + Neon Deployment
Generates secure values for environment variables with Neon database integration.
"""

import secrets
import string
import os

def generate_secret_key(length=50):
    """Generate a secure Django SECRET_KEY"""
    characters = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(characters) for _ in range(length))

def main():
    print("🔐 Quantum Tasks AI - Environment Variable Generator (Neon Edition)")
    print("=" * 70)
    print()
    
    print("📋 Copy these values to your Dokploy environment variables:")
    print()
    
    # Generate secure values
    secret_key = generate_secret_key()
    
    # Core Django settings
    print("🔑 ESSENTIAL VARIABLES (Required):")
    print(f"SECRET_KEY={secret_key}")
    print("DEBUG=false")
    print("ALLOWED_HOSTS=ai.quantumtaskai.com,*.quantumtaskai.com,quantumtaskai.com")
    print("CSRF_TRUSTED_ORIGINS=https://ai.quantumtaskai.com,https://quantumtaskai.com")
    print()
    
    # Neon database settings
    print("🗄️ NEON DATABASE VARIABLE:")
    print("NEON_DATABASE_URL=postgresql://your_username:your_password@your_endpoint.neon.tech/quantumtasks_ai?sslmode=require")
    print("# ☝️  Get this from your Neon dashboard: Database → Connection Details → Connection String")
    print()
    
    # Email settings (user needs to fill these)
    print("📧 EMAIL CONFIGURATION (Fill in your values):")
    print("EMAIL_HOST_USER=your-email@gmail.com")
    print("EMAIL_HOST_PASSWORD=your-gmail-app-password")
    print("DEFAULT_FROM_EMAIL=Quantum Tasks AI <noreply@ai.quantumtaskai.com>")
    print("REQUIRE_EMAIL_VERIFICATION=true")
    print()
    
    # Security settings
    print("🔒 SECURITY SETTINGS:")
    print("SECURE_SSL_REDIRECT=true")
    print("SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https")
    print("COMPOSE_PROJECT_NAME=quantumtasks-ai")
    print()
    
    print("💡 OPTIONAL VARIABLES (Configure as needed):")
    print("# Payment Processing")
    print("STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key_here")
    print("STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here")
    print()
    print("# AI APIs")
    print("OPENAI_API_KEY=sk-your_openai_api_key_here")
    print("GROQ_API_KEY=gsk_your_groq_api_key_here")
    print("SERPAPI_API_KEY=your_serpapi_key_here")
    print("OPENWEATHER_API_KEY=your_weather_api_key_here")
    print()
    
    print("🎯 HOW TO GET YOUR NEON DATABASE URL:")
    print("1. Go to https://neon.tech and login to your account")
    print("2. Select your project (or create one)")
    print("3. Go to 'Dashboard' → 'Connection Details'")
    print("4. Copy the 'Connection String' (it looks like the format above)")
    print("5. Make sure the database name matches 'quantumtasks_ai' or update accordingly")
    print()
    
    # Save to file option
    save_to_file = input("💾 Save these variables to .env.neon file? (y/N): ").lower()
    if save_to_file == 'y':
        with open('.env.neon', 'w') as f:
            f.write("# Generated Environment Variables for Dokploy + Neon\n")
            f.write("# Generated on: " + str(os.popen('date').read().strip()) + "\n\n")
            f.write("# ESSENTIAL VARIABLES\n")
            f.write(f"SECRET_KEY={secret_key}\n")
            f.write("DEBUG=false\n")
            f.write("ALLOWED_HOSTS=ai.quantumtaskai.com,*.quantumtaskai.com,quantumtaskai.com\n")
            f.write("CSRF_TRUSTED_ORIGINS=https://ai.quantumtaskai.com,https://quantumtaskai.com\n\n")
            f.write("# NEON DATABASE VARIABLE\n")
            f.write("NEON_DATABASE_URL=postgresql://your_username:your_password@your_endpoint.neon.tech/quantumtasks_ai?sslmode=require\n")
            f.write("# Get this from Neon dashboard: Database → Connection Details\n\n")
            f.write("# EMAIL CONFIGURATION (Fill in your values)\n")
            f.write("EMAIL_HOST_USER=your-email@gmail.com\n")
            f.write("EMAIL_HOST_PASSWORD=your-gmail-app-password\n")
            f.write("DEFAULT_FROM_EMAIL=Quantum Tasks AI <noreply@ai.quantumtaskai.com>\n")
            f.write("REQUIRE_EMAIL_VERIFICATION=true\n\n")
            f.write("# SECURITY SETTINGS\n")
            f.write("SECURE_SSL_REDIRECT=true\n")
            f.write("SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https\n")
            f.write("COMPOSE_PROJECT_NAME=quantumtasks-ai\n\n")
            f.write("# OPTIONAL VARIABLES (Configure as needed)\n")
            f.write("# STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key_here\n")
            f.write("# OPENAI_API_KEY=sk-your_openai_api_key_here\n")
            f.write("# GROQ_API_KEY=gsk_your_groq_api_key_here\n")
            f.write("# SERPAPI_API_KEY=your_serpapi_key_here\n")
            f.write("# OPENWEATHER_API_KEY=your_weather_api_key_here\n")
        print("✅ Variables saved to .env.neon")
        print("⚠️  Remember to:")
        print("   - Update NEON_DATABASE_URL with your actual Neon connection string")
        print("   - Update EMAIL_HOST_USER and EMAIL_HOST_PASSWORD")
    
    print()
    print("📝 Next Steps:")
    print("1. Get your Neon database connection string from neon.tech")
    print("2. Copy all variables to Dokploy environment settings")
    print("3. Update email settings with your Gmail app password")
    print("4. Add optional API keys as needed")
    print("5. Deploy your project in Dokploy!")
    print()
    print("🌐 Your site will be live at: https://ai.quantumtaskai.com")
    print("🗄️  Database: Neon Serverless PostgreSQL (no local DB container needed!)")

if __name__ == "__main__":
    main()
