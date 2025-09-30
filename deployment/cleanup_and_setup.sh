#!/bin/bash
set -e

echo "=== Cleaning up previous installations ==="

# Remove Python source code directory (saves ~500MB)
echo "Removing Python source code..."
rm -rf ~/Python-3.11.5*

# Remove custom compiled Python installations
echo "Removing custom Python installations..."
sudo rm -rf /usr/local/lib/python3.11 2>/dev/null || true
sudo rm -f /usr/local/bin/python3.11 2>/dev/null || true
sudo rm -f /usr/local/bin/pip3.11 2>/dev/null || true

# Clean up broken symlinks
echo "Cleaning up broken symlinks..."
sudo find /usr/bin -name "python3.11*" -type l -delete 2>/dev/null || true
sudo find /usr/lib64 -name "libpython3.11*" -delete 2>/dev/null || true

# Clean up cache directories
echo "Cleaning up cache directories..."
rm -rf ~/.cache/pip 2>/dev/null || true
rm -rf ~/.local/share/pypoetry 2>/dev/null || true
rm -rf ~/.cache/pypoetry 2>/dev/null || true
rm -rf ~/.local/poetry 2>/dev/null || true

# Clean package cache
echo "Cleaning package cache..."
sudo yum clean all

# Remove temporary files
sudo rm -rf /tmp/* 2>/dev/null || true

echo "=== Setting up clean environment ==="

# Check system Python3 has SSL
echo "Testing system Python3 SSL support..."
python3 -c "import ssl; print('✓ SSL works:', ssl.OPENSSL_VERSION)"

# Create clean virtual environment
echo "Creating virtual environment..."
python3 -m venv ~/app_venv

# Activate virtual environment
echo "Activating virtual environment..."
source ~/app_venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install poetry
echo "Installing poetry..."
pip install poetry

# Test poetry
echo "Testing poetry..."
poetry --version

# Add activation to bashrc for convenience
if ! grep -q "source ~/app_venv/bin/activate" ~/.bashrc; then
    echo "source ~/app_venv/bin/activate" >> ~/.bashrc
    echo "✓ Added virtual environment activation to ~/.bashrc"
fi

echo "=== Setup complete! ==="
echo ""
echo "Virtual environment created at ~/app_venv"
echo "To activate manually: source ~/app_venv/bin/activate"
echo "Poetry version: $(poetry --version)"
echo ""
echo "Current disk usage:"
df -h /
