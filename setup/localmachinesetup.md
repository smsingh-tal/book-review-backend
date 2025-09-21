# Local Development Environment Setup Guide

## Prerequisites Installation

### 1. Command Line Tools
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

### 2. Package Manager
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 3. Version Control
```bash
# Install Git
brew install git

# Configure Git (replace with your details)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Backend Setup

### 1. Python Environment
```bash
# Install Python version manager
brew install pyenv

# Install Python 3.11
pyenv install 3.11

# Set global Python version
pyenv global 3.11

# Install Poetry for dependency management
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. PostgreSQL Database
```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Add PostgreSQL to your PATH (for Apple Silicon Macs)
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Create postgres superuser and set password
createuser -s postgres
psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';"

# Create database
dropdb book_review_db || true
createdb -U postgres book_review_db

# Verify database creation and connection
psql -U postgres -d book_review_db -c "\l"

# Test connection with credentials
psql "postgresql://postgres:postgres@localhost:5432/book_review_db" -c "SELECT 1;"
```

### 3. Backend Dependencies
```bash
# Navigate to backend directory
cd book-review-backend

# Initialize Poetry and create virtual environment
poetry init
poetry install

# Install required packages
poetry add fastapi sqlalchemy alembic psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart pytest python-dotenv uvicorn
```

## Frontend Setup

### 1. Node.js Environment
```bash
# Install Node Version Manager (nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash

# Load nvm in current shell
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# Add these lines to your ~/.zshrc or ~/.bashrc for permanent setup
echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.zshrc
echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.zshrc
echo '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"' >> ~/.zshrc

# Install Node.js v20 (required for Vite)
nvm install 20
nvm use 20
nvm alias default 20

# Verify installation
node --version # Should show v20.x.x
npm --version  # Should show v10.x.x
```

### 2. Frontend Project Setup
```bash
# Create React project with Vite
npm create vite@latest book-review-frontend -- --template react-ts

# Navigate to frontend directory and install dependencies
cd book-review-frontend
npm install

# Install required packages
npm install @mui/material @emotion/react @emotion/styled @reduxjs/toolkit react-redux axios react-router-dom @mui/icons-material

# Start the development server
npm run dev    # Access the app at http://localhost:5173
```

## Docker Setup

### 1. Install Docker
```bash
# Install Docker Desktop for Mac
brew install --cask docker

# Start Docker Desktop
open -a Docker
```

### 2. Create Docker Configuration

Create `docker-compose.yml` in the root directory:

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: book_review_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./book-review-backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./book-review-backend:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/book_review_db
    depends_on:
      - postgres

  frontend:
    build: ./book-review-frontend
    volumes:
      - ./book-review-frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

## Environment Configuration

### 1. Backend Environment Variables
Create `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/book_review_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your-openai-api-key
```

### 2. Frontend Environment Variables
Create `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

## Project Structure Setup

```bash
# Create project structure
mkdir -p book-review-backend/app/{api,core,db,schemas,services,utils}
mkdir -p book-review-frontend/src/{components,features,hooks,layouts,services,store,types,utils}
```

## Running the Application

### Option 1: Running with Docker
```bash
# Build and start all services
docker-compose up --build
```

### Option 2: Running Services Individually

#### Backend:
```bash
cd book-review-backend
poetry run uvicorn app.main:app --reload
```

#### Frontend:
```bash
cd book-review-frontend
npm run dev
```

#### Database:
```bash
# Start PostgreSQL service
brew services start postgresql@15
```

## Development Tools

### 1. VS Code Extensions
Install the following VS Code extensions:
- Python
- Pylance
- ESLint
- Prettier
- Docker
- GitLens
- Error Lens
- Python Test Explorer

### 2. Code Formatting Tools
```bash
# Backend
poetry add --dev black isort flake8

# Frontend
npm install --save-dev prettier eslint
```

## Testing Setup

### Backend Tests
```bash
# Install pytest and related packages
poetry add --dev pytest pytest-asyncio httpx

