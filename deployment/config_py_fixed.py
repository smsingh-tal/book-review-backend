import os
from functools import lru_cache
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    
    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME: str = os.getenv("DB_NAME", "book_review")
    
    @property
    def DATABASE_URL(self) -> str:
        """Constructs database URL from individual components"""
        # Use DATABASE_URL environment variable if set, otherwise construct PostgreSQL URL
        if os.getenv("DATABASE_URL"):
            return os.getenv("DATABASE_URL")
        else:
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Other Settings  
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key")  # In production, use a strong secret key
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-openai-api-key")  # Optional, only if using OpenAI features
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

@lru_cache()
def get_settings() -> Settings:
    return Settings()
