# Book Review Backend

A FastAPI-based backend service for book reviews and recommendations.

## Environment Setup

1. Create a copy of `.env.template` as `.env`:
   ```bash
   cp .env.template .env
   ```

2. Update the `.env` file with your actual values:
   - `OPENAI_API_KEY`: Get from [OpenAI Dashboard](https://platform.openai.com/account/api-keys)
   - `SECRET_KEY`: Generate a secure random key
   - `DB_PASSWORD`: Your local PostgreSQL password

   Never commit the `.env` file with actual values to version control!

3. For production deployment:
   - Set environment variables directly in your deployment platform
   - Do not use the `.env` file in production

## Development Setup

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Run the development server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

3. Run tests:
   ```bash
   poetry run pytest
   ```
