"""API configuration."""

import os

from dotenv import load_dotenv

load_dotenv()


class APIConfig:
    """API configuration from environment variables."""

    DATABASE_URL = os.getenv("DATABASE_URL")
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")
        
        return True
