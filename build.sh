#!/usr/bin/env bash
set -o errexit

# Install Python 3.12 if needed (Render will use runtime.txt)
echo "Using Python version from runtime.txt..."

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate