#!/usr/bin/env bash
# Start script for Render deployment

set -o errexit  # exit on error

echo "Running database migrations..."
python manage.py migrate

echo "Creating admin user if needed..."
python manage.py reset_admin --password=RenderTemp123! || true

echo "Starting gunicorn server..."
exec gunicorn netcop_hub.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 60