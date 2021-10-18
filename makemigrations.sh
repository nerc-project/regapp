#! /bin/bash

REGAPP_REPO=ghcr.io
PROJECT_LOCATION=/home/jculbert/development/nerc
REGAPP_IMAGE=$REGAPP_REPO/nerc-project/regapp:master

docker login $REGAPP_REPO
docker pull $REGAPP_IMAGE

docker run --rm \
-e "PYTHONPATH=/code" \
-e "DJANGO_SECRET_KEY=dummy" \
-e "REGAPP_EMAIL_HOST=dummy" \
-e "REGAPP_EMAIL_USE_TLS=dummy" \
-e "REGAPP_EMAIL_PORT=0" \
-e "REGAPP_EMAIL_HOST_USER=dummy" \
-e "REGAPP_EMAIL_HOST_PASSWORD=dummy" \
-e "REGAPP_REGAPP_CLIENT_ID=dummy" \
-e "REGAPP_REGAPP_CLIENT_SECRET=dummy" \
-v $PROJECT_LOCATION:/code $REGAPP_IMAGE \
sh -c "python regapp/manage.py makemigrations"
