Bash

#!/bin/bash

# 1. Install Python dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# 2. Run migrations
echo "Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# 3. Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear
