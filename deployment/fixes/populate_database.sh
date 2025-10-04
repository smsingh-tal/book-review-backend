#!/bin/bash
set -e

echo "Starting database population..."

# Go to the project root directory
cd "$(dirname "$0")/../.." || exit 1
echo "Working directory: $(pwd)"

# Make sure environment variables are set
if [ ! -f .env ]; then
    echo "Creating .env file with database URL"
    echo "export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/book_review" > .env
fi

# Source the environment variables
source .env
echo "Environment variables loaded"

# Set PYTHONPATH
export PYTHONPATH=$PWD
echo "PYTHONPATH set to $PYTHONPATH"

# Populate books from the script
echo "Populating books table..."
python scripts/populate_books.py

# Check if the populate script was successful
if [ $? -eq 0 ]; then
    echo "Database populated successfully!"
    
    # Count the books in the database
    BOOK_COUNT=$(sudo -u postgres /usr/local/pgsql/bin/psql -d book_review -c "SELECT COUNT(*) FROM books;" -t | tr -d ' ')
    echo "Book count in database: $BOOK_COUNT"
else
    echo "Error: Failed to populate the database."
    exit 1
fi

echo "Database population completed successfully!"