# Run tests
poetry run pytest
```

### Frontend Tests
```bash
# Install testing libraries
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Run tests
npm test
```

## Next Steps

1. Initialize Git repository:
```bash
git init
git add .
git commit -m "Initial project setup"
```

2. Start implementing tasks in order:
   - 001_DB_SETUP
   - 002_AUTH_SERVICE
   - 003_BOOK_SERVICE
   - And so on...

3. For each task:
   - Create a new branch
   - Implement the feature
   - Write tests
   - Create PR for review

## Configuration Examples

### 1. Frontend Configuration Examples

#### Redux Store Setup (src/store/index.ts)
```typescript
import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice';
import booksReducer from '../features/books/booksSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    books: booksReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

#### API Client Setup (src/services/api.ts)
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

#### Environment Types (src/types/env.d.ts)
```typescript
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

### 2. Backend Configuration Examples

#### FastAPI App Setup (app/main.py)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.v1.api import api_router

app = FastAPI(title="Book Review API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
```

#### Database Configuration (app/core/config.py)
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
```

#### SQLAlchemy Models Example (app/db/models.py)
```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
```

## Troubleshooting

### Common Issues and Solutions

1. PostgreSQL Connection Issues:
```bash
# Restart PostgreSQL
brew services restart postgresql@15

# Check PostgreSQL status
brew services list | grep postgresql

# Check if PostgreSQL is listening
lsof -i :5432

# Reset PostgreSQL password
psql postgres
\password postgres
```

2. Node.js/npm Issues:
```bash
# Clear npm cache
npm cache clean -f

# Clear node modules and package lock
rm -rf node_modules package-lock.json
npm install

# If nvm is not found after installation
source ~/.nvm/nvm.sh
# Add to ~/.zshrc or ~/.bashrc if not already there
echo 'source ~/.nvm/nvm.sh' >> ~/.zshrc

# If getting EACCES permission errors
sudo chown -R $USER:$GROUP ~/.npm
sudo chown -R $USER:$GROUP ~/.config
```

3. Python/Poetry Issues:
```bash
# If poetry command not found
curl -sSL https://install.python-poetry.org | python3 -
export PATH="/Users/$USER/.local/bin:$PATH"

# Recreate virtual environment
poetry env remove python
poetry install

# If dependencies are conflicting
poetry update
poetry install --sync

# Show poetry environment info
poetry env info
```

4. FastAPI Development Server Issues:
```bash
# Check if port 8000 is already in use
lsof -i :8000
kill -9 <PID>

# Run with debug mode
poetry run uvicorn app.main:app --reload --debug

# Check logs
poetry run uvicorn app.main:app --reload --log-level debug
```

5. Vite Development Server Issues:
```bash
# If port 5173 is in use
lsof -i :5173
kill -9 <PID>

# Clear vite cache
rm -rf node_modules/.vite

# Run with debug logging
npm run dev -- --debug

# Run on different port
npm run dev -- --port 3000
```

### Environment Verification

Run these commands to verify your setup:

```bash
# Node.js environment
node --version  # Should be v20.x.x
npm --version   # Should be v10.x.x
nvm current     # Should show v20.x.x

# Python environment
python --version  # Should be Python 3.11.x
poetry --version  # Should show poetry version
poetry env list   # Should show active environment

# PostgreSQL
psql --version    # Should show PostgreSQL 15.x
psql -l          # Should list book_review_db

# Docker
docker --version
docker-compose --version
```

### Security Checklist

1. Database:
   - [ ] PostgreSQL password is set
   - [ ] Database user has limited privileges
   - [ ] Database is not exposed to public network

2. Backend:
   - [ ] JWT secret key is secure and not in version control
   - [ ] CORS is properly configured
   - [ ] Environment variables are set
   - [ ] Password hashing is implemented

3. Frontend:
   - [ ] API URL is configured correctly
   - [ ] JWT token is stored securely
   - [ ] Environment variables are set
   - [ ] API requests include proper headers
