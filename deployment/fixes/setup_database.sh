#!/bin/bash

# This script sets up the database and user for the book-review-backend application

# Default values
DB_NAME="book_review"
DB_USER="book_user"
DB_PASSWORD="secure_password" # You should change this to a secure password

# Check if PostgreSQL client tools are installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL client tools not found"
    echo "Please install them first with: sudo dnf install -y postgresql15"
    exit 1
fi

# Check if PostgreSQL server is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL server is not running or not accepting connections"
    echo "Please make sure the PostgreSQL server is running"
    exit 1
fi

echo "Setting up database for book-review-backend application..."

# Create the database if it doesn't exist
if ! psql -h localhost -p 5432 -U postgres -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "Creating database: $DB_NAME"
    createdb -h localhost -p 5432 -U postgres "$DB_NAME"
    echo "✅ Database created successfully"
else
    echo "✅ Database '$DB_NAME' already exists"
fi

# Create the user if it doesn't exist
if ! psql -h localhost -p 5432 -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo "Creating user: $DB_USER"
    psql -h localhost -p 5432 -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    echo "✅ User created successfully"
else
    echo "✅ User '$DB_USER' already exists, updating password"
    psql -h localhost -p 5432 -U postgres -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
fi

# Grant privileges
echo "Granting privileges to user $DB_USER on database $DB_NAME"
psql -h localhost -p 5432 -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
psql -h localhost -p 5432 -U postgres -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
echo "✅ Privileges granted"

echo ""
echo "🎉 Database setup complete!"
echo "Connection details:"
echo "- Host: localhost"
echo "- Port: 5432"
echo "- Database: $DB_NAME"
echo "- User: $DB_USER"
echo "- Password: $DB_PASSWORD"
echo ""
echo "Database URL format: postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
echo "You can test the connection with:"
echo "psql -h localhost -p 5432 -d $DB_NAME -U $DB_USER"
