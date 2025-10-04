#!/bin/bash

# This script sets up the book_review database and creates a database user for the application
# It will automatically detect which port PostgreSQL is running on (5432 or 5433)

# Set default values
DB_NAME="book_review"
DB_USER="book_user"
DB_PASSWORD="secure_password"  # Change this to a secure password

echo "Setting up database for the book-review-backend application..."

# Check if PostgreSQL client tools are installed
if ! command -v psql &>/dev/null; then
    echo "❌ PostgreSQL client tools not found"
    echo "Installing PostgreSQL client tools..."
    sudo dnf install -y postgresql15
fi

# Detect PostgreSQL installation and connection method
echo "Checking PostgreSQL connection..."

# Find the PostgreSQL data directory
echo "Finding PostgreSQL data directory..."
if [ -d "/usr/local/pgsql/data" ]; then
    PGDATA="/usr/local/pgsql/data"
    echo "Found PostgreSQL data directory at: $PGDATA"
elif [ -d "/var/lib/pgsql/data" ]; then
    PGDATA="/var/lib/pgsql/data"
    echo "Found PostgreSQL data directory at: $PGDATA"
else
    echo "Searching for PostgreSQL data directory..."
    PGDATA=$(sudo find / -name "postgresql.conf" -type f 2>/dev/null | grep -v "backup" | head -n 1 | xargs dirname 2>/dev/null)
    if [ -n "$PGDATA" ]; then
        echo "Found PostgreSQL data directory at: $PGDATA"
    else
        echo "Could not find PostgreSQL data directory"
    fi
fi

# Find the PostgreSQL socket directory
echo "Finding PostgreSQL socket directory..."
if [ -S "/tmp/.s.PGSQL.5432" ]; then
    SOCKET_DIR="/tmp"
    echo "Found PostgreSQL socket in /tmp"
elif [ -S "/var/run/postgresql/.s.PGSQL.5432" ]; then
    SOCKET_DIR="/var/run/postgresql"
    echo "Found PostgreSQL socket in /var/run/postgresql"
elif [ -S "/run/postgresql/.s.PGSQL.5432" ]; then
    SOCKET_DIR="/run/postgresql"
    echo "Found PostgreSQL socket in /run/postgresql"
else
    echo "Could not find PostgreSQL socket file"
    SOCKET_DIR=""
fi

# Try different methods of connection
if sudo -u postgres PGHOST=$SOCKET_DIR psql -c "SELECT 1;" &>/dev/null; then
    echo "✅ PostgreSQL direct connection successful via socket directory"
    PGPORT=5432
    PGHOST=$SOCKET_DIR
elif sudo -u postgres psql -h localhost -c "SELECT 1;" &>/dev/null; then
    echo "✅ PostgreSQL direct connection successful via TCP localhost"
    PGPORT=5432
    PGHOST="localhost"
elif sudo -u postgres psql -h 127.0.0.1 -c "SELECT 1;" &>/dev/null; then
    echo "✅ PostgreSQL direct connection successful via TCP IP"
    PGPORT=5432
    PGHOST="127.0.0.1"
else
    echo "❌ PostgreSQL server is not running or not accepting connections"
    echo "Attempting to diagnose the issue..."
    
    # Check PostgreSQL service status
    echo "PostgreSQL service status:"
    systemctl status postgresql
    
    # Check PostgreSQL data directory
    PGDATA="/usr/local/pgsql/data"
    echo "Checking permissions of PostgreSQL data directory: $PGDATA"
    ls -la $PGDATA 2>/dev/null || echo "Cannot access data directory"
    
    echo "Please ensure PostgreSQL is running with: sudo systemctl start postgresql"
    echo "If it's already running, there might be connection issues."
    exit 1
fi

# Create the database if it doesn't exist
echo "Creating database '$DB_NAME' if it doesn't exist..."

# Try both connection methods for checking if the database exists
if ! sudo -u postgres PGHOST=${PGHOST:-$SOCKET_DIR} psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "Creating database with sudo -u postgres..."
    
    # Try different methods to create the database
    if sudo -u postgres PGHOST=${PGHOST:-$SOCKET_DIR} createdb "$DB_NAME" 2>/dev/null; then
        echo "✅ Database '$DB_NAME' created successfully"
    elif sudo -u postgres createdb -h localhost "$DB_NAME" 2>/dev/null; then
        echo "✅ Database '$DB_NAME' created successfully via localhost"
    elif sudo -u postgres createdb -h 127.0.0.1 "$DB_NAME" 2>/dev/null; then
        echo "✅ Database '$DB_NAME' created successfully via IP"
    else
        echo "❌ Failed to create database. Attempting direct SQL command..."
        sudo -u postgres PGHOST=${PGHOST:-$SOCKET_DIR} psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ Database '$DB_NAME' created successfully using direct SQL"
        else
            echo "❌ Failed to create database using multiple methods"
            exit 1
        fi
    fi
