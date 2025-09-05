FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV SECRET_KEY="build-time-dummy-key-change-in-production"

# Collect static files
RUN python manage.py collectstatic --noinput

# Create directory for media files
RUN mkdir -p /app/media

# Expose port
EXPOSE 80

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && gunicorn netcop_hub.wsgi:application --bind 0.0.0.0:80"]