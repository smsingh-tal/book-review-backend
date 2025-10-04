#!/bin/bash
set -e

echo "================================"
echo "Book Review Backend Deployment"
echo "================================"

# Go to the project root directory
cd "$(dirname "$0")/../.." || exit 1
echo "Working directory: $(pwd)"

# Kill any running instances of the application
echo "Stopping any running application instances..."
pkill -f 'uvicorn app.main:app' || echo "No running instances found"

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

# Fix database migrations
echo "Fixing database migrations..."
bash deployment/fixes/fix_migrations.sh

# Populate the database
echo "Populating database..."
bash deployment/fixes/populate_database.sh

# Start the application
echo "Starting the application..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info > server.log 2>&1 &

# Check if the application started successfully
sleep 5
if pgrep -f 'uvicorn app.main:app' > /dev/null; then
    echo "Application started successfully!"
    echo "API is accessible at http://localhost:8000"
    echo "API documentation is available at http://localhost:8000/docs"
    echo "Logs are being written to server.log"
else
    echo "Error: Failed to start the application."
    echo "Check server.log for details."
    exit 1
fi

echo "Deployment completed successfully!"
