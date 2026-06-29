"""
Configuration settings for the Resume Intelligence Platform
"""

from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file
    """
    
    # Application
    APP_NAME: str = "Resume Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:////tmp/resume_intelligence.db"
    
    # File Upload
    UPLOAD_DIR: Path = Path("/tmp/uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".doc"}
    
    # AI Models
    EMBEDDINGS_DIR: Path = Path("/tmp/embeddings")
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"  # Fast and efficient
    SPACY_MODEL: str = "en_core_web_sm"
    
    # Matching Algorithm Weights
    WEIGHT_REQUIRED_SKILLS: float = 0.40
    WEIGHT_PREFERRED_SKILLS: float = 0.20
    WEIGHT_EXPERIENCE: float = 0.20
    WEIGHT_CERTIFICATIONS: float = 0.10
    WEIGHT_EDUCATION: float = 0.10
    
    # Performance
    CACHE_EMBEDDINGS: bool = True
    MAX_WORKERS: int = 4
    
    # Security
    MAX_FILENAME_LENGTH: int = 255
    SANITIZE_FILENAMES: bool = True
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Create necessary directories (only if writable)
try:
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass  # Directories will be created at runtime