else
    echo "✅ Database '$DB_NAME' already exists"
fi

# Create the user if it doesn't exist
echo "Creating database user '$DB_USER' if it doesn't exist..."
if ! sudo -u postgres PGHOST=${PGHOST:-$SOCKET_DIR} psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo "Creating user $DB_USER..."
    sudo -u postgres PGHOST=${PGHOST:-$SOCKET_DIR} psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    if [ $? -eq 0 ]; then
        echo "✅ User '$DB_USER' created successfully"
    else
        echo "❌ Failed to create user using standard method, trying alternative..."
        sudo -u postgres psql -h localhost -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "❌ Failed to create user. This is critical for application functionality."
            exit 1
        else
            echo "✅ User '$DB_USER' created successfully with alternative method"
        fi
    fi
else
    echo "✅ User '$DB_USER' already exists, updating password..."
    sudo -u postgres PGHOST=${PGHOST:-$SOCKET_DIR} psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
fi

# Grant privileges to the user
echo "Granting privileges to user $DB_USER on database $DB_NAME..."
sudo -u postgres PGHOST=${PGHOST:-$SOCKET_DIR} psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Connect to the specific database to grant schema privileges
echo "Granting schema privileges..."
if sudo -u postgres PGHOST=${PGHOST:-$SOCKET_DIR} psql -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;" 2>/dev/null; then
    echo "✅ Schema privileges granted"
else
    echo "⚠️ Could not grant schema privileges using socket connection, trying alternatives..."
    if sudo -u postgres psql -h localhost -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;" 2>/dev/null; then
        echo "✅ Schema privileges granted using localhost connection"
    elif sudo -u postgres psql -h 127.0.0.1 -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;" 2>/dev/null; then
        echo "✅ Schema privileges granted using IP connection"
    else
        echo "⚠️ Could not grant schema privileges. The application may have limited functionality."
    fi
fi
echo "✅ Database privileges granted"

# Test the connection with the new user
echo "Testing connection with the new user..."
if PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME -c "SELECT 'Connection successful';" &>/dev/null; then
    echo "✅ Connection test successful"
else
    echo "⚠️ Connection test failed. Checking PostgreSQL client authentication settings."
    echo "You may need to edit PostgreSQL authentication configuration."
    
    # Check pg_hba.conf content
    echo "Current pg_hba.conf configuration:"
    PG_HBA_CONF="/usr/local/pgsql/data/pg_hba.conf"
    if [ -f "$PG_HBA_CONF" ]; then
        sudo grep -v "^#" "$PG_HBA_CONF" | grep -v "^$"
        
        echo "Updating pg_hba.conf to allow password authentication..."
        # Make backup of current config
        sudo cp "$PG_HBA_CONF" "${PG_HBA_CONF}.bak"
        
        # Add MD5 authentication line if it doesn't exist
        if ! sudo grep -q "host all all 0.0.0.0/0 md5" "$PG_HBA_CONF"; then
            echo "host all all 0.0.0.0/0 md5" | sudo tee -a "$PG_HBA_CONF"
        fi
        
        echo "Reloading PostgreSQL configuration..."
        sudo -u postgres psql -c "SELECT pg_reload_conf();"
        
        echo "Testing connection again..."
        if PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME -c "SELECT 'Connection successful';" &>/dev/null; then
            echo "✅ Connection test now successful after configuration update"
        else
            echo "❌ Connection still failing. Manual intervention required."
        fi
    else
        echo "❌ Cannot locate pg_hba.conf file at $PG_HBA_CONF"
    fi
fi

echo ""
echo "🎉 Database setup complete!"
echo "Database connection details:"
echo "- Host: localhost"
echo "- Port: $PGPORT"
echo "- Database: $DB_NAME"
echo "- Username: $DB_USER"
echo "- Password: $DB_PASSWORD"
echo ""
echo "Database URL format: postgresql://$DB_USER:$DB_PASSWORD@localhost:$PGPORT/$DB_NAME"
echo ""
echo "Save these details for your application configuration."
