#! /bin/bash

# Twice the number of cores plus one
let NUM_WORKERS="2*`nproc`+1"

export DJANGO_SETTINGS_MODULE=regapp.config.settings

python manage.py collectstatic --noinput

if [ "$1" = "--devel" ]; then
        uvicorn regapp.config.asgi:application --reload --reload-include=*.j2 --host=0.0.0.0 --port=8123
else
        gunicorn --env DJANGO_SETTINGS_MODULE=regapp.config.settings -k uvicorn.workers.UvicornWorker --timeout 120 --workers $NUM_WORKERS --no-sendfile --bind=0.0.0.0:8123 regapp.config.asgi:application
fi
