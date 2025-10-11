#!/usr/bin/env bash

# Fix 1: Ensure the correct interpreter is used for pip
echo "Installing dependencies from requirements.txt..."
python3.9 -m pip install -r requirements.txt

# Fix 2 & 3: Ensure the correct interpreter is used for manage.py
echo "Running database migrations..."
python3.9 manage.py makemigrations --noinput
python3.9 manage.py migrate --noinput

# Fix 4: Ensure the correct interpreter is used for collectstatic
echo "Collecting static files..."
python3.9 manage.py collectstatic --noinput --clear
