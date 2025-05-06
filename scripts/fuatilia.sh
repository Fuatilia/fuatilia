#!/bin/bash
# Run dev command in background to allow other commands to follow
python app/manage.py makemigrations
python app/manage.py migrate
python app/manage.py runserver 0.0.0.0:8000 &
sleep 10
cd app
celery -A settings worker --loglevel=debug --concurrency 1
