#!/bin/bash

# This script ensures PostgreSQL is properly configured to run in the background as a system service
# It checks, enables, and starts the PostgreSQL service

echo "Setting up PostgreSQL to run in the background as a service..."

# Check if the PostgreSQL service is enabled to start at boot
echo "Checking if PostgreSQL service is enabled at boot..."
if sudo systemctl is-enabled postgresql &>/dev/null; then
    echo "✅ PostgreSQL service is already enabled at boot"
else
    echo "Enabling PostgreSQL service to start at boot..."
    sudo systemctl enable postgresql
    echo "✅ PostgreSQL service enabled"
fi

# Check if the PostgreSQL service is running
echo "Checking if PostgreSQL service is running..."
if sudo systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL service is already running"
else
    echo "Starting PostgreSQL service..."
    sudo systemctl start postgresql
    echo "✅ PostgreSQL service started"
fi

# Verify PostgreSQL status
echo "PostgreSQL service status:"
sudo systemctl status postgresql --no-pager

echo ""
echo "🔍 Checking PostgreSQL connectivity..."
if command -v pg_isready &>/dev/null; then
    # Try port 5432 first (standard port)
    if pg_isready -h localhost -p 5432 &>/dev/null; then
        echo "✅ PostgreSQL is accepting connections on port 5432"
        PORT=5432
    # Try port 5433 next (alternative port)
    elif pg_isready -h localhost -p 5433 &>/dev/null; then
        echo "✅ PostgreSQL is accepting connections on port 5433"
        PORT=5433
    else
        echo "❌ PostgreSQL is not accepting connections on standard ports"
        echo "Please check the PostgreSQL logs for errors:"
        echo "sudo cat /tmp/postgresql.log"
        exit 1
    fi
else
    echo "⚠️ pg_isready command not found. Installing PostgreSQL client tools..."
    sudo dnf install -y postgresql15
    
    if pg_isready -h localhost -p 5432 &>/dev/null; then
        echo "✅ PostgreSQL is accepting connections on port 5432"
        PORT=5432
    elif pg_isready -h localhost -p 5433 &>/dev/null; then
        echo "✅ PostgreSQL is accepting connections on port 5433"
        PORT=5433
    else
        echo "❌ PostgreSQL is not accepting connections"
        echo "Please check the PostgreSQL logs for errors:"
        echo "sudo cat /tmp/postgresql.log"
        exit 1
    fi
fi

echo ""
echo "PostgreSQL is now running in the background on port $PORT"
echo "You can connect to it using: psql -h localhost -p $PORT -U postgres"
echo ""
echo "To check the service status at any time, run:"
echo "sudo systemctl status postgresql"
echo ""
echo "To stop the service:"
echo "sudo systemctl stop postgresql"
echo ""
echo "To restart the service:"
echo "sudo systemctl restart postgresql"
