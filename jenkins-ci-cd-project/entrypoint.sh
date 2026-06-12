#!/bin/sh

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate --no-input

# Collect static files
echo "Collect static files"
python manage.py collectstatic --no-input

# Start server
echo "Starting server"
exec "$@"
