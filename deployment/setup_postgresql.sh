#!/bin/bash

# PostgreSQL Setup Script for Amazon Linux 2/2023
# This script installs and configures PostgreSQL for the book review application

set -e

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "Cannot determine OS version"
    exit 1
fi

echo "=== Setting up PostgreSQL on $OS $VER ==="

# Set PostgreSQL version based on OS
if [[ "$OS" == *"Amazon Linux"* ]] && [[ "$VER" == "2023" ]]; then
    PGSQL_VERSION="15"
else
    PGSQL_VERSION="14"
fi

echo "Using PostgreSQL $PGSQL_VERSION for $OS $VER"

# Update the system
echo "Updating system packages..."
if command -v dnf &> /dev/null; then
    sudo dnf update -y
else
    sudo yum update -y
fi

if [[ "$OS" == *"Amazon Linux"* ]] && [[ "$VER" == "2023" ]]; then
    # For Amazon Linux 2023, PostgreSQL should already be installed by install_dependencies.sh
    echo "PostgreSQL $PGSQL_VERSION should already be installed by install_dependencies.sh"
    
    # If not installed, exit with error
    if ! command -v /usr/pgsql-15/bin/psql &> /dev/null; then
        echo "PostgreSQL 15 not found. Please run install_dependencies.sh first."
        exit 1
    fi
else
    # For Amazon Linux 2, install PostgreSQL 14
    echo "Installing PostgreSQL 14..."
    sudo yum install -y postgresql14 postgresql14-server postgresql14-contrib
    
    # Initialize the database
    echo "Initializing PostgreSQL database..."
    sudo /usr/pgsql-14/bin/postgresql-14-setup initdb
fi

# Enable and start PostgreSQL service
echo "Starting PostgreSQL service..."
sudo systemctl enable postgresql-$PGSQL_VERSION
sudo systemctl start postgresql-$PGSQL_VERSION

# Check if PostgreSQL is running
echo "Checking PostgreSQL status..."
sudo systemctl status postgresql-$PGSQL_VERSION --no-pager

# Configure PostgreSQL for local connections
echo "Configuring PostgreSQL authentication..."

# Backup original configuration
sudo cp /var/lib/pgsql/$PGSQL_VERSION/data/pg_hba.conf /var/lib/pgsql/$PGSQL_VERSION/data/pg_hba.conf.backup
sudo cp /var/lib/pgsql/$PGSQL_VERSION/data/postgresql.conf /var/lib/pgsql/$PGSQL_VERSION/data/postgresql.conf.backup

# Update pg_hba.conf to allow local connections with password authentication
sudo sed -i "s/local   all             all                                     peer/local   all             all                                     md5/" /var/lib/pgsql/$PGSQL_VERSION/data/pg_hba.conf
sudo sed -i "s/host    all             all             127.0.0.1\/32            ident/host    all             all             127.0.0.1\/32            md5/" /var/lib/pgsql/$PGSQL_VERSION/data/pg_hba.conf
sudo sed -i "s/host    all             all             ::1\/128                 ident/host    all             all             ::1\/128                 md5/" /var/lib/pgsql/$PGSQL_VERSION/data/pg_hba.conf

# For Amazon Linux 2023, scram-sha-256 might be default auth method instead of peer/ident
if [[ "$OS" == *"Amazon Linux"* ]] && [[ "$VER" == "2023" ]]; then
    sudo sed -i "s/local   all             all                                     scram-sha-256/local   all             all                                     md5/" /var/lib/pgsql/$PGSQL_VERSION/data/pg_hba.conf
    sudo sed -i "s/host    all             all             127.0.0.1\/32            scram-sha-256/host    all             all             127.0.0.1\/32            md5/" /var/lib/pgsql/$PGSQL_VERSION/data/pg_hba.conf
    sudo sed -i "s/host    all             all             ::1\/128                 scram-sha-256/host    all             all             ::1\/128                 md5/" /var/lib/pgsql/$PGSQL_VERSION/data/pg_hba.conf
fi

# Configure PostgreSQL to listen on localhost
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /var/lib/pgsql/$PGSQL_VERSION/data/postgresql.conf

# Restart PostgreSQL to apply configuration changes
echo "Restarting PostgreSQL to apply configuration..."
sudo systemctl restart postgresql-$PGSQL_VERSION

# Set up database and user
echo "Setting up database and user..."

# Switch to postgres user and create database and user
sudo -u postgres psql << EOF
-- Set password for postgres user
ALTER USER postgres PASSWORD 'postgres';

-- Create the book_review database
DROP DATABASE IF EXISTS book_review;
CREATE DATABASE book_review;

-- Grant all privileges on book_review database to postgres user
GRANT ALL PRIVILEGES ON DATABASE book_review TO postgres;

-- Show databases to confirm creation
\l

-- Quit
\q
EOF

# Test the connection
echo "Testing PostgreSQL connection..."
PGPASSWORD=postgres psql -h localhost -U postgres -d book_review -c "SELECT version();"

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL setup completed successfully!"
    echo ""
    echo "Database Details:"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  Database: book_review"
    echo "  Username: postgres" 
    echo "  Password: postgres"
    echo ""
    echo "Connection string: postgresql://postgres:postgres@localhost:5432/book_review"
else
    echo "❌ PostgreSQL connection test failed!"
    exit 1
fi
