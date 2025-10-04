#!/bin/bash

# PostgreSQL Connection Diagnostics
# This script helps diagnose PostgreSQL connection issues on EC2

echo "========== PostgreSQL Connection Diagnostics =========="
echo "Running diagnostics to help troubleshoot PostgreSQL connection issues..."

echo -e "\n1. Checking PostgreSQL service status:"
sudo systemctl status postgresql

echo -e "\n2. Checking PostgreSQL process:"
ps aux | grep postgres

echo -e "\n3. Checking PostgreSQL data directory:"
for dir in "/usr/local/pgsql/data" "/var/lib/pgsql/data" "/var/lib/postgresql/data"; do
    echo "Checking $dir:"
    if [ -d "$dir" ]; then
        ls -la $dir | head -n 5
        echo "Found postgresql.conf: $(find $dir -name "postgresql.conf" | wc -l)"
        echo "Found pg_hba.conf: $(find $dir -name "pg_hba.conf" | wc -l)"
    else
        echo "Directory does not exist"
    fi
done

echo -e "\n4. Searching for PostgreSQL socket files:"
for dir in "/tmp" "/var/run/postgresql" "/run/postgresql" "/usr/local/pgsql/data"; do
    find $dir -name ".s.PGSQL.*" -type s 2>/dev/null
done

echo -e "\n5. Checking PostgreSQL port:"
netstat -tuln | grep 5432

echo -e "\n6. Testing PostgreSQL connection methods:"

echo -e "\n   a. Socket connection:"
sudo -u postgres psql -c "SELECT 'Socket connection working';" 2>&1

echo -e "\n   b. TCP connection to localhost:"
sudo -u postgres psql -h localhost -c "SELECT 'TCP localhost connection working';" 2>&1

echo -e "\n   c. TCP connection to 127.0.0.1:"
sudo -u postgres psql -h 127.0.0.1 -c "SELECT 'TCP IP connection working';" 2>&1

echo -e "\n7. Checking PostgreSQL client configuration:"
which psql
psql --version

echo -e "\n8. Checking PostgreSQL log for errors:"
for log in "/usr/local/pgsql/data/log/postgresql.log" "/var/log/postgresql/postgresql.log"; do
    if [ -f "$log" ]; then
        echo "Last 10 lines of $log:"
        sudo tail -n 10 $log
    fi
done

echo -e "\n========== Diagnostics Complete =========="
echo "Based on these results, you may need to:"
echo "1. Fix the socket path using the fix_postgres_socket.sh script"
echo "2. Modify pg_hba.conf to allow connections"
echo "3. Ensure PostgreSQL is configured to listen on the expected port"
echo "4. Check if the PostgreSQL service is properly configured"
