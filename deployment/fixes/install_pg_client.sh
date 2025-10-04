#!/bin/bash

# This script installs PostgreSQL client tools on Amazon Linux 2023
# These tools are needed for commands like psql, pg_isready, createdb, etc.

echo "Installing PostgreSQL 15 client tools..."

# Install PostgreSQL client tools
sudo dnf install -y postgresql15

# Verify installation
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL client tools installed successfully!"
    psql --version
else
    echo "❌ Failed to install PostgreSQL client tools"
    exit 1
fi

echo ""
echo "Available PostgreSQL commands:"
echo "• psql - PostgreSQL interactive terminal"
echo "• pg_isready - Check if PostgreSQL server is accepting connections"
echo "• createdb - Create a new PostgreSQL database"
echo "• dropdb - Drop a PostgreSQL database"
echo "• pg_dump - Backup a PostgreSQL database"
echo "• pg_restore - Restore a PostgreSQL database"

echo ""
echo "Example usage:"
echo "psql -h localhost -p 5432 -U postgres"
echo "pg_isready -h localhost -p 5432"
echo "createdb -h localhost -p 5432 -U postgres your_db_name"
