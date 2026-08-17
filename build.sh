#!/usr/bin/env bash
set -o errexit

# Install Python 3.12 manually
echo "Installing Python 3.12..."
apt-get update
apt-get install -y python3.12 python3.12-venv python3.12-dev

# Create a virtual environment with Python 3.12
python3.12 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate