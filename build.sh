#!/usr/bin/env bash

# 1. Install Python dependencies using the global pip3 executable
echo "Installing dependencies from requirements.txt..."
pip3 install -r requirements.txt

# 2. Run migrations
echo "Running database migrations..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

# 3. Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear
