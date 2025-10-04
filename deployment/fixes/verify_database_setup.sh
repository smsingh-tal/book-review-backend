#!/bin/bash

# This script verifies that the database is properly set up
# and displays connection information

# Set default values
DB_NAME="book_review"
DB_USER="book_user"
DB_PASSWORD="secure_password"

echo "Verifying database setup for the book review application..."

# Check if PostgreSQL is running
if sudo systemctl is-active postgresql &>/dev/null; then
    echo "✅ PostgreSQL service is running"
else
    echo "❌ PostgreSQL service is not running"
    echo "Starting PostgreSQL service..."
    sudo systemctl start postgresql
    if sudo systemctl is-active postgresql &>/dev/null; then
        echo "✅ PostgreSQL service started successfully"
    else
        echo "❌ Failed to start PostgreSQL service"
        exit 1
    fi
fi

# Check if database exists
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "✅ Database '$DB_NAME' exists"
else
    echo "❌ Database '$DB_NAME' does not exist"
    exit 1
fi

# Check if user exists
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo "✅ User '$DB_USER' exists"
else
    echo "❌ User '$DB_USER' does not exist"
    exit 1
fi

# Check if user can connect to database
echo "Testing database connection..."
if PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME -c "SELECT 'Connection successful' AS status;" &>/dev/null; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
    echo "This may be due to authentication configuration issues."
    exit 1
fi

# Display database connection information
echo ""
echo "======================= DATABASE INFO ======================="
echo "Database Name: $DB_NAME"
echo "Database User: $DB_USER"
echo "Database Password: $DB_PASSWORD"
echo ""
echo "Connection URL: postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo "============================================================"
echo ""
echo "✅ Database is properly set up and ready to use"
