"""
Proje yapılandırması
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Proje kök dizini
BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Proje ayarları"""
    
    # FastAPI
    api_title: str = "Glutensiz Yaşam Rehberi API"
    api_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Database
    database_path: str = str(BASE_DIR / "db" / "gluten_db.db")
    
    # External APIs
    openfoodfacts_api_url: str = "https://world.openfoodfacts.org/api/v0"
    ean_search_api_url: str = "https://api.ean-search.com"
    
    # CORS
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://glutensizyasamrehberi.vercel.app"
    ]
    
    # Logging
    log_level: str = "INFO"
    
    # OCR & NLP
    ocr_model: str = "tr"
    nlp_model: str = "distilbert-base-multilingual-cased"
    
    # Admin
    admin_username: str = "admin"
    admin_password: str = "changeme"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
