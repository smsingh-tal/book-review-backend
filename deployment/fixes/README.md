# PostgreSQL Fixes

This directory contains scripts for fixing and managing PostgreSQL on Amazon Linux 2023.

## Scripts

### Configuration Fixes
- `fix_postgresql_config.sh`: Cleans up the PostgreSQL configuration file, removing duplicate entries and creating a properly formatted config
- `fix_postgresql_config_direct.sh`: Simpler direct fix for PostgreSQL configuration issues
- `update_postgresql_port.sh`: Updates the PostgreSQL service to use port 5432 instead of 5433
- `setup_postgresql_service.sh`: Sets up PostgreSQL to run in the background as a system service

### Installation & Verification
- `install_pg_client.sh`: Installs PostgreSQL client tools needed for commands like psql, pg_isready, etc.
- `verify_postgresql.sh`: Verifies that PostgreSQL is running correctly after configuration fixes

### Database Setup
- `setup_application_database.sh`: Sets up a database and user for the book-review-backend application

### Utilities
- `check_and_free_port.sh`: Checks if a port (default 5432) is in use and optionally kills the process
- `test_postgresql.sh`: Comprehensive script to test if PostgreSQL is running correctly
- `quick_check_postgresql.sh`: Fast check to verify if PostgreSQL is running properly

## Usage

Transfer these scripts to your EC2 instance and use one of the following options:

### Option 1: One-Step Setup (Recommended)

Run the all-in-one setup script that performs all steps in sequence:

```bash
chmod +x setup_all.sh
sudo ./setup_all.sh
```

### Option 2: Step-by-Step Setup

If you prefer to run each step individually:

1. First, fix the PostgreSQL configuration:
   ```
   chmod +x fix_postgresql_config.sh
   sudo ./fix_postgresql_config.sh
   ```

2. Update PostgreSQL service to use port 5432 (standard port):
   ```
   chmod +x update_postgresql_port.sh
   sudo ./update_postgresql_port.sh
   ```

3. Setup PostgreSQL as a background service:
   ```
   chmod +x setup_postgresql_service.sh
   sudo ./setup_postgresql_service.sh
   ```

4. Install client tools if needed:
   ```
   chmod +x install_pg_client.sh
   sudo ./install_pg_client.sh
   ```

5. Verify PostgreSQL is running:
   ```
   chmod +x verify_postgresql.sh
   ./verify_postgresql.sh
   ```

6. Set up the application database:
   ```
   chmod +x setup_application_database.sh
   ./setup_application_database.sh
   ```

## Testing PostgreSQL

To test if PostgreSQL is running correctly:

```bash
chmod +x test_postgresql.sh
./test_postgresql.sh
```

This script performs comprehensive tests:
- Checks if the PostgreSQL service is running
- Identifies which port PostgreSQL is listening on
- Tests connections using pg_isready and psql
- Checks for the existence of the application database and user
- Examines logs for any errors

## Troubleshooting

If you encounter issues:

1. Run the test script first: `./test_postgresql.sh`
2. Check PostgreSQL logs: `sudo cat /tmp/postgresql.log`
3. Check if the port is available: `./check_and_free_port.sh`
4. Check if the PostgreSQL service is running: `sudo systemctl status postgresql`
