#!/usr/bin/env bash

# 1. Install Python dependencies using explicit paths and -m pip
# This format is the most robust way to ensure installation runs
echo "Installing dependencies from requirements.txt..."
/usr/bin/python3.9 -m pip install -r requirements.txt

# 2. Run migrations
echo "Running database migrations..."
/usr/bin/python3.9 manage.py makemigrations --noinput
/usr/bin/python3.9 manage.py migrate --noinput

# 3. Collect static files
echo "Collecting static files..."
/usr/bin/python3.9 manage.py collectstatic --noinput --clear
