#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed database (TEMPORARY: Runs seed_ems to create test users)
python manage.py seed_ems

# Collect static files
python manage.py collectstatic --no-input
