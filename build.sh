#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "==> Upgrading pip..."
pip install --upgrade pip

echo "==> Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "==> Collecting static assets for WhiteNoise..."
python manage.py collectstatic --noinput

echo "==> Applying database migrations to Supabase PostgreSQL..."
python manage.py migrate --noinput

echo "==> AnumatiSetu Build Complete!"
