#!/bin/bash

# Script to run the application using Poetry on EC2
# This script starts the FastAPI application using Poetry and Uvicorn

# Set environment variables and configuration
export PYTHONPATH="$(pwd)"
APP_PORT=8000
LOG_LEVEL="info"  # Options: debug, info, warning, error, critical

# Kill any existing application instances to avoid port conflicts
echo "Stopping any existing application instances..."
pkill -f "uvicorn app.main:app" || true

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install it first."
    echo "Run: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Ensure all dependencies are installed
echo "Installing dependencies with Poetry..."
poetry install --no-root

# Verify if the database is running and accessible
echo "Verifying database connection..."
poetry run python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        dbname='book_review',
        user='book_user',
        password='secure_password',
        host='localhost',
        port=5432
    )
    print('✅ Database connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    print('Checking if PostgreSQL is running and accessible...')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database connection failed. Please ensure PostgreSQL is running."
    echo "Try: sudo systemctl restart postgresql"
    echo "Or setup database with: sudo -u postgres psql -c \"CREATE DATABASE book_reviews; CREATE USER book_user WITH PASSWORD 'book_password'; GRANT ALL PRIVILEGES ON DATABASE book_reviews TO book_user;\""
    exit 1
fi

# Run migrations to ensure database schema is up to date
echo "Running database migrations..."
poetry run alembic upgrade head

# Start the application
echo "Starting the application with Poetry and Uvicorn..."
echo "The application will be available at: http://localhost:${APP_PORT}"
echo "Press Ctrl+C to stop the application"

# Run the application in production mode on EC2

# Create log directory if it doesn't exist
mkdir -p logs

echo "Starting application in production mode on EC2..."

# Run with nohup to keep running after SSH session closes
nohup poetry run uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT} --log-level ${LOG_LEVEL} > logs/server.log 2>&1 &

APP_PID=$!
echo "Application started with PID: ${APP_PID}"

# Print access information with EC2 public IP
INSTANCE_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "YOUR_EC2_PUBLIC_IP")
echo ""
echo "=================================================="
echo "Application is running on EC2 instance"
echo "Access the API docs at: http://${INSTANCE_IP}:${APP_PORT}/docs"
echo "Access the API at: http://${INSTANCE_IP}:${APP_PORT}/api/v1/"
echo "=================================================="
echo ""
echo "To stop the application, run: pkill -f 'uvicorn app.main:app'"
echo "To view logs: tail -f server.log"
