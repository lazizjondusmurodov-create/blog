#!/usr/bin/env bash
# Serverda build paytida ishlaydigan buyruqlar (Render, Railway va h.k.)
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
