#!/bin/bash

# PostgreSQL Setup Script for Amazon Linux 2
# This script installs and configures PostgreSQL for the book review application

set -e

echo "=== Setting up PostgreSQL on Amazon Linux 2 ==="

# Update the system
echo "Updating system packages..."
sudo yum update -y

# Install PostgreSQL 14 (recommended version for Amazon Linux 2)
echo "Installing PostgreSQL 14..."
sudo yum install -y postgresql14 postgresql14-server postgresql14-contrib

# Initialize the database
echo "Initializing PostgreSQL database..."
sudo postgresql-14-setup initdb

# Enable and start PostgreSQL service
echo "Starting PostgreSQL service..."
sudo systemctl enable postgresql-14
sudo systemctl start postgresql-14

# Check if PostgreSQL is running
echo "Checking PostgreSQL status..."
sudo systemctl status postgresql-14 --no-pager

# Configure PostgreSQL for local connections
echo "Configuring PostgreSQL authentication..."

# Backup original configuration
sudo cp /var/lib/pgsql/14/data/pg_hba.conf /var/lib/pgsql/14/data/pg_hba.conf.backup
sudo cp /var/lib/pgsql/14/data/postgresql.conf /var/lib/pgsql/14/data/postgresql.conf.backup

# Update pg_hba.conf to allow local connections with password authentication
sudo sed -i "s/local   all             all                                     peer/local   all             all                                     md5/" /var/lib/pgsql/14/data/pg_hba.conf
sudo sed -i "s/host    all             all             127.0.0.1\/32            ident/host    all             all             127.0.0.1\/32            md5/" /var/lib/pgsql/14/data/pg_hba.conf
sudo sed -i "s/host    all             all             ::1\/128                 ident/host    all             all             ::1\/128                 md5/" /var/lib/pgsql/14/data/pg_hba.conf

# Configure PostgreSQL to listen on localhost
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /var/lib/pgsql/14/data/postgresql.conf

# Restart PostgreSQL to apply configuration changes
echo "Restarting PostgreSQL to apply configuration..."
sudo systemctl restart postgresql-14

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
