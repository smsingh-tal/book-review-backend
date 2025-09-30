#!/bin/bash

# Script to fix dependencies for Python 3.7 deployment
echo "Fixing dependencies for Python 3.7 compatibility..."

# Backup original pyproject.toml
cp pyproject.toml pyproject.toml.backup

# Create a temporary pyproject.toml with Python 3.7 compatible dependencies
cat > pyproject.toml << 'EOF'
[tool.poetry]
name = "book-review-backend"
version = "0.1.0"
description = "Book Review Platform Backend"
authors = ["Shiv S <shiv.singh@talentica.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = ">=3.7,<4.0"
fastapi = ">=0.68.0,<0.95.0"
uvicorn = {extras = ["standard"], version = ">=0.15.0,<0.23.0"}
sqlalchemy = ">=1.4.0,<2.0.0"
alembic = ">=1.7.0,<1.14.0"
psycopg2-binary = ">=2.8.6,<3.0.0"
python-jose = {extras = ["cryptography"], version = ">=3.3.0,<4.0.0"}
passlib = {extras = ["bcrypt"], version = ">=1.7.4,<2.0.0"}
python-multipart = ">=0.0.5,<0.0.7"
httpx = ">=0.24.0,<0.25.0"
pydantic-settings = ">=1.0.0,<2.0.0"
pillow = ">=8.0.0,<10.0.0"
pytest = ">=6.0.0,<8.0.0"
pytest-asyncio = ">=0.18.0,<1.0.0"
pydantic = {extras = ["email"], version = ">=1.8.0,<2.0.0"}
pytest-aiohttp = ">=0.3.0,<1.0.0"
email-validator = ">=1.1.0,<2.0.0"
requests = ">=2.25.0,<3.0.0"
redis = ">=3.5.0,<5.0.0"
aiohttp = ">=3.7.0,<4.0.0"
openai = ">=0.27.0,<1.0.0"
numpy = ">=1.19.0,<1.25.0"
python-dotenv = ">=0.19.0,<2.0.0"
scikit-learn = ">=0.24.0,<1.2.0"

[tool.poetry.group.dev.dependencies]
pytest = ">=6.0.0,<8.0.0"
black = ">=21.0.0,<23.0.0"
isort = ">=5.0.0,<6.0.0"
flake8 = ">=3.8.0,<7.0.0"
pytest-asyncio = ">=0.18.0,<1.0.0"

[tool.pytest.ini_options]
filterwarnings = ["ignore::DeprecationWarning:passlib.utils"]
testpaths = ["tests"]
pythonpath = ["."]

[build-system]
requires = ["poetry-core>=1.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
EOF

echo "Dependencies fixed for Python 3.7. Original file backed up as pyproject.toml.backup"
echo "Now run: poetry lock --no-update && poetry install --only main"
