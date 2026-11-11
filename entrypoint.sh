#!/bin/sh
set -e
cd /app
export PYTHONPATH=/app

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python scripts/ensure_superuser.py

exec gunicorn recetario.wsgi:application --bind 0.0.0.0:8000
