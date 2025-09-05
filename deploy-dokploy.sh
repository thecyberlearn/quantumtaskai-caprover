#!/bin/bash
# Deployment helper script for Dokploy
# This script helps configure environment variables before deployment

set -e

echo "🚀 Dokploy Deployment Configuration Helper"
echo "=========================================="

# Get domain from user
read -p "Enter your domain (e.g., quamtumtaskai.netcoptech.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo "❌ Domain is required"
    exit 1
fi

# Generate secret key if not provided
if [ -z "$SECRET_KEY" ]; then
    echo "🔑 Generating SECRET_KEY..."
    SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
fi

# Set default environment variables
export DOMAIN="$DOMAIN"
export SECRET_KEY="$SECRET_KEY"
export DEBUG="false"
export ALLOWED_HOSTS="$DOMAIN,*"
export CSRF_TRUSTED_ORIGINS="https://$DOMAIN,http://$DOMAIN"
export SECURE_SSL_REDIRECT="false"
export SECURE_PROXY_SSL_HEADER="HTTP_X_FORWARDED_PROTO,https"
export DOKPLOY_PROJECT_NAME="quantum-tasks-ai"
export PYTHONUNBUFFERED="1"

echo "✅ Configuration complete:"
echo "   - Domain: $DOMAIN"
echo "   - SECRET_KEY: ${SECRET_KEY:0:20}..."
echo "   - ALLOWED_HOSTS: $ALLOWED_HOSTS" 
echo "   - SSL Redirect: $SECURE_SSL_REDIRECT"

echo ""
echo "📋 Environment variables to set in Dokploy:"
echo "DOMAIN=$DOMAIN"
echo "SECRET_KEY=$SECRET_KEY"
echo "DEBUG=false"
echo "ALLOWED_HOSTS=$ALLOWED_HOSTS"
echo "CSRF_TRUSTED_ORIGINS=$CSRF_TRUSTED_ORIGINS"
echo "SECURE_SSL_REDIRECT=false"
echo "SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https"
echo "DOKPLOY_PROJECT_NAME=quantum-tasks-ai"
echo "PYTHONUNBUFFERED=1"

echo ""
echo "🔄 After setting these variables in Dokploy, trigger a redeploy."
echo "🌐 Your app should be accessible at: https://$DOMAIN"
