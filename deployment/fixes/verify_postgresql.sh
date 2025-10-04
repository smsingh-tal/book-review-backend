#!/bin/bash

# This script verifies that PostgreSQL is running correctly after configuration fixes

echo "Checking PostgreSQL server status..."

# Check if PostgreSQL is running
if systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL service is active and running"
else
    echo "❌ PostgreSQL service is not running"
    echo "Checking logs for errors..."
    sudo cat /tmp/postgresql.log | tail -20
    echo ""
    echo "Try starting the service manually:"
    echo "sudo systemctl start postgresql"
    exit 1
fi

# Check if PostgreSQL is accepting connections
if command -v pg_isready &> /dev/null; then
    if pg_isready -h localhost -p 5432; then
        echo "✅ PostgreSQL is accepting connections on port 5432"
    else
        echo "❌ PostgreSQL is not accepting connections"
        echo "Checking listener status..."
        sudo netstat -tulpn | grep 5432 || echo "No process is listening on port 5432"
        echo ""
        echo "Check configuration and restart the service:"
        echo "sudo systemctl restart postgresql"
        exit 1
    fi
else
    echo "⚠️ pg_isready command not found. Installing PostgreSQL client tools..."
    sudo dnf install -y postgresql15
    
    if command -v pg_isready &> /dev/null; then
        if pg_isready -h localhost -p 5432; then
            echo "✅ PostgreSQL is accepting connections on port 5432"
        else
            echo "❌ PostgreSQL is not accepting connections"
            echo "Checking listener status..."
            sudo netstat -tulpn | grep 5432 || echo "No process is listening on port 5432"
            echo ""
            echo "Check configuration and restart the service:"
            echo "sudo systemctl restart postgresql"
            exit 1
        fi
    else
        echo "❌ Could not install PostgreSQL client tools. Continuing with basic checks..."
        # Check if something is listening on the PostgreSQL port
        if sudo netstat -tulpn | grep 5432; then
            echo "✅ Something is listening on port 5432 (likely PostgreSQL)"
        else
            echo "❌ No process is listening on port 5432"
            echo "Check configuration and restart the service:"
            echo "sudo systemctl restart postgresql"
            exit 1
        fi
    fi
fi

# Try to connect to PostgreSQL
echo "Testing database connection..."
if command -v psql &> /dev/null; then
    if psql -h localhost -p 5432 -U postgres -c "SELECT version();" > /dev/null 2>&1; then
        echo "✅ Successfully connected to PostgreSQL database"
    else
        echo "❌ Could not connect to PostgreSQL database"
        echo "Check authentication settings or try connecting manually:"
        echo "psql -h localhost -p 5432 -U postgres"
        echo ""
        echo "If you get a password prompt, you might need to set up the postgres user password:"
        echo "sudo -u postgres psql -c \"ALTER USER postgres WITH PASSWORD 'your_password';\""
        exit 1
    fi
else
    echo "⚠️ psql command not found. PostgreSQL client tools are not installed."
    echo "To install PostgreSQL client tools, run:"
    echo "sudo dnf install -y postgresql15"
    echo ""
    echo "After installation, try connecting manually:"
    echo "psql -h localhost -p 5432 -U postgres"
    
    # We can't test the connection further without psql
    echo "Skipping direct connection test due to missing tools."
    # Don't exit here, so we can show the final instructions
fi

echo ""
echo "🎉 PostgreSQL service is running!"

if ! command -v psql &> /dev/null || ! command -v pg_isready &> /dev/null; then
    echo "⚠️ Important: PostgreSQL client tools are not fully installed"
    echo "Install them with:"
    echo "sudo dnf install -y postgresql15"
    echo ""
    echo "After installing the client tools, run this verification script again."
else
    echo "You can connect to the database using: psql -h localhost -p 5432 -U postgres"
fi

# Add reminder about setting up a database and user for your application
echo ""
echo "Next steps:"
echo "1. Create a database for your application:"
echo "   createdb -h localhost -p 5432 -U postgres book_review"
echo ""
echo "2. Create an application user with appropriate permissions:"
echo "   psql -h localhost -p 5432 -U postgres -c \"CREATE USER book_user WITH PASSWORD 'your_secure_password';\""
echo "   psql -h localhost -p 5432 -U postgres -c \"GRANT ALL PRIVILEGES ON DATABASE book_review TO book_user;\""
