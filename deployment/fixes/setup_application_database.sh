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
if pg_isready -h localhost -p 5432 &>/dev/null; then
    PGPORT=5432
    echo "✅ PostgreSQL detected on port 5432"
elif pg_isready -h localhost -p 5433 &>/dev/null; then
    PGPORT=5433
    echo "✅ PostgreSQL detected on port 5433"
else
    echo "❌ PostgreSQL server is not running or not accepting connections"
    echo "Please start PostgreSQL with: sudo systemctl start postgresql"
    exit 1
fi

# Create the database if it doesn't exist
echo "Creating database '$DB_NAME' if it doesn't exist..."
if ! psql -h localhost -p $PGPORT -U postgres -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    createdb -h localhost -p $PGPORT -U postgres "$DB_NAME"
    echo "✅ Database '$DB_NAME' created successfully"
else
    echo "✅ Database '$DB_NAME' already exists"
fi

# Create the user if it doesn't exist
echo "Creating database user '$DB_USER' if it doesn't exist..."
if ! psql -h localhost -p $PGPORT -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    psql -h localhost -p $PGPORT -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    echo "✅ User '$DB_USER' created successfully"
else
    echo "✅ User '$DB_USER' already exists, updating password..."
    psql -h localhost -p $PGPORT -U postgres -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
fi

# Grant privileges to the user
echo "Granting privileges to user $DB_USER on database $DB_NAME..."
psql -h localhost -p $PGPORT -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
psql -h localhost -p $PGPORT -U postgres -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
echo "✅ Privileges granted"

# Test the connection with the new user
echo "Testing connection with the new user..."
if PGPASSWORD=$DB_PASSWORD psql -h localhost -p $PGPORT -U $DB_USER -d $DB_NAME -c "SELECT 'Connection successful';" &>/dev/null; then
    echo "✅ Connection test successful"
else
    echo "⚠️ Connection test failed. Check PostgreSQL client authentication settings."
    echo "You may need to edit /usr/local/pgsql/data/pg_hba.conf to allow password authentication"
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
