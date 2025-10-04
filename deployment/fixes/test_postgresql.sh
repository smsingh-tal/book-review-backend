#!/bin/bash

# This script checks if PostgreSQL is running and performs various tests
# to verify it's working correctly

echo "===== PostgreSQL Status Test ====="

# Part 1: Check if PostgreSQL service is running
echo ""
echo "Checking PostgreSQL service status..."
if sudo systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL service is running"
    
    # Get additional service details
    echo ""
    echo "PostgreSQL service details:"
    sudo systemctl status postgresql --no-pager | grep -E "Active:|Main PID:|Tasks:|Memory:|CPU:"
else
    echo "❌ PostgreSQL service is NOT running"
    echo "Try starting the service with: sudo systemctl start postgresql"
    exit 1
fi

# Part 2: Check which port PostgreSQL is listening on
echo ""
echo "Checking PostgreSQL listening ports..."
PORTS=$(sudo netstat -tulpn | grep postgres | awk '{print $4}' | cut -d':' -f2)

if [ -z "$PORTS" ]; then
    echo "❌ PostgreSQL is not listening on any ports"
    echo "Check the PostgreSQL configuration and logs"
    exit 1
else
    for PORT in $PORTS; do
        echo "✅ PostgreSQL is listening on port: $PORT"
        TEST_PORT=$PORT
    done
fi

# Part 3: Test connection with pg_isready
echo ""
echo "Testing PostgreSQL connection with pg_isready..."

if ! command -v pg_isready &>/dev/null; then
    echo "⚠️ pg_isready command not found. Installing PostgreSQL client tools..."
    sudo dnf install -y postgresql15 > /dev/null
fi

if command -v pg_isready &>/dev/null; then
    if pg_isready -h localhost -p $TEST_PORT; then
        echo "✅ PostgreSQL is accepting connections on port $TEST_PORT"
    else
        echo "❌ PostgreSQL is not accepting connections"
        echo "Check PostgreSQL logs for errors: sudo cat /tmp/postgresql.log"
        exit 1
    fi
else
    echo "❌ Could not install pg_isready tool"
    echo "Will try connecting with psql instead"
fi

# Part 4: Test database connection with psql
echo ""
echo "Testing database connection with psql..."

if ! command -v psql &>/dev/null; then
    echo "⚠️ psql command not found. Installing PostgreSQL client tools..."
    sudo dnf install -y postgresql15 > /dev/null
fi

if command -v psql &>/dev/null; then
    # Try connecting as postgres user
    if psql -h localhost -p $TEST_PORT -U postgres -c "SELECT version();" > /dev/null 2>&1; then
        echo "✅ Successfully connected to PostgreSQL as 'postgres' user"
        DB_VERSION=$(psql -h localhost -p $TEST_PORT -U postgres -c "SELECT version();" -t | tr -d ' ')
        echo "PostgreSQL version: $DB_VERSION"
    else
        echo "❌ Could not connect as 'postgres' user"
        echo "This could be due to authentication issues"
    fi
    
    # Check for book_review database and user if they exist
    if psql -h localhost -p $TEST_PORT -U postgres -lqt | cut -d \| -f 1 | grep -qw "book_review"; then
        echo "✅ 'book_review' database exists"
        
        # Check if book_user exists
        if psql -h localhost -p $TEST_PORT -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='book_user'" | grep -q 1; then
            echo "✅ 'book_user' user exists"
            
            # Try connecting as book_user
            echo "Attempting to connect as 'book_user'..."
            if PGPASSWORD="secure_password" psql -h localhost -p $TEST_PORT -U book_user -d book_review -c "SELECT current_user;" > /dev/null 2>&1; then
                echo "✅ Successfully connected as 'book_user'"
            else
                echo "❌ Could not connect as 'book_user'"
                echo "This could be due to incorrect password or permissions"
            fi
        else
            echo "ℹ️ 'book_user' user does not exist yet"
        fi
    else
        echo "ℹ️ 'book_review' database does not exist yet"
    fi
else
    echo "❌ Could not install psql tool"
fi

# Part 5: Check PostgreSQL logs for errors
echo ""
echo "Checking PostgreSQL logs for recent errors..."
if [ -f "/tmp/postgresql.log" ]; then
    ERROR_COUNT=$(grep -c "ERROR:" /tmp/postgresql.log)
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo "⚠️ Found $ERROR_COUNT errors in the PostgreSQL log"
        echo "Recent errors:"
        grep "ERROR:" /tmp/postgresql.log | tail -5
    else
        echo "✅ No errors found in the PostgreSQL log"
    fi
else
    echo "ℹ️ PostgreSQL log file not found at /tmp/postgresql.log"
fi

echo ""
echo "===== Database Connection Summary ====="
echo "PostgreSQL service: Running"
echo "Listening on port: $TEST_PORT"
echo "Connection status: $(pg_isready -h localhost -p $TEST_PORT)"
echo ""
echo "To connect to PostgreSQL manually:"
echo "psql -h localhost -p $TEST_PORT -U postgres"
