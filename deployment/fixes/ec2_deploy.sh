#!/bin/bash

# EC2 PostgreSQL Deployment Script
# This script handles special considerations for PostgreSQL on EC2

# Exit on error
set -e

# Colors for output
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NC="\033[0m"  # No Color

# Print step header
print_step() {
    echo ""
    echo -e "${YELLOW}==== $1 ====${NC}"
    echo ""
}

print_step "FIXING POSTGRESQL SOCKET ISSUES"
sudo bash deployment/fixes/fix_postgres_socket.sh

print_step "VERIFYING POSTGRESQL SERVICE"
if sudo systemctl is-active postgresql &>/dev/null; then
    echo -e "${GREEN}✅ PostgreSQL service is running${NC}"
else
    echo -e "${RED}❌ PostgreSQL service is not running${NC}"
    echo "Starting PostgreSQL service..."
    sudo systemctl start postgresql
    sleep 2
    if ! sudo systemctl is-active postgresql &>/dev/null; then
        echo -e "${RED}❌ Failed to start PostgreSQL service${NC}"
        exit 1
    fi
fi

print_step "TESTING DIRECT POSTGRESQL CONNECTION"
echo "Attempting direct PostgreSQL connection..."
if sudo -u postgres psql -c "SELECT 'PostgreSQL is working';" &>/dev/null; then
    echo -e "${GREEN}✅ PostgreSQL connection successful${NC}"
else
    echo -e "${RED}❌ Failed to connect to PostgreSQL${NC}"
    echo "This may indicate permission issues or configuration problems."
    exit 1
fi

print_step "CREATING APPLICATION DATABASE"
# Create book_review database
echo "Creating database if it doesn't exist..."
if ! sudo -u postgres psql -l | grep -q "book_review"; then
    sudo -u postgres psql -c "CREATE DATABASE book_review;"
    echo -e "${GREEN}✅ Database created${NC}"
else
    echo -e "${GREEN}✅ Database already exists${NC}"
fi

print_step "CREATING APPLICATION USER"
# Create application user
echo "Creating application user..."
if ! sudo -u postgres psql -c "\du" | grep -q "book_user"; then
    sudo -u postgres psql -c "CREATE USER book_user WITH PASSWORD 'secure_password';"
    echo -e "${GREEN}✅ User created${NC}"
else
    sudo -u postgres psql -c "ALTER USER book_user WITH PASSWORD 'secure_password';"
    echo -e "${GREEN}✅ User password updated${NC}"
fi

print_step "GRANTING DATABASE PRIVILEGES"
# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE book_review TO book_user;"
sudo -u postgres psql -d book_review -c "GRANT ALL ON SCHEMA public TO book_user;"
echo -e "${GREEN}✅ Privileges granted${NC}"

print_step "SETTING UP APPLICATION"
# Install Poetry if needed
if ! command -v poetry &>/dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    source $HOME/.poetry/env
fi

# Install dependencies
echo "Installing dependencies..."
poetry install --no-root

# Set up environment
echo "Setting up environment..."
export PYTHONPATH=$(pwd)
export DATABASE_URL="postgresql://book_user:secure_password@localhost:5432/book_review"

print_step "RUNNING DATABASE MIGRATIONS"
# Run migrations
poetry run alembic upgrade head
echo -e "${GREEN}✅ Database migrations complete${NC}"

print_step "LOADING SAMPLE DATA"
# Load sample data
poetry run python scripts/populate_books.py
echo -e "${GREEN}✅ Sample data loaded${NC}"

print_step "STARTING APPLICATION"
# Start the application
mkdir -p logs
echo "Starting the application..."
pkill -f "uvicorn app.main:app" || true
nohup poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info > logs/server.log 2>&1 &
APP_PID=$!
echo -e "${GREEN}✅ Application started with PID: $APP_PID${NC}"

# Get instance IP
INSTANCE_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "YOUR_EC2_IP")
echo ""
echo -e "The application is running at: ${GREEN}http://$INSTANCE_IP:8000${NC}"
echo -e "API Documentation: ${GREEN}http://$INSTANCE_IP:8000/docs${NC}"
echo ""
echo "To stop the application: pkill -f 'uvicorn app.main:app'"
echo "To view logs: tail -f logs/server.log"
