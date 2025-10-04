#!/bin/bash

# This script checks if a port is in use and kills the process if necessary

PORT=5432
echo "Checking if port $PORT is in use..."

# Check if the port is in use
if sudo netstat -tulpn | grep ":$PORT" > /dev/null; then
    echo "Port $PORT is in use. Getting details:"
    sudo netstat -tulpn | grep ":$PORT"
    
    # Get PID of process using the port
    PID=$(sudo lsof -t -i :$PORT)
    if [ -n "$PID" ]; then
        echo "Process ID using port $PORT: $PID"
        echo "Process details:"
        sudo ps -p $PID -o pid,ppid,user,cmd
        
        echo "Do you want to kill this process? (y/n)"
        read -p "> " response
        
        if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
            echo "Killing process $PID..."
            sudo kill -9 $PID
            echo "Process killed. Checking port again..."
            sudo netstat -tulpn | grep ":$PORT" || echo "Port $PORT is now free"
        else
            echo "Process not killed. You'll need to free up port $PORT before PostgreSQL can use it."
        fi
    else
        echo "Could not find process ID using port $PORT."
    fi
else
    echo "Port $PORT is not in use and is available for PostgreSQL."
fi
