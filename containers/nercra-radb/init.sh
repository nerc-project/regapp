#! /bin/sh
export PGPASSWORD=$POSTGRES_PASSWORD
psql --username=postgres -c "create user $DJANGO_DB_USER with password '$DJANGO_DB_PASSWORD'"
psql --username=postgres -c "create database $DJANGO_DB_NAME with owner $DJANGO_DB_USER"
