#!/bin/bash

# Simple Application Deployment Script for Book Review Application
# This script assumes PostgreSQL and the database are already set up

# Colors
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NC="\033[0m" # No Color

echo -e "${YELLOW}===== Deploying Book Review Application =====${NC}"

# Database settings
DB_NAME="book_review"
DB_USER="book_user"
DB_PASSWORD="secure_password"

# 1. Set environment variables
export PYTHONPATH=$(pwd)
export DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"

# 2. Run database migrations
echo -e "\n${YELLOW}Running database migrations...${NC}"
poetry run alembic upgrade head
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database migrations completed successfully${NC}"
else
    echo -e "${RED}❌ Database migrations failed${NC}"
    exit 1
fi

# 3. Load sample data
echo -e "\n${YELLOW}Loading sample data...${NC}"
poetry run python scripts/populate_books.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Sample data loaded successfully${NC}"
else
    echo -e "${YELLOW}⚠️ Sample data loading might have had issues${NC}"
    echo "This could be because data already exists, continuing..."
fi

# 4. Start the application
echo -e "\n${YELLOW}Starting the application...${NC}"
mkdir -p logs

# Kill any existing application processes
pkill -f "uvicorn app.main:app" || true

# Start the application
nohup poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info > logs/server.log 2>&1 &

# Get the PID of the application
APP_PID=$!
sleep 3

# Check if application is running
if ps -p $APP_PID > /dev/null; then
    echo -e "${GREEN}✅ Application started successfully (PID: $APP_PID)${NC}"
else
    echo -e "${RED}❌ Application failed to start${NC}"
    echo "Check logs for details:"
    tail -n 20 logs/server.log
    exit 1
fi

# Display application access information
INSTANCE_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "YOUR_EC2_IP")

echo -e "\n${GREEN}===== Application Deployment Complete =====${NC}"
echo ""
echo "Application access details:"
echo -e "  API URL: ${GREEN}http://$INSTANCE_IP:8000${NC}"
echo -e "  API Documentation: ${GREEN}http://$INSTANCE_IP:8000/docs${NC}"
echo ""
echo "To check application logs:"
echo "  tail -f logs/server.log"
echo ""
echo "To stop the application:"
echo "  pkill -f 'uvicorn app.main:app'"
