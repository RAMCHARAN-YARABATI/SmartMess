#!/usr/bin/env bash

# 🚨 CRITICAL FIX: Run installation inside the script to ensure environment is loaded

# 1. Install dependencies using the generic pip3 command
echo "Installing dependencies from requirements.txt..."
# Use python3 -m pip to ensure the right path, as simple pip3 sometimes fails
python3 -m pip install -r requirements.txt

# 2. Run migrations
echo "Running database migrations..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

# 3. Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear
