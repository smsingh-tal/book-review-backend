#!/bin/bash

# This script runs all the necessary steps to set up PostgreSQL and the book-review-backend database

echo "===== POSTGRESQL COMPLETE SETUP SCRIPT ====="
echo "This script will:"
echo "1. Fix PostgreSQL configuration"
echo "2. Update PostgreSQL service port to 5432 (if needed)"
echo "3. Set up PostgreSQL to run as a background service"
echo "4. Install PostgreSQL client tools"
echo "5. Set up the book-review application database"
echo ""
echo "Press Enter to continue or Ctrl+C to cancel..."
read -r

# Step 1: Fix PostgreSQL configuration
echo ""
echo "===== STEP 1: Fixing PostgreSQL configuration ====="
chmod +x fix_postgresql_config.sh
sudo ./fix_postgresql_config.sh

# Step 2: Update PostgreSQL service port to 5432 (if needed)
echo ""
echo "===== STEP 2: Updating PostgreSQL service port ====="
chmod +x update_postgresql_port.sh
sudo ./update_postgresql_port.sh

# Step 3: Set up PostgreSQL as a background service
echo ""
echo "===== STEP 3: Setting up PostgreSQL as a background service ====="
chmod +x setup_postgresql_service.sh
sudo ./setup_postgresql_service.sh

# Step 4: Install PostgreSQL client tools
echo ""
echo "===== STEP 4: Installing PostgreSQL client tools ====="
chmod +x install_pg_client.sh
sudo ./install_pg_client.sh

# Step 5: Set up the book-review application database
echo ""
echo "===== STEP 5: Setting up application database ====="
chmod +x setup_application_database.sh
./setup_application_database.sh

echo ""
echo "===== SETUP COMPLETE ====="
echo "PostgreSQL has been configured and is running in the background"
echo "The book_review database has been set up for your application"
echo ""
echo "To check PostgreSQL status at any time: sudo systemctl status postgresql"
echo "To connect to your database: psql -h localhost -U book_user -d book_review"
echo ""
echo "Remember to update your application's database connection settings"
