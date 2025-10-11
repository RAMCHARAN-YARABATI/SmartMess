#!/usr/bin/env bash

# 1. Install Python dependencies
echo "Installing dependencies from requirements.txt..."
python3.9 -m pip install -r requirements.txt

# 2. Run migrations
echo "Running database migrations..."
python3.9 manage.py makemigrations --noinput
python3.9 manage.py migrate --noinput

# 3. Collect static files
echo "Collecting static files..."
python3.9 manage.py collectstatic --noinput --clear
