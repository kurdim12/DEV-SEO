#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
# Note: Only run if DATABASE_URL is set (production)
if [ -n "$DATABASE_URL" ]; then
    echo "Running database migrations..."
    python -m alembic upgrade head
fi
