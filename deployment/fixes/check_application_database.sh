#!/bin/bash

# Script to verify if the application database is created
# Usage: ./check_application_database.sh [database_name] [username]

# Default values
DB_NAME="${1:-book_reviews}"
DB_USER="${2:-book_user}"

echo "Checking for application database: $DB_NAME and user: $DB_USER"

# Check if PostgreSQL is running first
if ! systemctl is-active --quiet postgresql; then
    echo "❌ PostgreSQL service is not running. Please start it first."
    exit 1
fi

# Check if psql command is available
if ! command -v psql &> /dev/null; then
    echo "❌ psql command not found. Please install PostgreSQL client tools."
    exit 1
fi

# Function to run psql commands safely
run_psql_command() {
    sudo -u postgres psql -c "$1" 2>/dev/null
}

# Check if database exists
echo "Checking if database '$DB_NAME' exists..."
if run_psql_command "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q "1 row"; then
    echo "✅ Database '$DB_NAME' exists."
    DB_EXISTS=true
else
    echo "❌ Database '$DB_NAME' does not exist."
    DB_EXISTS=false
fi

# Check if user exists
echo "Checking if user '$DB_USER' exists..."
if run_psql_command "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q "1 row"; then
    echo "✅ User '$DB_USER' exists."
    USER_EXISTS=true
else
    echo "❌ User '$DB_USER' does not exist."
    USER_EXISTS=false
fi

# If both database and user exist, check user permissions on database
if [ "$DB_EXISTS" = true ] && [ "$USER_EXISTS" = true ]; then
    echo "Checking user permissions on database..."
    if run_psql_command "SELECT has_database_privilege('$DB_USER', '$DB_NAME', 'CONNECT')" | grep -q "t"; then
        echo "✅ User '$DB_USER' has connection privileges to database '$DB_NAME'."
    else
        echo "❌ User '$DB_USER' does not have connection privileges to database '$DB_NAME'."
    fi
    
    # Check if the user can create tables in the database
    if run_psql_command "SELECT has_database_privilege('$DB_USER', '$DB_NAME', 'CREATE')" | grep -q "t"; then
        echo "✅ User '$DB_USER' has CREATE privileges on database '$DB_NAME'."
    else
        echo "❌ User '$DB_USER' does not have CREATE privileges on database '$DB_NAME'."
    fi
    
    # Optional: Check for specific tables in the database
    echo "Checking for tables in the database..."
    TABLE_COUNT=$(sudo -u postgres psql -d "$DB_NAME" -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'" -t | tr -d ' ')
    echo "✅ Found $TABLE_COUNT tables in database '$DB_NAME'."
    
    # List some tables (if any)
    if [ "$TABLE_COUNT" -gt 0 ]; then
        echo "Sample tables in database:"
        sudo -u postgres psql -d "$DB_NAME" -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 5" -t
    fi
fi

# Summary
echo ""
echo "Database verification summary:"
if [ "$DB_EXISTS" = true ] && [ "$USER_EXISTS" = true ]; then
    echo "✅ Application database setup appears to be complete."
    exit 0
else
    echo "❌ Application database setup is incomplete."
    exit 1
fi
