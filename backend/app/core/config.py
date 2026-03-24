from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "Data Reporting System API"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_HERE"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: Optional[str] = "postgresql+asyncpg://yangke@localhost:5432/reporting_db"

    # Redis
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"

    # DeepSeek (主力模型，兼容 OpenAI SDK)
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Anthropic (保留备用)
    ANTHROPIC_API_KEY: Optional[str] = None

    # OpenAI (保留备用)
    OPENAI_API_KEY: Optional[str] = None
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_data"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
