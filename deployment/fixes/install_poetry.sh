#!/bin/bash

# Poetry Installation Helper for EC2
# This script installs Poetry for the current user and sets up PATH

echo "===== Poetry Installation Helper for EC2 ====="
echo "This script will install Poetry for the current user (ec2-user)"

# Check if Poetry is already installed
if command -v poetry &>/dev/null; then
    echo "✅ Poetry is already installed:"
    poetry --version
    echo "Nothing to do."
    exit 0
fi

# Install Poetry
echo "Installing Poetry..."
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH in .bashrc if not already there
if ! grep -q "PATH=\"\$HOME/.local/bin:\$PATH\"" ~/.bashrc; then
    echo "Adding Poetry to PATH in ~/.bashrc..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

# Add Poetry to current session PATH
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
echo "Verifying Poetry installation..."
if command -v poetry &>/dev/null; then
    echo "✅ Poetry installed successfully!"
    poetry --version
    echo ""
    echo "Poetry has been installed and added to your PATH."
    echo "You can now use 'poetry' commands directly."
    echo ""
    echo "If you open a new terminal, Poetry will be available automatically."
else
    echo "⚠️ Poetry was installed but is not in PATH."
    echo "Please run these commands manually:"
    echo ""
    echo "  export PATH=\"$HOME/.local/bin:\$PATH\""
    echo "  source ~/.bashrc"
    echo ""
    echo "Then verify with: poetry --version"
fi
