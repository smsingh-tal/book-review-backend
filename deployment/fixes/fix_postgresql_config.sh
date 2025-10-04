#!/bin/bash

# This script fixes the postgresql.conf file by removing duplicate port entries
# and ensuring proper formatting

# Location of the PostgreSQL config file
PGCONF="/usr/local/pgsql/data/postgresql.conf"

# Check if the file exists
if [ ! -f "$PGCONF" ]; then
    echo "PostgreSQL configuration file not found at $PGCONF"
    exit 1
fi

echo "Creating backup of current configuration..."
sudo cp "$PGCONF" "${PGCONF}.bak.$(date +%Y%m%d%H%M%S)"

# Remove the duplicate port and listen_addresses entries
echo "Cleaning up configuration file..."

# Create a clean version with unique settings
sudo grep -v "^port = " "$PGCONF" | sudo grep -v "^listen_addresses = " > /tmp/pg_conf_clean.tmp

# Add the correct settings at the end of the file
echo "Adding proper configuration..."
cat << EOF | sudo tee -a /tmp/pg_conf_clean.tmp

#------------------------------------------------------------------------------
# CONNECTION SETTINGS
#------------------------------------------------------------------------------

# Custom settings
port = 5432                  # Using standard PostgreSQL port
listen_addresses = '*'       # Listen on all interfaces
EOF

# Replace the original file
sudo cp /tmp/pg_conf_clean.tmp "$PGCONF"
sudo rm /tmp/pg_conf_clean.tmp

echo "PostgreSQL configuration file has been cleaned up."
echo "You can now restart PostgreSQL with: sudo systemctl restart postgresql"
echo "After restart, connect using: psql -h localhost -p 5432 -U postgres"
