#!/bin/bash
# Dokploy startup script

set -e  # Exit on any error

echo "🚀 Starting Quantum Tasks AI on Dokploy"
echo "======================================="

# Run database migrations
echo "📄 Running database migrations..."
DJANGO_SETTINGS_MODULE=production_https_settings python manage.py migrate --noinput

# Create cache table if needed
echo "🗄️ Ensuring cache table exists..."
DJANGO_SETTINGS_MODULE=production_https_settings python manage.py createcachetable || true

# Check if we can access the database
echo "🔍 Testing database connection..."
DJANGO_SETTINGS_MODULE=production_https_settings python manage.py check --database default

# Start the application
echo "🌐 Starting gunicorn server on port 3000..."
echo "Health check endpoint: /health/"
echo "🔒 HTTPS enabled with SSL redirect"
echo "======================================="

DJANGO_SETTINGS_MODULE=production_https_settings exec gunicorn netcop_hub.wsgi:application
    --bind 0.0.0.0:3000 \
    --workers 2 \
    --timeout 120 \
    --max-requests 1000 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile -
