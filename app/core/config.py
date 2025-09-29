from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")
    
    # Database Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "book_review"
    
    @property
    def DATABASE_URL(self) -> str:
        """Constructs database URL from individual components"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Other Settings
    secret_key: str = "your-secret-key"  # In production, use a strong secret key
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = "your-openai-api-key"  # Optional, only if using OpenAI features
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

@lru_cache()
def get_settings() -> Settings:
    return Settings()
