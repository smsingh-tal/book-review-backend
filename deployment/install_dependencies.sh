#!/bin/bash

# Update system packages
sudo yum update -y

# Install PostgreSQL
sudo yum install -y postgresql postgresql-server postgresql-devel postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Update PostgreSQL configuration to allow remote connections
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /var/lib/pgsql/data/postgresql.conf
echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a /var/lib/pgsql/data/pg_hba.conf

# Restart PostgreSQL to apply changes
sudo systemctl restart postgresql

# Install Python 3 and pip (system python3 has SSL support)
sudo yum install -y python3 python3-pip

# Install git and other required packages
sudo yum install -y git gcc python3-devel postgresql-devel

# Create virtual environment with system Python3
python3 -m venv /home/ec2-user/venv

# Activate virtual environment and install poetry
source /home/ec2-user/venv/bin/activate
pip install --upgrade pip
pip install poetry

# Add virtual environment activation to bashrc
echo 'source /home/ec2-user/venv/bin/activate' >> ~/.bashrc

# Create app directory
mkdir -p /home/ec2-user/app

# Set up the application
cd /home/ec2-user/app
git clone https://github.com/smsingh-tal/book-review-backend.git .

# Copy the setup script
cp deployment/setup_app.sh /home/ec2-user/
chmod +x /home/ec2-user/setup_app.sh

# Add environment variables to bashrc
echo 'export PATH="/home/ec2-user/.local/bin:$PATH"' >> /home/ec2-user/.bashrc
echo 'export PYTHONPATH="/home/ec2-user/app:$PYTHONPATH"' >> /home/ec2-user/.bashrc

# Run the setup script as ec2-user
sudo -u ec2-user /home/ec2-user/setup_app.sh
