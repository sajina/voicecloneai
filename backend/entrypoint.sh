#!/bin/sh

set -e

echo "Running migrations..."
python manage.py migrate

echo "Ensuring admin user exists..."
python manage.py ensure_admin

echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "WARNING: collectstatic failed, continuing..."

echo "Starting Gunicorn on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 2 --timeout 120
