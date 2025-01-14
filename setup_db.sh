
#!/bin/bash
set -e

# Wait for PostgreSQL to be available
until pg_isready -h db -p 5432 -U postgres; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Run the Flask migrations
flask db upgrade

# Start the Flask application
exec ./boot.sh