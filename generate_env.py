#!/usr/bin/env python3
"""
Environment Variable Generator for Quantum Tasks AI Dokploy Deployment
Generates secure values for environment variables needed for deployment.
"""

import secrets
import string
import os

def generate_secret_key(length=50):
    """Generate a secure Django SECRET_KEY"""
    characters = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(characters) for _ in range(length))

def generate_password(length=24):
    """Generate a secure password"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def main():
    print("🔐 Quantum Tasks AI - Environment Variable Generator")
    print("=" * 60)
    print()
    
    print("📋 Copy these values to your Dokploy environment variables:")
    print()
    
    # Generate secure values
    secret_key = generate_secret_key()
    postgres_password = generate_password()
    
    # Core Django settings
    print("🔑 ESSENTIAL VARIABLES (Required):")
    print(f"SECRET_KEY={secret_key}")
    print("DEBUG=false")
    print("ALLOWED_HOSTS=ai.quantumtaskai.com,*.quantumtaskai.com,quantumtaskai.com")
    print("CSRF_TRUSTED_ORIGINS=https://ai.quantumtaskai.com,https://quantumtaskai.com")
    print()
    
    # Database settings
    print("🗄️ DATABASE VARIABLES:")
    print("POSTGRES_DB=quantumtasks_ai")
    print(f"POSTGRES_PASSWORD={postgres_password}")
    print(f"DATABASE_URL=postgresql://postgres:{postgres_password}@db:5432/quantumtasks_ai")
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
    
    # Save to file option
    save_to_file = input("💾 Save these variables to .env.production file? (y/N): ").lower()
    if save_to_file == 'y':
        with open('.env.production', 'w') as f:
            f.write("# Generated Environment Variables for Dokploy\n")
            f.write("# Generated on: " + str(os.popen('date').read().strip()) + "\n\n")
            f.write("# ESSENTIAL VARIABLES\n")
            f.write(f"SECRET_KEY={secret_key}\n")
            f.write("DEBUG=false\n")
            f.write("ALLOWED_HOSTS=ai.quantumtaskai.com,*.quantumtaskai.com,quantumtaskai.com\n")
            f.write("CSRF_TRUSTED_ORIGINS=https://ai.quantumtaskai.com,https://quantumtaskai.com\n\n")
            f.write("# DATABASE VARIABLES\n")
            f.write("POSTGRES_DB=quantumtasks_ai\n")
            f.write(f"POSTGRES_PASSWORD={postgres_password}\n")
            f.write(f"DATABASE_URL=postgresql://postgres:{postgres_password}@db:5432/quantumtasks_ai\n\n")
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
        print("✅ Variables saved to .env.production")
        print("⚠️  Remember to update EMAIL_HOST_USER and EMAIL_HOST_PASSWORD!")
    
    print()
    print("📝 Next Steps:")
    print("1. Copy the essential variables to Dokploy environment settings")
    print("2. Update email settings with your Gmail app password")
    print("3. Add optional API keys as needed")
    print("4. Deploy your project in Dokploy!")
    print()
    print("🌐 Your site will be live at: https://ai.quantumtaskai.com")

if __name__ == "__main__":
    main()
