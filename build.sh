#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "==> Installing project dependencies..."
pip install -r requirements.txt

echo "==> Collecting static assets with WhiteNoise..."
python manage.py collectstatic --no-input

echo "==> Running database migrations..."
python manage.py migrate

echo "==> Build complete for CreatorSpark!"
