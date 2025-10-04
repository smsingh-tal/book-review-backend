#!/bin/bash

# This script is designed to fix PostgreSQL socket issues on EC2
# It determines the correct socket location and creates a symlink if necessary

echo "Fixing PostgreSQL socket issues..."

# Find the PostgreSQL socket
echo "Searching for PostgreSQL socket..."
SOCKET_PATHS=(
    "/tmp/.s.PGSQL.5432" 
    "/var/run/postgresql/.s.PGSQL.5432" 
    "/run/postgresql/.s.PGSQL.5432"
    "/usr/local/pgsql/data/.s.PGSQL.5432"
)

FOUND_SOCKET=""
for SOCKET in "${SOCKET_PATHS[@]}"; do
    if [ -S "$SOCKET" ]; then
        FOUND_SOCKET="$SOCKET"
        echo "✅ Found PostgreSQL socket at: $FOUND_SOCKET"
        break
    fi
done

if [ -z "$FOUND_SOCKET" ]; then
    echo "Searching for PostgreSQL socket file on the system..."
    FOUND_SOCKET=$(sudo find / -name ".s.PGSQL.5432" -type s 2>/dev/null | head -n 1)
    
    if [ -n "$FOUND_SOCKET" ]; then
        echo "✅ Found PostgreSQL socket at: $FOUND_SOCKET"
    else
        echo "❌ Could not find PostgreSQL socket file"
        echo "Checking if PostgreSQL is running..."
        if sudo systemctl status postgresql &>/dev/null; then
            echo "✅ PostgreSQL service is running but socket not found"
            echo "This may indicate a custom configuration"
        else
            echo "❌ PostgreSQL service is not running"
            echo "Starting PostgreSQL service..."
            sudo systemctl start postgresql
        fi
        exit 1
    fi
fi

# Create standard socket directories if they don't exist
for DIR in "/run/postgresql" "/var/run/postgresql"; do
    if [ ! -d "$DIR" ]; then
        echo "Creating directory: $DIR"
        sudo mkdir -p "$DIR"
        sudo chmod 777 "$DIR"
    fi
done

# Create symlinks for common socket locations
SOCKET_DIR=$(dirname "$FOUND_SOCKET")
SOCKET_FILE=$(basename "$FOUND_SOCKET")

for DIR in "/run/postgresql" "/var/run/postgresql" "/tmp"; do
    if [ "$DIR" != "$SOCKET_DIR" ]; then
        TARGET="$DIR/$SOCKET_FILE"
        if [ ! -e "$TARGET" ]; then
            echo "Creating symlink from $FOUND_SOCKET to $TARGET"
            sudo ln -sf "$FOUND_SOCKET" "$TARGET"
        fi
    fi
done

echo "✅ PostgreSQL socket links created"
echo "Try connecting to PostgreSQL using: sudo -u postgres psql"
