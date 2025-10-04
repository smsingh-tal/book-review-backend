#!/bin/bash

# This is a direct fix command to fix the PostgreSQL configuration issue
# Run this on your EC2 instance to fix the configuration immediately

# Back up the current configuration
sudo cp /usr/local/pgsql/data/postgresql.conf /usr/local/pgsql/data/postgresql.conf.bak.$(date +%Y%m%d%H%M%S)

# Remove duplicate entries and create a clean configuration
sudo sed -i '/^port = /d' /usr/local/pgsql/data/postgresql.conf
sudo sed -i '/^listen_addresses = /d' /usr/local/pgsql/data/postgresql.conf

# Add proper configuration at the end of the file
echo "" | sudo tee -a /usr/local/pgsql/data/postgresql.conf
echo "#------------------------------------------------------------------------------" | sudo tee -a /usr/local/pgsql/data/postgresql.conf
echo "# CONNECTION SETTINGS" | sudo tee -a /usr/local/pgsql/data/postgresql.conf
echo "#------------------------------------------------------------------------------" | sudo tee -a /usr/local/pgsql/data/postgresql.conf
echo "" | sudo tee -a /usr/local/pgsql/data/postgresql.conf
echo "# Custom settings" | sudo tee -a /usr/local/pgsql/data/postgresql.conf
echo "port = 5432                  # Using standard PostgreSQL port" | sudo tee -a /usr/local/pgsql/data/postgresql.conf
echo "listen_addresses = '*'       # Listen on all interfaces" | sudo tee -a /usr/local/pgsql/data/postgresql.conf

echo "PostgreSQL configuration has been fixed. Now restart PostgreSQL:"
echo "sudo systemctl restart postgresql"
echo "After restart, connect using: psql -h localhost -p 5432 -U postgres"
