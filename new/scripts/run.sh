#!/bin/sh
set -e

# Load environment variables from .env.sample file
if [ -f "./.env" ]; then
    echo "Loading environment variables from .env file"
    export $(grep -v '^#' ./.env.sample | xargs)
fi

python manage.py collectstatic --noinput
python manage.py migrate
gunicorn -b :8000 --chdir /app backend.wsgi:application
