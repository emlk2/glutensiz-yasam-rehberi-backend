"""
Barkod tarama endpoint'leri
"""
from fastapi import APIRouter, HTTPException, status
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import BarcodeRequest, BarcodeResponseSuccess, BarcodeResponseNotFound, ErrorResponse
from db.database import db
from utils.validators import validate_barcode
from utils.helpers import format_product_response, get_risk_emoji
from utils.logger import logger


router = APIRouter(prefix="/api/v1/scan", tags=["Barcode Scanning"])


@router.post(
    "/barcode",
    response_model=BarcodeResponseSuccess | BarcodeResponseNotFound,
    summary="Barkod ile ürün sorgu",
    description="Barkod numarası ile veritabanında ürün arar"
)
async def scan_barcode(request: BarcodeRequest):
    """
    Barkod tarama endpoint'i
    
    - **barcode**: 8-14 karakterli barkod numarası
    """
    try:
        # Barkod validasyonu
        is_valid, message = validate_barcode(request.barcode)
        if not is_valid:
            logger.warning(f"Geçersiz barkod: {request.barcode}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Veritabanında ara
        product = db.get_product_by_barcode(request.barcode)
        
        if product:
            logger.info(f"✅ Ürün bulundu: {product['product_name']} ({request.barcode})")
            
            return BarcodeResponseSuccess(
                status="success",
                product=format_product_response(product)
            )
        else:
            logger.info(f"❌ Ürün bulunamadı: {request.barcode}")
            
            return BarcodeResponseNotFound(
                status="not_found",
                message="Ürün veri tabanında bulunamadı. Lütfen içindekiler analizi yapınız.",
                suggestion="ingredients_analysis"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Barkod tarama hatası: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sunucu hatası oluştu"
        )


@router.get(
    "/stats",
    summary="Veritabanı istatistikleri",
    description="Barkod tarama veri tabanı istatistiklerini döndür"
)
async def get_barcode_stats():
    """Veritabanı istatistiklerini getir"""
    try:
        stats = db.get_statistics()
        
        return {
            "status": "success",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"İstatistik hatası: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="İstatistik alınamadı"
        )
