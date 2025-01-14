#!/bin/sh
set -e

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! PGPASSWORD=postgres psql -h db -U postgres -d flask_celery -c '\q'; do
  echo >&2 "Postgres is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL started"

# Apply database migrations
echo "Applying database migrations..."
alembic upgrade head || {
    echo "Failed to apply database migrations"
    exit 1
}
echo "Database migrations completed successfully"

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn -b :5000 \
    --access-logfile - \
    --error-logfile - \
    --workers 4 \
    --timeout 120 \
    main:app