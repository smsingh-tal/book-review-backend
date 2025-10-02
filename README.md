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

## API Endpoints

The API is available at the following base URL: `/v1`

### Main Endpoints

- Authentication: `/v1/auth`
  - POST `/v1/auth/register`: Register a new user
  - POST `/v1/auth/login`: Log in an existing user
  - POST `/v1/auth/logout`: Log out the current user

- Books: `/v1/books`
  - GET `/v1/books`: List all books
  - GET `/v1/books/{book_id}`: Get book details

- Reviews: `/v1/reviews`
  - POST `/v1/reviews`: Create a new review
  - GET `/v1/reviews?book_id={book_id}`: Get reviews for a book
  - PUT `/v1/reviews/{review_id}`: Update a review
  - DELETE `/v1/reviews/{review_id}`: Delete a review

- Recommendations: `/v1/recommendations`
  - POST `/v1/recommendations`: Get personalized book recommendations

- Profile: `/v1/profile`
  - GET `/v1/profile/me`: Get current user profile
  - PUT `/v1/profile/me`: Update user profile
  - GET `/v1/profile/me/favorites`: Get user's favorite books

- Storage: `/v1/storage`
  - POST `/v1/storage/upload`: Upload a file

## Deployment

For deployment instructions, refer to the [Beginner's Guide to AWS Deployment](deployment/BEGINNER_GUIDE.md).
