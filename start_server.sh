#!/bin/bash

# Export environment variables
export PYTHONPATH=/Users/shivs/Documents/Talentica/ailearning/book-review-backend
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
export JWT_SECRET="your-secret-key"  # Change this in production
export JWT_ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES=30

# Run the FastAPI server using uvicorn
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
