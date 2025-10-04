#!/bin/bash

# Complete setup script for book-review-backend application on EC2
# This script will:
# 1. Set up and verify PostgreSQL
# 2. Create the application database and user
# 3. Run database migrations
# 4. Load sample data
# 5. Start the application

# Set colored output
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NC="\033[0m" # No Color

# Print section header
print_header() {
    echo ""
    echo -e "${YELLOW}=======================================================${NC}"
    echo -e "${YELLOW} $1 ${NC}"
    echo -e "${YELLOW}=======================================================${NC}"
    echo ""
}

# Check if a command succeeded
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
        exit 1
    fi
}

# 1. Check PostgreSQL Service
print_header "CHECKING POSTGRESQL SERVICE"

sudo systemctl is-active postgresql &>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PostgreSQL service is running${NC}"
else
    echo -e "${YELLOW}⚠️ PostgreSQL service is not running. Attempting to start...${NC}"
    sudo systemctl start postgresql
    check_status "Starting PostgreSQL service"
fi

# 2. Set up the Application Database
print_header "SETTING UP APPLICATION DATABASE"

echo "Running database setup script..."
sudo bash deployment/fixes/setup_application_database.sh
check_status "Setting up application database"

# 3. Verify Database Setup
print_header "VERIFYING DATABASE SETUP"

bash deployment/fixes/verify_database_setup.sh
check_status "Database verification"

# 4. Install Application Dependencies
print_header "INSTALLING APPLICATION DEPENDENCIES"

# Check if Poetry is installed
if ! command -v poetry &>/dev/null; then
    echo -e "${YELLOW}⚠️ Poetry not found. Installing Poetry...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
    check_status "Installing Poetry"
fi

# Install dependencies
poetry install --no-root
check_status "Installing application dependencies"

# 5. Run Database Migrations
print_header "RUNNING DATABASE MIGRATIONS"

export PYTHONPATH=$(pwd)
poetry run alembic upgrade head
check_status "Running database migrations"

# 6. Load Sample Data
print_header "LOADING SAMPLE DATA"

echo "Loading books data..."
poetry run python scripts/populate_books.py
check_status "Loading sample data"

# 7. Start the Application
print_header "STARTING THE APPLICATION"

echo "Starting the application..."
# First kill any running instances
pkill -f "uvicorn app.main:app" || true

# Start the application in the background
nohup poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info > logs/server.log 2>&1 &

APP_PID=$!
sleep 2

# Check if application is running
if ps -p $APP_PID > /dev/null; then
    echo -e "${GREEN}✅ Application started successfully with PID: ${APP_PID}${NC}"
else
    echo -e "${RED}❌ Failed to start the application${NC}"
    echo "Check logs in logs/server.log for details"
    exit 1
fi

# Get instance IP
INSTANCE_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "YOUR_EC2_IP")

# Display application access information
print_header "APPLICATION INFORMATION"

echo -e "API is running at: ${GREEN}http://${INSTANCE_IP}:8000${NC}"
echo -e "API Documentation: ${GREEN}http://${INSTANCE_IP}:8000/docs${NC}"
echo ""
echo "To stop the application: pkill -f 'uvicorn app.main:app'"
echo "To view logs: tail -f logs/server.log"
echo ""
echo -e "${GREEN}Setup completed successfully!${NC}"
