#!/usr/bin/env bash

# 1. Run migrations
echo "Running database migrations..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

# 2. Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear
