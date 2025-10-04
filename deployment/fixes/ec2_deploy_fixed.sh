#!/bin/bash

# EC2 Poetry Setup and Deployment Script
# This script installs Poetry and sets it up properly on EC2
# Then deploys the book review application

# Set variables
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NC="\033[0m" # No Color

# Print section header
print_header() {
    echo ""
    echo -e "${YELLOW}==== $1 ====${NC}"
    echo ""
}

# 1. Set up Poetry properly
print_header "SETTING UP POETRY"

# Check if Poetry is installed
if command -v poetry &>/dev/null; then
    echo -e "${GREEN}✅ Poetry is already installed${NC}"
    poetry --version
else
    echo "Installing Poetry for current user (not using sudo)..."
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Add Poetry to PATH
    if [ -d "$HOME/.local/bin" ]; then
        echo "export PATH=\"$HOME/.local/bin:\$PATH\"" >> ~/.bashrc
        export PATH="$HOME/.local/bin:$PATH"
        echo -e "${GREEN}✅ Added Poetry to PATH in ~/.bashrc${NC}"
    fi
    
    # Verify Poetry installation
    if command -v poetry &>/dev/null; then
        echo -e "${GREEN}✅ Poetry installed successfully${NC}"
        poetry --version
    else
        echo -e "${RED}❌ Poetry installation failed or not in PATH${NC}"
        echo "Manual steps for Poetry setup:"
        echo "1. Add the following to your ~/.bashrc:"
        echo "   export PATH=\"$HOME/.local/bin:\$PATH\""
        echo "2. Run: source ~/.bashrc"
        echo "3. Verify with: poetry --version"
        
        # Ask user to continue
        read -p "Continue with manual Poetry setup? Press Enter when ready or Ctrl+C to abort"
    fi
fi

# 2. Configure PostgreSQL
print_header "CONFIGURING POSTGRESQL"

# Check PostgreSQL is running
if sudo systemctl is-active postgresql &>/dev/null; then
    echo -e "${GREEN}✅ PostgreSQL service is running${NC}"
else
    echo -e "${RED}❌ PostgreSQL service is not running${NC}"
    echo "Starting PostgreSQL..."
    sudo systemctl start postgresql
    if sudo systemctl is-active postgresql &>/dev/null; then
        echo -e "${GREEN}✅ PostgreSQL service started${NC}"
    else
        echo -e "${RED}❌ Failed to start PostgreSQL service${NC}"
        exit 1
    fi
fi

# Configure PostgreSQL for TCP connections
print_header "CONFIGURING POSTGRESQL FOR TCP CONNECTIONS"

# Find PostgreSQL data directory
PG_DATA_DIR="/usr/local/pgsql/data"
if [ ! -d "$PG_DATA_DIR" ]; then
    # Try to find it
    for dir in "/var/lib/pgsql/data" "/var/lib/postgresql/data"; do
        if [ -d "$dir" ]; then
            PG_DATA_DIR="$dir"
            break
        fi
    done
fi

echo "PostgreSQL data directory: $PG_DATA_DIR"

# Modify postgresql.conf to listen on all interfaces if needed
if [ -f "$PG_DATA_DIR/postgresql.conf" ]; then
    # Check if already listening
    if ! grep -q "listen_addresses = '*'" "$PG_DATA_DIR/postgresql.conf"; then
        echo "Configuring PostgreSQL to listen on all interfaces..."
        sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_DATA_DIR/postgresql.conf"
        sudo sed -i "s/listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_DATA_DIR/postgresql.conf"
    fi
    
    # Ensure pg_hba.conf allows password authentication
    echo "Configuring pg_hba.conf for password authentication..."
    if ! grep -q "host all all 0.0.0.0/0 md5" "$PG_DATA_DIR/pg_hba.conf"; then
        echo "host all all 0.0.0.0/0 md5" | sudo tee -a "$PG_DATA_DIR/pg_hba.conf"
    fi
    
    # Restart PostgreSQL to apply changes
    echo "Restarting PostgreSQL..."
    sudo systemctl restart postgresql
    sleep 2
    
    # Verify PostgreSQL is running
    if sudo systemctl is-active postgresql &>/dev/null; then
        echo -e "${GREEN}✅ PostgreSQL restarted successfully${NC}"
    else
        echo -e "${RED}❌ Failed to restart PostgreSQL${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Cannot find postgresql.conf${NC}"
    exit 1
fi

# 3. Set up the database and user
print_header "SETTING UP DATABASE"

# Create database
echo "Creating database..."
if ! sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname = 'book_review'" | grep -q 1; then
    sudo -u postgres psql -c "CREATE DATABASE book_review;"
    echo -e "${GREEN}✅ Database created${NC}"
else
    echo -e "${GREEN}✅ Database already exists${NC}"
fi

# Create user and grant privileges
echo "Creating database user..."
if ! sudo -u postgres psql -c "SELECT 1 FROM pg_roles WHERE rolname = 'book_user'" | grep -q 1; then
    sudo -u postgres psql -c "CREATE USER book_user WITH PASSWORD 'secure_password';"
    echo -e "${GREEN}✅ User created${NC}"
else
    sudo -u postgres psql -c "ALTER USER book_user WITH PASSWORD 'secure_password';"
    echo -e "${GREEN}✅ User password updated${NC}"
fi

# Grant privileges
echo "Granting privileges..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE book_review TO book_user;"
sudo -u postgres psql -d book_review -c "GRANT ALL ON SCHEMA public TO book_user;"
echo -e "${GREEN}✅ Privileges granted${NC}"

# 4. Install application dependencies
print_header "INSTALLING APPLICATION DEPENDENCIES"

# Install dependencies
poetry install --no-root
echo -e "${GREEN}✅ Dependencies installed${NC}"

# 5. Run database migrations
print_header "RUNNING DATABASE MIGRATIONS"

# Set environment variables
export PYTHONPATH=$(pwd)
export DATABASE_URL="postgresql://book_user:secure_password@localhost:5432/book_review"

# Run migrations
poetry run alembic upgrade head
echo -e "${GREEN}✅ Database migrations complete${NC}"

# 6. Load sample data
print_header "LOADING SAMPLE DATA"

poetry run python scripts/populate_books.py
echo -e "${GREEN}✅ Sample data loaded${NC}"

# 7. Start the application
print_header "STARTING APPLICATION"

# Create logs directory
mkdir -p logs

# Kill any existing instances
pkill -f "uvicorn app.main:app" || true

# Start the application
nohup poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info > logs/server.log 2>&1 &
APP_PID=$!
echo -e "${GREEN}✅ Application started with PID: $APP_PID${NC}"

# Display application access information
INSTANCE_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "YOUR_EC2_IP")
echo ""
echo -e "${YELLOW}==== APPLICATION ACCESS INFORMATION ====${NC}"
echo -e "API endpoint: ${GREEN}http://$INSTANCE_IP:8000${NC}"
echo -e "API documentation: ${GREEN}http://$INSTANCE_IP:8000/docs${NC}"
echo ""
echo "To stop the application: pkill -f 'uvicorn app.main:app'"
echo "To view logs: tail -f logs/server.log"
echo ""
echo -e "${GREEN}Deployment complete!${NC}"
