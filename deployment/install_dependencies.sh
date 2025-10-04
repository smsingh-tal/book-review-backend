#!/bin/bash

# Update system packages
sudo dnf update -y

# Install PostgreSQL 14 on Amazon Linux 2023
# Enable PostgreSQL repository
sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm

# Install PostgreSQL 14 packages
sudo dnf install -y postgresql14-server postgresql14 postgresql14-devel
sudo /usr/pgsql-14/bin/postgresql-14-setup initdb
sudo systemctl enable postgresql-14
sudo systemctl start postgresql-14

# Update PostgreSQL configuration to allow remote connections
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /var/lib/pgsql/14/data/postgresql.conf
echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a /var/lib/pgsql/14/data/pg_hba.conf

# Restart PostgreSQL to apply changes
sudo systemctl restart postgresql-14

# Install development tools and libraries required for Python compilation
sudo dnf install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel wget make

# Install Python 3.11+ as the primary Python version
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.11.8/Python-3.11.8.tgz
sudo tar xzf Python-3.11.8.tgz
cd Python-3.11.8
sudo ./configure --enable-optimizations
sudo make altinstall
sudo ln -sf /usr/local/bin/python3.11 /usr/bin/python3
sudo ln -sf /usr/local/bin/pip3.11 /usr/bin/pip3

# Install git and other required packages
sudo dnf install -y git gcc postgresql14-devel

# Create virtual environment with Python 3.11
python3.11 -m venv /home/ec2-user/venv

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
