#!/bin/bash
# Dokploy startup script

set -e  # Exit on any error

echo "🚀 Starting Quantum Tasks AI on Dokploy"
echo "======================================="

# Run database migrations
echo "📄 Running database migrations..."
python manage.py migrate --noinput

# Create cache table if needed
echo "🗄️ Ensuring cache table exists..."
python manage.py createcachetable || true

# Check if we can access the database
echo "🔍 Testing database connection..."
python manage.py check --database default

# Start the application
echo "🌐 Starting gunicorn server on port 3000..."
echo "Health check endpoint: /health/"
echo "======================================="

exec gunicorn netcop_hub.wsgi:application \
    --bind 0.0.0.0:3000 \
    --workers 2 \
    --timeout 120 \
    --max-requests 1000 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile -
