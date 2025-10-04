#!/bin/bash

# Error handling
set -e  # Exit on any error
trap 'echo "Error on line $LINENO. Exit code: $?" >&2' ERR

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Error logging function
error_log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Setup PostgreSQL database
setup_database() {
    log "Setting up PostgreSQL database..."
    
    # Detect the PostgreSQL version
    if systemctl list-units --all | grep -q postgresql-15; then
        PGSQL_VERSION="15"
    else
        PGSQL_VERSION="14"
    fi
    
    log "Using PostgreSQL version $PGSQL_VERSION"
    
    # Check if PostgreSQL is running
    if ! systemctl is-active --quiet postgresql-$PGSQL_VERSION; then
        error_log "PostgreSQL is not running. Starting PostgreSQL..."
        sudo systemctl start postgresql-$PGSQL_VERSION
    fi
    
    # Wait for PostgreSQL to be ready
    for i in {1..30}; do
        if sudo -u postgres /usr/pgsql-$PGSQL_VERSION/bin/psql -c '\l' >/dev/null 2>&1; then
            break
        fi
        log "Waiting for PostgreSQL to be ready... ($i/30)"
        sleep 1
    done

    # Create the database and set password
    if ! sudo -u postgres /usr/pgsql-$PGSQL_VERSION/bin/psql -lqt | cut -d \| -f 1 | grep -qw book_review; then
        log "Creating database and setting password..."
        sudo -u postgres /usr/pgsql-$PGSQL_VERSION/bin/psql -c "ALTER USER postgres WITH PASSWORD 'postgres';" || { error_log "Failed to set postgres password"; exit 1; }
        sudo -u postgres /usr/pgsql-$PGSQL_VERSION/bin/psql -c "CREATE DATABASE book_review;" || { error_log "Failed to create database"; exit 1; }
    else
        log "Database 'book_review' already exists"
    fi
    
    # Initialize the database schema
    cd /home/ec2-user/app || { error_log "Failed to change to app directory"; exit 1; }
    
    # Run database migrations using alembic
    log "Running database migrations..."
    poetry run alembic upgrade head || { error_log "Failed to run database migrations"; exit 1; }
    
    # Run any initial data setup scripts if they exist
    if [ -f "init_db.sql" ]; then
        log "Running init_db.sql..."
        sudo -u postgres /usr/pgsql-$PGSQL_VERSION/bin/psql -d book_review -f init_db.sql || { error_log "Failed to run init_db.sql"; exit 1; }
    fi
    
    if [ -f "init_books.sql" ]; then
        log "Running init_books.sql..."
        sudo -u postgres /usr/pgsql-$PGSQL_VERSION/bin/psql -d book_review -f init_books.sql || { error_log "Failed to run init_books.sql"; exit 1; }
        
        # Verify data was loaded correctly
        log "Verifying book data was loaded correctly..."
        BOOK_COUNT=$(sudo -u postgres /usr/pgsql-$PGSQL_VERSION/bin/psql -d book_review -t -c "SELECT COUNT(*) FROM books;")
        BOOK_COUNT=$(echo "$BOOK_COUNT" | tr -d '[:space:]')
        
        if [ "$BOOK_COUNT" -lt 1 ]; then
            error_log "Book data verification failed. No books found in the database."
            exit 1
        else
            log "Book data verification successful. Found $BOOK_COUNT books in the database."
        fi
    fi
    
    log "Database setup completed successfully"
}

