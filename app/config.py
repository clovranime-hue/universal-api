"""
Configuration settings for the Universal Media Downloader API
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    
    # Instagram - Uses SSSInstagram.com (100% FREE)
    instagram_method: str = "sssinstagram"  # Only method supported
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", 60))  # Longer timeout for browser automation
    
    # Limits
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", 100))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", 30))
    
    # Rate limiting (requests per hour per IP)
    rate_limit: int = 100
    
    # yt-dlp options
    ytdlp_timeout: int = 30
    ytdlp_retries: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
