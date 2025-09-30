#!/bin/bash

# Fix for alembic config import issue on EC2
# This script updates the config.py file to use the correct imports

set -e

echo "=== Fixing alembic config import issue ==="

CONFIG_FILE="app/core/config.py"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
fi

echo "Creating backup of config.py..."
cp "$CONFIG_FILE" "${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"

echo "Updating imports in config.py..."

# Replace pydantic_settings import with pydantic
sed -i 's/from pydantic_settings import BaseSettings/from pydantic import BaseModel\nfrom dotenv import load_dotenv/' "$CONFIG_FILE"

# Replace BaseSettings with BaseModel
sed -i 's/class Settings(BaseSettings):/class Settings(BaseModel):/' "$CONFIG_FILE"

# Add load_dotenv() call after imports
sed -i '/from dotenv import load_dotenv/a\\n# Load environment variables from .env file\nload_dotenv()' "$CONFIG_FILE"

echo "✅ Config file updated successfully!"

echo "Verifying the changes..."
head -15 "$CONFIG_FILE"

echo ""
echo "Now try running: alembic upgrade head"