# Setup application using Poetry
setup_application() {
    log "Setting up application environment..."
    
    # Install poetry if not already installed
    if ! command_exists poetry; then
        log "Installing Poetry..."
        curl -sSL https://install.python-poetry.org | python3 - || { error_log "Failed to install Poetry"; exit 1; }
        export PATH="/home/ec2-user/.local/bin:$PATH"
    else
        log "Poetry is already installed"
    fi
    
    # Verify Poetry installation
    if ! command_exists poetry; then
        error_log "Poetry installation failed or PATH not set correctly"
        exit 1
    fi
    
    cd /home/ec2-user/app || { error_log "Failed to change to app directory"; exit 1; }
    
    # Configure poetry to create virtual environment in project directory
    log "Configuring Poetry..."
    poetry config virtualenvs.in-project true || { error_log "Failed to configure Poetry"; exit 1; }
    
    # Clean any existing virtual environment
    if [ -d ".venv" ]; then
        log "Removing existing virtual environment..."
        rm -rf .venv
    fi
    
    # Install dependencies with retry mechanism
    log "Installing dependencies..."
    for i in {1..3}; do
        if poetry install --no-dev; then
            break
        fi
        if [ $i -eq 3 ]; then
            error_log "Failed to install dependencies after 3 attempts"
            exit 1
        fi
        log "Retry $i/3: Installing dependencies..."
        sleep 5
    done
    
    # Create necessary directories
    log "Creating upload directory..."
    mkdir -p uploads || { error_log "Failed to create uploads directory"; exit 1; }
    
    # Verify the installation and Python version
    if ! poetry run python -c "import sys, fastapi; assert sys.version_info >= (3, 11), 'Python 3.11+ required'; print(f'Using Python {sys.version}')" 2>/dev/null; then
        error_log "FastAPI installation verification failed or Python version is less than 3.11"
        exit 1
    fi
    
    log "Application setup completed successfully"
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    # Stop existing service if it exists
    if systemctl is-active --quiet bookreview; then
        log "Stopping existing bookreview service..."
        sudo systemctl stop bookreview || { error_log "Failed to stop existing service"; exit 1; }
    fi
    
    # Create the service file
    log "Creating service file..."
    cat << EOF | sudo tee /etc/systemd/system/bookreview.service
[Unit]
Description=Book Review Backend Service
After=network.target postgresql-${PGSQL_VERSION}.service
Requires=postgresql-${PGSQL_VERSION}.service

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/app
Environment="PATH=/home/ec2-user/.local/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/home/ec2-user/app"
Environment="PYTHONHOME=/usr/local/bin/python3.11"
ExecStart=/home/ec2-user/.local/bin/poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
StartLimitIntervalSec=60
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
EOF

    # Verify service file creation
    if [ ! -f "/etc/systemd/system/bookreview.service" ]; then
        error_log "Failed to create service file"
        exit 1
    fi

    # Reload systemd and enable the service
    log "Reloading systemd daemon..."
    sudo systemctl daemon-reload || { error_log "Failed to reload systemd"; exit 1; }
    
    log "Enabling bookreview service..."
    sudo systemctl enable bookreview || { error_log "Failed to enable service"; exit 1; }
    
    log "Starting bookreview service..."
    sudo systemctl start bookreview || { error_log "Failed to start service"; exit 1; }
    
    # Verify service is running
    sleep 5
    if ! systemctl is-active --quiet bookreview; then
        error_log "Service failed to start. Check logs with: journalctl -u bookreview"
        exit 1
    fi
    
    log "Systemd service created and started successfully"
}

# Verify environment
verify_environment() {
    log "Verifying environment..."
    
    # Check if service is running
    if systemctl is-active --quiet bookreview; then
        log "Service is running"
        
        # Test API endpoint
        if curl -s http://localhost:8000/docs >/dev/null; then
            log "API is responding"
        else
            error_log "API is not responding"
            exit 1
        fi
    else
        error_log "Service is not running"
        exit 1
    fi
}

# Main setup sequence
main() {
    log "Starting setup process..."
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        error_log "Please do not run this script as root"
        exit 1
    fi
    
    setup_database
    setup_application
    create_systemd_service
    verify_environment
    
    log "Setup completed successfully!"
    log "You can access the API at: http://localhost:8000"
    log "API documentation is available at: http://localhost:8000/docs"
}

# Run main setup
main
