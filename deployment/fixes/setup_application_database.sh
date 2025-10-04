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

# Detect which port PostgreSQL is running on
echo "Checking PostgreSQL connection..."

# First try direct connection with psql
if sudo -u postgres psql -c "SELECT 1;" &>/dev/null; then
    echo "✅ PostgreSQL direct connection successful"
    PGPORT=5432
elif pg_isready -h localhost -p 5432 &>/dev/null; then
    PGPORT=5432
    echo "✅ PostgreSQL detected on port 5432"
elif pg_isready -h localhost -p 5433 &>/dev/null; then
    PGPORT=5433
    echo "✅ PostgreSQL detected on port 5433"
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
if ! sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "Creating database with sudo -u postgres..."
    sudo -u postgres createdb "$DB_NAME"
    echo "✅ Database '$DB_NAME' created successfully"
else
    echo "✅ Database '$DB_NAME' already exists"
fi

# Create the user if it doesn't exist
echo "Creating database user '$DB_USER' if it doesn't exist..."
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    echo "✅ User '$DB_USER' created successfully"
else
    echo "✅ User '$DB_USER' already exists, updating password..."
    sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
fi

# Grant privileges to the user
echo "Granting privileges to user $DB_USER on database $DB_NAME..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
echo "✅ Privileges granted"

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
