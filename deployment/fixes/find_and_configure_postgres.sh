#!/bin/bash

# PostgreSQL Location Finder and Configuration Script
# This script is designed to find the PostgreSQL installation on EC2
# and configure it for TCP connections

# Colors for output
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NC="\033[0m" # No Color

echo -e "${YELLOW}===== PostgreSQL Location Finder and Configuration =====${NC}"

# First, check if PostgreSQL is running
if sudo systemctl is-active postgresql &>/dev/null; then
    echo -e "${GREEN}✅ PostgreSQL service is running${NC}"
else
    echo -e "${RED}❌ PostgreSQL service is not running${NC}"
    echo "Starting PostgreSQL service..."
    sudo systemctl start postgresql
    sleep 2
    if sudo systemctl is-active postgresql &>/dev/null; then
        echo -e "${GREEN}✅ PostgreSQL service started${NC}"
    else
        echo -e "${RED}❌ Failed to start PostgreSQL service${NC}"
        exit 1
    fi
fi

# Find where PostgreSQL is actually installed
echo -e "\n${YELLOW}Finding PostgreSQL installation...${NC}"

# Find the PostgreSQL executable
PG_BIN=$(which postgres 2>/dev/null)
if [ -z "$PG_BIN" ]; then
    echo "Looking for postgres executable..."
    PG_BIN=$(sudo find / -name postgres -type f -executable 2>/dev/null | head -n 1)
fi

if [ -n "$PG_BIN" ]; then
    echo -e "${GREEN}✅ Found PostgreSQL executable: $PG_BIN${NC}"
    PG_INSTALL_DIR=$(dirname $(dirname $PG_BIN))
    echo "PostgreSQL installation directory: $PG_INSTALL_DIR"
else
    echo -e "${RED}❌ Could not find PostgreSQL executable${NC}"
    echo "Will try to use default paths"
    PG_INSTALL_DIR="/usr/local/pgsql"
fi

# Find the PostgreSQL data directory from the service file
echo -e "\n${YELLOW}Finding PostgreSQL data directory...${NC}"

# Try multiple methods to find the data directory
# 1. From systemd service file
PG_DATA_DIR=""
if [ -f "/etc/systemd/system/postgresql.service" ]; then
    echo "Checking systemd service file..."
    PGDATA_LINE=$(sudo grep "PGDATA=" /etc/systemd/system/postgresql.service)
    if [[ $PGDATA_LINE =~ PGDATA=(.+) ]]; then
        PG_DATA_DIR="${BASH_REMATCH[1]}"
        PG_DATA_DIR=$(echo $PG_DATA_DIR | tr -d '"' | tr -d "'")
        echo "Found data directory in service file: $PG_DATA_DIR"
    fi
fi

# 2. From process environment
if [ -z "$PG_DATA_DIR" ]; then
    echo "Checking process environment..."
    PG_PID=$(pgrep -f "postgres" | head -n 1)
    if [ -n "$PG_PID" ]; then
        ENVIRON_PATH="/proc/$PG_PID/environ"
        if [ -f "$ENVIRON_PATH" ]; then
            PG_DATA_DIR=$(sudo strings "$ENVIRON_PATH" | grep "PGDATA=" | cut -d= -f2)
            if [ -n "$PG_DATA_DIR" ]; then
                echo "Found data directory in process environment: $PG_DATA_DIR"
            fi
        fi
    fi
fi

# 3. From default locations
if [ -z "$PG_DATA_DIR" ]; then
    echo "Checking default locations..."
    for dir in "/usr/local/pgsql/data" "/var/lib/pgsql/data" "/var/lib/postgresql/data"; do
        if [ -d "$dir" ]; then
            PG_DATA_DIR="$dir"
            echo "Found data directory at default location: $PG_DATA_DIR"
            break
        fi
    done
fi

# 4. Last resort - search for postgresql.conf
if [ -z "$PG_DATA_DIR" ]; then
    echo "Searching for postgresql.conf..."
    CONF_FILE=$(sudo find / -name "postgresql.conf" -type f 2>/dev/null | grep -v "backup" | head -n 1)
    if [ -n "$CONF_FILE" ]; then
        PG_DATA_DIR=$(dirname "$CONF_FILE")
        echo "Found data directory by searching for config file: $PG_DATA_DIR"
    fi
fi

# Display PostgreSQL data directory
if [ -n "$PG_DATA_DIR" ]; then
    echo -e "${GREEN}✅ PostgreSQL data directory: $PG_DATA_DIR${NC}"
else
    echo -e "${RED}❌ Could not determine PostgreSQL data directory${NC}"
    exit 1
fi

