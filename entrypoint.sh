#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
# Ensure STATIC_ROOT is configured in settings.py (e.g., 'static_root')
python manage.py collectstatic --noinput --clear

# Start Gunicorn server
# Adjust the number of workers based on your VPS resources (e.g., 2 * CPU cores + 1)
# --bind 0.0.0.0:8000 - Listen on all interfaces, port 8000
# config.wsgi:application - Path to your Django WSGI application
echo "Starting Gunicorn server..."
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 # Example with 3 workers 