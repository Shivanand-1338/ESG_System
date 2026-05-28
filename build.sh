#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Build React frontend (if Node.js is available)
if command -v node &> /dev/null; then
    echo "Node.js found, building frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
else
    echo "Node.js not found, skipping frontend build"
fi

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create default superuser if it doesn't exist
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@breatheesg.com', 'admin123')
    print('Created default admin user')
else:
    print('Admin user already exists')
"
