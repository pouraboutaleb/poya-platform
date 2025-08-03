from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Security settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Database settings
    database_url: str = "postgresql://user:password@localhost:5432/mrdpol_core_db"
    
    # CORS settings
    cors_origins: str = "http://localhost:5173"
    
    @property 
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated string to list of CORS origins"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # File Storage settings
    storage_path: str = "./storage"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: str = "image/jpeg,image/png,image/gif,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/plain,text/csv"
    
    # Application settings
    debug: bool = False
    environment: str = "production"
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Convert comma-separated string to list of allowed file types"""
        return [ft.strip() for ft in self.allowed_file_types.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
