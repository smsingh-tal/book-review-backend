#!/bin/bash

# Make all setup scripts executable

chmod +x deployment/fixes/setup_application_database.sh
chmod +x deployment/fixes/verify_database_setup.sh
chmod +x deployment/fixes/run_application_with_poetry.sh
chmod +x deployment/fixes/complete_setup.sh
chmod +x deployment/fixes/fix_postgres_socket.sh
chmod +x deployment/fixes/diagnose_postgres_connection.sh
chmod +x deployment/fixes/ec2_deploy.sh
chmod +x deployment/fixes/ec2_deploy_fixed.sh
chmod +x deployment/fixes/install_poetry.sh

echo "All scripts are now executable!"
