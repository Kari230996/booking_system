#!/bin/bash
set -e

# Wait for postgres
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "Waiting for postgres..."
  sleep 2
done

echo "PostgreSQL started"

# Run migrations
python manage.py migrate

# Start server
exec "$@"
