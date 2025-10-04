#!/bin/bash

# Detect the Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
fi

echo "Detected OS: $OS $VER"

# Update system packages based on the detected OS
# Use full paths for more reliable command detection
if [ -x /usr/bin/dnf ] || [ -x /bin/dnf ]; then
    echo "Using dnf package manager..."
    sudo /usr/bin/dnf update -y || sudo /bin/dnf update -y
elif [ -x /usr/bin/yum ] || [ -x /bin/yum ]; then
    echo "Using yum package manager..."
    sudo /usr/bin/yum update -y || sudo /bin/yum update -y
elif [ -x /usr/bin/apt-get ] || [ -x /bin/apt-get ]; then
    echo "Using apt package manager..."
    sudo /usr/bin/apt-get update -y || sudo /bin/apt-get update -y
    sudo apt-get upgrade -y
else
    echo "No supported package manager found (dnf, yum, apt-get)"
    exit 1
fi

# Install PostgreSQL 15 based on the detected OS
if [[ "$OS" == *"Amazon Linux"* ]] && [[ "$VER" == "2023" ]]; then
    echo "Installing PostgreSQL for Amazon Linux 2023..."
    # For Amazon Linux 2023, use direct RPM installation method
    echo "Downloading PostgreSQL 15 RPM packages..."
    mkdir -p ~/postgres_install
    cd ~/postgres_install
    
    # Download PostgreSQL 15 packages directly
    curl -O https://download.postgresql.org/pub/repos/yum/15/redhat/rhel-9-x86_64/postgresql15-libs-15.6-1PGDG.rhel9.x86_64.rpm
    curl -O https://download.postgresql.org/pub/repos/yum/15/redhat/rhel-9-x86_64/postgresql15-15.6-1PGDG.rhel9.x86_64.rpm
    curl -O https://download.postgresql.org/pub/repos/yum/15/redhat/rhel-9-x86_64/postgresql15-server-15.6-1PGDG.rhel9.x86_64.rpm
    curl -O https://download.postgresql.org/pub/repos/yum/15/redhat/rhel-9-x86_64/postgresql15-contrib-15.6-1PGDG.rhel9.x86_64.rpm
    curl -O https://download.postgresql.org/pub/repos/yum/15/redhat/rhel-9-x86_64/postgresql15-devel-15.6-1PGDG.rhel9.x86_64.rpm
    
    # Install dependencies first
    sudo dnf install -y libicu || sudo yum install -y libicu
    
    # Install the packages
    sudo rpm -ivh postgresql15-libs-15.6-1PGDG.rhel9.x86_64.rpm
    sudo rpm -ivh postgresql15-15.6-1PGDG.rhel9.x86_64.rpm
    sudo rpm -ivh postgresql15-server-15.6-1PGDG.rhel9.x86_64.rpm
    sudo rpm -ivh postgresql15-contrib-15.6-1PGDG.rhel9.x86_64.rpm
    sudo rpm -ivh postgresql15-devel-15.6-1PGDG.rhel9.x86_64.rpm

    # Clean up
    cd ~
    rm -rf ~/postgres_install
    
    # Initialize the database
    sudo /usr/pgsql-15/bin/postgresql-15-setup initdb
    
    # Enable and start PostgreSQL
    sudo systemctl enable postgresql-15
    sudo systemctl start postgresql-15
    
    # Add PostgreSQL to PATH
    echo 'export PATH=$PATH:/usr/pgsql-15/bin' >> ~/.bashrc
    source ~/.bashrc
elif [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    # For Ubuntu or Debian
    echo "Installing PostgreSQL for Ubuntu/Debian..."
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    sudo apt-get update
    sudo apt-get -y install postgresql-15 postgresql-client-15 postgresql-server-dev-15
    sudo systemctl enable postgresql
    sudo systemctl start postgresql
else
    echo "Unsupported OS for PostgreSQL installation"
    exit 1
fi

# Update PostgreSQL configuration to allow remote connections
if [[ "$OS" == *"Amazon Linux"* ]] && [[ "$VER" == "2023" ]]; then
    sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /var/lib/pgsql/14/data/postgresql.conf
    echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a /var/lib/pgsql/14/data/pg_hba.conf
elif [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/14/main/postgresql.conf
    echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a /etc/postgresql/14/main/pg_hba.conf
fi

# Restart PostgreSQL to apply changes
if [[ "$OS" == *"Amazon Linux"* ]] && [[ "$VER" == "2023" ]]; then
    sudo systemctl restart postgresql-14
elif [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    sudo systemctl restart postgresql
fi

# Install development tools and libraries required for Python compilation
if command -v dnf &> /dev/null; then
    sudo dnf install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel wget make
elif command -v yum &> /dev/null; then
    sudo yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel wget make
elif command -v apt-get &> /dev/null; then
    sudo apt-get install -y gcc libssl-dev libbz2-dev libffi-dev zlib1g-dev wget make
else
    echo "Cannot install development tools - no supported package manager"
    exit 1
fi

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
if command -v dnf &> /dev/null; then
    sudo dnf install -y git gcc
    # PostgreSQL development package already installed in previous step for AL2023
    if [[ ! ("$OS" == *"Amazon Linux"* && "$VER" == "2023") ]]; then
        sudo dnf install -y postgresql-devel
    fi
elif command -v yum &> /dev/null; then
    sudo yum install -y git gcc
    # PostgreSQL development package already installed in previous step for AL2023
    if [[ ! ("$OS" == *"Amazon Linux"* && "$VER" == "2023") ]]; then
        if [[ "$OS" == *"Amazon Linux"* ]]; then
            sudo yum install -y postgresql14-devel
        else
            sudo yum install -y postgresql-devel
        fi
    fi
elif command -v apt-get &> /dev/null; then
    sudo apt-get install -y git gcc
    # Install PostgreSQL development package
    sudo apt-get install -y libpq-dev
else
    echo "Cannot install git and required packages - no supported package manager"
    exit 1
fi

# Determine the username
if [[ "$OS" == *"Amazon Linux"* ]]; then
    USERNAME="ec2-user"
elif [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    USERNAME="ubuntu"
else
    USERNAME=$(whoami)
fi

echo "Setting up for user: $USERNAME"

# Create virtual environment with Python 3.11
python3.11 -m venv /home/$USERNAME/venv

# Activate virtual environment and install poetry
source /home/$USERNAME/venv/bin/activate
pip install --upgrade pip
pip install poetry

# Add virtual environment activation to bashrc
echo "source /home/$USERNAME/venv/bin/activate" >> /home/$USERNAME/.bashrc

# Create app directory
mkdir -p /home/$USERNAME/app

# Set up the application
cd /home/$USERNAME/app
git clone https://github.com/smsingh-tal/book-review-backend.git .

# Copy the setup script
cp deployment/setup_app.sh /home/$USERNAME/
chmod +x /home/$USERNAME/setup_app.sh

# Add environment variables to bashrc
echo "export PATH=\"/home/$USERNAME/.local/bin:\$PATH\"" >> /home/$USERNAME/.bashrc
echo "export PYTHONPATH=\"/home/$USERNAME/app:\$PYTHONPATH\"" >> /home/$USERNAME/.bashrc

# Run the setup script as the correct user
if [ "$(whoami)" != "$USERNAME" ]; then
    sudo -u $USERNAME /home/$USERNAME/setup_app.sh
else
    /home/$USERNAME/setup_app.sh
fi
