#!/bin/bash

# Simple Database Setup Script for Book Review Application
# This script assumes PostgreSQL is already properly configured

# Colors
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NC="\033[0m" # No Color

echo -e "${YELLOW}===== Setting up Book Review Database =====${NC}"

# Database settings
DB_NAME="book_review"
DB_USER="book_user"
DB_PASSWORD="secure_password"

# 1. Create database
echo -e "\n${YELLOW}Creating database...${NC}"
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
    echo -e "${GREEN}✅ Database '$DB_NAME' already exists${NC}"
else
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Database '$DB_NAME' created successfully${NC}"
    else
        echo -e "${RED}❌ Failed to create database${NC}"
        exit 1
    fi
fi

# 2. Create user
echo -e "\n${YELLOW}Creating database user...${NC}"
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo -e "${GREEN}✅ User '$DB_USER' already exists${NC}"
    echo "Updating password..."
    sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
else
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ User '$DB_USER' created successfully${NC}"
    else
        echo -e "${RED}❌ Failed to create user${NC}"
        exit 1
    fi
fi

# 3. Grant privileges
echo -e "\n${YELLOW}Granting privileges...${NC}"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
echo -e "${GREEN}✅ Privileges granted${NC}"

# 4. Test connection
echo -e "\n${YELLOW}Testing connection...${NC}"
export PGPASSWORD="$DB_PASSWORD"
if psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "SELECT 'Connection test successful';" &>/dev/null; then
    echo -e "${GREEN}✅ Connection test successful${NC}"
else
    echo -e "${YELLOW}⚠️ Connection test with TCP failed, trying with local socket...${NC}"
    if psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT 'Connection test successful';" &>/dev/null; then
        echo -e "${GREEN}✅ Connection test successful using local socket${NC}"
    else
        echo -e "${RED}❌ Connection test failed${NC}"
        echo "This may be due to pg_hba.conf configuration issues."
    fi
fi

echo -e "\n${GREEN}===== Database Setup Complete =====${NC}"
echo ""
echo "Database connection details:"
echo "  Name: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo "  Connection URL: postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
