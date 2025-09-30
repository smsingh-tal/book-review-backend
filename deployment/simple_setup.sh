#!/bin/bash
set -e

echo "=== Simple EC2 Setup Script ==="

# Use Amazon Linux's system Python3 (which has SSL support)
echo "Creating virtual environment with system Python3..."
python3 -m venv ~/app_venv

echo "Activating virtual environment..."
source ~/app_venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing poetry..."
pip install poetry

echo "Cloning application..."
cd ~
if [ -d "book-review-backend" ]; then
    echo "Application directory exists, updating..."
    cd book-review-backend
    git pull
else
    echo "Cloning application..."
    git clone https://github.com/smsingh-tal/book-review-backend.git
    cd book-review-backend
fi

echo "Installing application dependencies..."
poetry env use ~/app_venv/bin/python
poetry install --no-dev

echo "Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from example"
fi

echo "=== Setup Complete ==="
echo "To activate the environment: source ~/app_venv/bin/activate"
echo "To run the app: cd ~/book-review-backend && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000"

# Add activation to bashrc for convenience
if ! grep -q "source ~/app_venv/bin/activate" ~/.bashrc; then
    echo "source ~/app_venv/bin/activate" >> ~/.bashrc
    echo "Added virtual environment activation to ~/.bashrc"
fi
