#!/bin/bash

# This script updates the PostgreSQL service to use port 5432 instead of 5433

echo "Updating PostgreSQL service configuration to use port 5432..."

# Check if the PostgreSQL service file exists
SERVICE_FILE="/etc/systemd/system/postgresql.service"

if [ -f "$SERVICE_FILE" ]; then
    echo "Creating backup of current service file..."
    sudo cp "$SERVICE_FILE" "${SERVICE_FILE}.bak.$(date +%Y%m%d%H%M%S)"

    # Check if the service is using a specific port in ExecStart
    if grep -q "\\-p 5433" "$SERVICE_FILE"; then
        echo "Changing PostgreSQL service port from 5433 to 5432..."
        sudo sed -i 's/-p 5433/-p 5432/g' "$SERVICE_FILE"
        
        echo "Reloading systemd daemon..."
        sudo systemctl daemon-reload
        
        echo "Restarting PostgreSQL service..."
        sudo systemctl restart postgresql
        
        echo "PostgreSQL service now configured to use port 5432"
    else
        echo "PostgreSQL service file doesn't explicitly specify port 5433 in ExecStart"
        echo "Showing current service file content:"
        cat "$SERVICE_FILE"
    fi
else
    echo "PostgreSQL service file not found at $SERVICE_FILE"
    echo "Checking for alternative locations..."
    
    # Look for other possible locations
    if [ -f "/usr/lib/systemd/system/postgresql.service" ]; then
        echo "Found PostgreSQL service at /usr/lib/systemd/system/postgresql.service"
        SERVICE_FILE="/usr/lib/systemd/system/postgresql.service"
        
        echo "Creating backup of current service file..."
        sudo cp "$SERVICE_FILE" "${SERVICE_FILE}.bak.$(date +%Y%m%d%H%M%S)"
        
        # Check if the service is using a specific port
        if grep -q "\\-p 5433" "$SERVICE_FILE"; then
            echo "Changing PostgreSQL service port from 5433 to 5432..."
            sudo sed -i 's/-p 5433/-p 5432/g' "$SERVICE_FILE"
            
            echo "Reloading systemd daemon..."
            sudo systemctl daemon-reload
            
            echo "Restarting PostgreSQL service..."
            sudo systemctl restart postgresql
            
            echo "PostgreSQL service now configured to use port 5432"
        else
            echo "PostgreSQL service file doesn't explicitly specify port 5433"
            echo "Showing current service file content:"
            cat "$SERVICE_FILE"
        fi
    else
        echo "Could not find PostgreSQL service file"
        echo "Please check the status of the service to identify the file location:"
        echo "systemctl status postgresql"
    fi
fi

echo ""
echo "After changing the port, verify PostgreSQL is running with:"
echo "sudo systemctl status postgresql"
echo "pg_isready -h localhost -p 5432"
