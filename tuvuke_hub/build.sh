#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "Running database migrations..."
python manage.py migrate

echo "Creating cache table..."
python manage.py createcachetable

echo "Loading initial data..."
# Uncomment these if you have fixture files
# python manage.py loaddata counties.json
# python manage.py loaddata initial_data.json

echo "Build completed successfully!"
