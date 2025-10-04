#!/bin/bash
set -e

echo "Starting database migration fix..."

# Go to the project root directory
cd "$(dirname "$0")/../.." || exit 1
echo "Working directory: $(pwd)"

# Make sure environment variables are set
if [ ! -f .env ]; then
    echo "Creating .env file with database URL"
    echo "export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/book_review" > .env
fi

# Source the environment variables
source .env
echo "Environment variables loaded"

# Set PYTHONPATH
export PYTHONPATH=$PWD
echo "PYTHONPATH set to $PYTHONPATH"

# Try to clean up alembic_version table if it exists
echo "Attempting to clean alembic_version table..."
sudo -u postgres /usr/local/pgsql/bin/psql -d book_review -c "DROP TABLE IF EXISTS alembic_version;" || echo "Could not drop alembic_version table (it may not exist)"

# Run the alembic migrations
echo "Running database migrations..."
alembic upgrade head

# Check if the migrations were successful
if [ $? -eq 0 ]; then
    echo "Database migrations completed successfully!"
    
    # Check if the necessary tables were created
    TABLES=$(sudo -u postgres /usr/local/pgsql/bin/psql -d book_review -c "\dt" -t | wc -l)
    if [ "$TABLES" -gt 0 ]; then
        echo "Database tables were created successfully!"
    else
        echo "Warning: No tables were created in the database."
    fi
else
    echo "Error: Database migrations failed."
    exit 1
fi

echo "Migration fix script completed successfully!"
