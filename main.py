"""
FastAPI Ana Dosyası - Glutensiz Yaşam Rehberi
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Config ve database
from config import settings
from db.init_db import init_database
from db.database import db
from utils.logger import logger

# Routes
from routes import barcode, ingredients, products

# ==================== STARTUP / SHUTDOWN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup ve shutdown işlemleri"""
    # STARTUP
    logger.info("🚀 Uygulama başlatılıyor...")
    init_database()
    logger.info("✅ Veritabanı hazır")
    logger.info("🟢 API çalışıyor")
    
    yield
    
    # SHUTDOWN
    logger.info("🛑 Uygulama kapatılıyor...")


# ==================== FASTAPI UYGULAMASI ====================

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Çölyak ve gluten hassasiyeti olan kişiler için ürün analiz sistemi",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# ==================== CORS MIDDLEWARE ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ROUTES ====================

# Barkod tarama
app.include_router(barcode.router)

# İçindekiler analizi
app.include_router(ingredients.router)

# Ürün yönetimi
app.include_router(products.router)


# ==================== ROOT ENDPOINT ====================

@app.get(
    "/",
    summary="API Hoş Geldiniz",
    description="API'nin aktif olduğunu kontrol et"
)
async def root():
    """Root endpoint"""
    return {
        "status": "success",
        "message": f"Glutensiz Yaşam Rehberi API v{settings.api_version} çalışıyor 🎉",
        "documentation": "/docs",
        "endpoints": {
            "barcode_scan": "/api/v1/scan/barcode",
            "ingredients_analysis": "/api/v1/analyze/ingredients",
            "product_search": "/api/v1/products/search"
        }
    }


@app.get("/health", summary="Sağlık Kontrolü")
async def health_check():
    """Sağlık kontrolü endpoint'i"""
    try:
        # Veritabanı bağlantısını test et
        stats = db.get_statistics()
        
        return {
            "status": "healthy",
            "database": "connected",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Sağlık kontrolü hatası: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


# ==================== ERROR HANDLERS ====================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Genel exception handler"""
    logger.error(f"Beklenmeyen hata: {str(exc)}", exc_info=True)
    
    return {
        "status": "error",
        "error_code": "INTERNAL_SERVER_ERROR",
        "message": "Sunucuda bir hata oluştu"
    }


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
