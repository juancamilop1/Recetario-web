#!/bin/sh
set -e
cd /app
export PYTHONPATH=/app

if [ -n "$DJANGO_DB_PATH" ]; then
  mkdir -p "$(dirname "$DJANGO_DB_PATH")"
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python scripts/ensure_superuser.py
python scripts/seed_demo.py

exec gunicorn recetario.wsgi:application --bind 0.0.0.0:8000
