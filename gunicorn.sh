#!/bin/sh

#python manage.py migrate

gunicorn saasot.wsgi:application --bind 0.0.0.0:8000 --timeout 600





