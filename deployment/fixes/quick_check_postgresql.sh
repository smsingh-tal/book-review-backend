#!/bin/bash

# This script provides a quick check of whether PostgreSQL is running properly
# and attempts to fix any issues automatically

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to check if PostgreSQL is running
check_postgres_running() {
    sudo systemctl is-active --quiet postgresql
}

# Function to find the PostgreSQL port
find_postgres_port() {
    local ports
    ports=$(sudo netstat -tulpn | grep postgres | awk '{print $4}' | cut -d':' -f2)
    if [ -z "$ports" ]; then
        # Try alternative detection method
        ports=$(sudo ss -tulpn | grep postgres | awk '{print $5}' | cut -d':' -f2)
    fi
    echo "$ports" | head -1
}

# Function to test connection using pg_isready
test_with_pg_isready() {
    local port="$1"
    if command_exists pg_isready; then
        pg_isready -h localhost -p "$port" > /dev/null 2>&1
        return $?
    fi
    return 1
}

# Function to test connection using psql
test_with_psql() {
    local port="$1"
    if command_exists psql; then
        psql -h localhost -p "$port" -U postgres -c "SELECT 1;" > /dev/null 2>&1
        return $?
    fi
    return 1
}

# Function to start PostgreSQL service
start_postgres() {
    echo "Starting PostgreSQL service..."
    sudo systemctl start postgresql
}

echo "🔍 Checking PostgreSQL status..."

# Step 1: Check if PostgreSQL service is running
if check_postgres_running; then
    echo "✅ PostgreSQL service is running"
else
    echo "❌ PostgreSQL service is not running"
    echo "Attempting to start PostgreSQL..."
    start_postgres
    sleep 2
    
    if check_postgres_running; then
        echo "✅ PostgreSQL service started successfully"
    else
        echo "❌ Failed to start PostgreSQL service"
        echo "Try running: sudo ./setup_postgresql_service.sh"
        exit 1
    fi
fi

# Step 2: Find which port PostgreSQL is listening on
PORT=$(find_postgres_port)
if [ -n "$PORT" ]; then
    echo "✅ PostgreSQL is listening on port: $PORT"
else
    echo "❌ PostgreSQL is not listening on any port"
    echo "This may indicate a configuration issue"
    echo "Try running: sudo ./fix_postgresql_config.sh"
    exit 1
fi

# Step 3: Test connection with pg_isready if available
if test_with_pg_isready "$PORT"; then
    echo "✅ PostgreSQL is accepting connections (pg_isready test passed)"
else
    echo "⚠️ pg_isready test failed"
fi

# Step 4: Test connection with psql if available
if test_with_psql "$PORT"; then
    echo "✅ PostgreSQL database connection successful (psql test passed)"
else
    echo "⚠️ psql test failed"
fi

# Final summary
if check_postgres_running && [ -n "$PORT" ] && (test_with_pg_isready "$PORT" || test_with_psql "$PORT"); then
    echo ""
    echo "✅ PostgreSQL is running correctly!"
    echo "Service: Active"
    echo "Port: $PORT"
    echo ""
    echo "To connect: psql -h localhost -p $PORT -U postgres"
    exit 0
else
    echo ""
    echo "⚠️ PostgreSQL is running but may have configuration issues."
    echo "For detailed diagnostics, run: ./test_postgresql.sh"
    exit 1
fi