# Verify that postgresql.conf exists in the data directory
if [ ! -f "$PG_DATA_DIR/postgresql.conf" ]; then
    echo -e "${RED}❌ postgresql.conf not found in $PG_DATA_DIR${NC}"
    echo "Searching for postgresql.conf file..."
    CONF_FILE=$(sudo find / -name "postgresql.conf" -type f 2>/dev/null | grep -v "backup" | head -n 1)
    if [ -n "$CONF_FILE" ]; then
        echo -e "${GREEN}✅ Found postgresql.conf at: $CONF_FILE${NC}"
        echo "Creating a symlink to the correct location..."
        sudo ln -sf "$CONF_FILE" "$PG_DATA_DIR/postgresql.conf"
    else
        echo -e "${RED}❌ Could not find postgresql.conf anywhere${NC}"
        echo "Creating a basic postgresql.conf file..."
        cat <<EOF | sudo tee "$PG_DATA_DIR/postgresql.conf"
# Basic PostgreSQL Configuration
listen_addresses = '*'
port = 5432
max_connections = 100
shared_buffers = 128MB
dynamic_shared_memory_type = posix
log_timezone = 'UTC'
datestyle = 'iso, mdy'
timezone = 'UTC'
lc_messages = 'en_US.UTF-8'
lc_monetary = 'en_US.UTF-8'
lc_numeric = 'en_US.UTF-8'
lc_time = 'en_US.UTF-8'
default_text_search_config = 'pg_catalog.english'
EOF
        echo -e "${GREEN}✅ Created basic postgresql.conf${NC}"
    fi
fi

# Verify that pg_hba.conf exists in the data directory
if [ ! -f "$PG_DATA_DIR/pg_hba.conf" ]; then
    echo -e "${RED}❌ pg_hba.conf not found in $PG_DATA_DIR${NC}"
    echo "Searching for pg_hba.conf file..."
    HBA_FILE=$(sudo find / -name "pg_hba.conf" -type f 2>/dev/null | grep -v "backup" | head -n 1)
    if [ -n "$HBA_FILE" ]; then
        echo -e "${GREEN}✅ Found pg_hba.conf at: $HBA_FILE${NC}"
        echo "Creating a symlink to the correct location..."
        sudo ln -sf "$HBA_FILE" "$PG_DATA_DIR/pg_hba.conf"
    else
        echo -e "${RED}❌ Could not find pg_hba.conf anywhere${NC}"
        echo "Creating a basic pg_hba.conf file..."
        cat <<EOF | sudo tee "$PG_DATA_DIR/pg_hba.conf"
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    all             all             0.0.0.0/0               md5
EOF
        echo -e "${GREEN}✅ Created basic pg_hba.conf${NC}"
    fi
fi

# Configure PostgreSQL to listen on all interfaces
echo -e "\n${YELLOW}Configuring PostgreSQL to listen on all interfaces...${NC}"
if sudo grep -q "^[#]*listen_addresses" "$PG_DATA_DIR/postgresql.conf"; then
    sudo sed -i "s/^[#]*listen_addresses.*/listen_addresses = '*'/" "$PG_DATA_DIR/postgresql.conf"
else
    echo "listen_addresses = '*'" | sudo tee -a "$PG_DATA_DIR/postgresql.conf"
fi

# Configure pg_hba.conf to allow password authentication
echo -e "\n${YELLOW}Configuring PostgreSQL authentication...${NC}"
if ! sudo grep -q "host.*all.*all.*0.0.0.0/0.*md5" "$PG_DATA_DIR/pg_hba.conf"; then
    echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a "$PG_DATA_DIR/pg_hba.conf"
fi

# Restart PostgreSQL to apply changes
echo -e "\n${YELLOW}Restarting PostgreSQL...${NC}"
sudo systemctl restart postgresql
sleep 2
if sudo systemctl is-active postgresql &>/dev/null; then
    echo -e "${GREEN}✅ PostgreSQL restarted successfully${NC}"
else
    echo -e "${RED}❌ Failed to restart PostgreSQL${NC}"
    echo "Checking PostgreSQL logs..."
    if [ -d "$PG_DATA_DIR/log" ]; then
        sudo tail -n 20 "$PG_DATA_DIR/log/postgresql.log"
    fi
    exit 1
fi

# Test PostgreSQL connection
echo -e "\n${YELLOW}Testing PostgreSQL connection...${NC}"
if sudo -u postgres psql -c "SELECT version();" &>/dev/null; then
    echo -e "${GREEN}✅ PostgreSQL connection successful${NC}"
    POSTGRES_VERSION=$(sudo -u postgres psql -t -c "SELECT version();")
    echo "PostgreSQL version: $POSTGRES_VERSION"
else
    echo -e "${RED}❌ Failed to connect to PostgreSQL${NC}"
    exit 1
fi

echo -e "\n${GREEN}===== PostgreSQL configuration completed successfully! =====${NC}"
echo ""
echo "PostgreSQL is now configured to accept TCP connections."
echo "You can now proceed with setting up the application database."
