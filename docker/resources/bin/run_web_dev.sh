#!/bin/sh

# wait for PSQL server to start
sleep 10

# prepare init migration
su -m myuser -c "python manage.py makemigrations cards"
su -m myuser -c "python manage.py makemigrations sets"
su -m myuser -c "python manage.py makemigrations stats"
su -m myuser -c "python manage.py makemigrations tournaments"
# migrate db, so we have the latest db schema
su -m myuser -c "python manage.py migrate"
# start development server on public ip interface, on port 8000
su -m myuser -c "python manage.py runserver 0.0.0.0:8000 --settings=config.settings.local"