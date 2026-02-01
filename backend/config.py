"""
Configuration module for Lotus backend
Loads and manages environment variables with production-safe defaults
"""

import logging
import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env from project root (parent of backend directory)
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"Loaded .env from {env_path}")
else:
    logger.warning(f".env not found at {env_path}, using system environment variables")


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    Validates environment and fails fast if required vars are missing
    """
    
    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        env_file_encoding = 'utf-8'
        extra = 'allow'
    # Supabase Configuration (Required)
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_KEY: str = Field(..., description="Supabase anonymous key")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., description="Supabase service role key")
    
    # FastAPI Configuration
    HOST: str = Field(default="0.0.0.0", description="FastAPI server host")
    PORT: int = Field(default=8000, description="FastAPI server port")
    DEBUG: bool | str = Field(default=False, description="Debug mode flag")
    
    # CORS Configuration
    CORS_ORIGINS: str | List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins (comma-separated string or list)"
    )
    
    # OpenAI Configuration (Required for vector search)
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    
    # Application Configuration
    ENVIRONMENT: str = Field(default="development", description="Environment: development/staging/production")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level: DEBUG/INFO/WARNING/ERROR")
    
    # Database Configuration (Production optimized)
    DATABASE_POOL_SIZE: int = Field(default=2, description="Connection pool size (dev: 2, prod: 10)")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, description="Connection pool timeout in seconds")
    
    # Sentry Configuration (Error tracking)
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry error tracking DSN")
    SENTRY_ENVIRONMENT: Optional[str] = Field(default=None, description="Sentry environment label")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=0.1, description="Sentry trace sampling rate (0.0-1.0)")
    SENTRY_PROFILES_SAMPLE_RATE: float = Field(default=0.1, description="Sentry profiling sampling rate (0.0-1.0)")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Requests per rate limit window")
    RATE_LIMIT_WINDOW_MINUTES: int = Field(default=1, description="Rate limit window in minutes")
    
    # Monitoring & Performance
    ENABLE_REQUEST_LOGGING: bool = Field(default=True, description="Enable detailed request logging")
    REQUEST_TIMEOUT_SECONDS: int = Field(default=30, description="Request timeout in seconds")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"
    
    @field_validator('DEBUG', mode='before')
    @classmethod
    def validate_debug(cls, v):
        """Convert string boolean to actual boolean"""
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return bool(v)
    
    @field_validator('ENVIRONMENT')
    @classmethod
    def validate_environment(cls, v):
        """Validate environment value (case-insensitive)"""
        v_lower = v.lower() if isinstance(v, str) else v
        if v_lower not in ['development', 'staging', 'production']:
            raise ValueError(f"ENVIRONMENT must be one of: development, staging, production. Got: {v}")
        return v_lower
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level value (case-insensitive)"""
        v_upper = v.upper() if isinstance(v, str) else v
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {', '.join(valid_levels)}. Got: {v}")
        return v_upper
    
    @field_validator('CORS_ORIGINS')
    @classmethod
    def validate_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list"""
        if isinstance(v, str):
            # Split comma-separated string into list
            origins = [origin.strip() for origin in v.split(',') if origin.strip()]
            return origins
        elif isinstance(v, list):
            return v
        else:
            raise ValueError(f"CORS_ORIGINS must be a string or list, got {type(v)}")
    
    @field_validator('DATABASE_POOL_SIZE')
    @classmethod
    def validate_pool_size(cls, v, info):
        """Validate and auto-adjust pool size based on environment"""
        environment = info.data.get('ENVIRONMENT', 'development')
        
        # Auto-adjust if not explicitly set
        if environment == 'production' and v == 2:
            logger.warning("Pool size is 2 in production. Recommending increase to 10.")
        elif environment == 'development' and v > 5:
            logger.warning("Pool size > 5 in development. Consider reducing to 2-5.")
        
        if v < 1:
            raise ValueError("DATABASE_POOL_SIZE must be >= 1")
        if v > 50:
            raise ValueError("DATABASE_POOL_SIZE must be <= 50")
        
        return v
    
    @field_validator('SENTRY_TRACES_SAMPLE_RATE', 'SENTRY_PROFILES_SAMPLE_RATE')
    @classmethod
    def validate_sample_rates(cls, v):
        """Validate sampling rates are between 0.0 and 1.0"""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Sample rate must be between 0.0 and 1.0. Got: {v}")
        return v


# Load settings with environment validation
try:
    settings = Settings()
    
    # Set logging level based on configuration
    log_level = getattr(logging, settings.LOG_LEVEL)
    logging.basicConfig(level=log_level)
    
    logger.info(f"✓ Configuration loaded for environment: {settings.ENVIRONMENT}")
    
    # Validate production requirements
    if settings.ENVIRONMENT == 'production':
        if settings.DEBUG:
            logger.error("❌ DEBUG mode cannot be enabled in production!")
            raise ValueError("DEBUG must be False in production")
        
        if not settings.OPENAI_API_KEY:
            logger.error("❌ OPENAI_API_KEY is required in production!")
            raise ValueError("OPENAI_API_KEY is required")
        
        if not settings.SENTRY_DSN:
            logger.warning("⚠️ SENTRY_DSN not configured. Error tracking disabled.")
        
        logger.info(f"✓ Pool size: {settings.DATABASE_POOL_SIZE} (production optimized)")
        logger.info(f"✓ Logging level: {settings.LOG_LEVEL}")
        logger.info(f"✓ CORS origins configured: {len(settings.CORS_ORIGINS)} origins")

except Exception as e:
    logger.error(f"❌ Failed to load configuration: {e}")
    raise
