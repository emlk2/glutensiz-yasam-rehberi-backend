"""
Ürün yönetimi endpoint'leri
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import ProductCreate, ProductUpdate, ProductSearchResponse
from db.database import db
from utils.validators import validate_product_name, validate_barcode
from utils.helpers import format_product_response
from utils.logger import logger


router = APIRouter(prefix="/api/v1/products", tags=["Product Management"])


@router.get(
    "/search",
    response_model=ProductSearchResponse,
    summary="Ürün arama",
    description="Ürün adı veya marka ile ara"
)
async def search_products(
    q: str = Query(..., min_length=1, description="Arama metni"),
    limit: int = Query(10, ge=1, le=100, description="Sonuç sınırı")
):
    """
    Ürün arama endpoint'i
    
    - **q**: Arama metni (ürün adı, marka vb.)
    - **limit**: Döndürülecek sonuç sayısı (default: 10, max: 100)
    """
    try:
        results = db.search_products(q, limit)
        
        formatted_results = [format_product_response(product) for product in results]
        
        logger.info(f"Arama yapıldı: '{q}' - {len(results)} sonuç")
        
        return ProductSearchResponse(
            status="success",
            results=formatted_results,
            total=len(formatted_results)
        )
    
    except Exception as e:
        logger.error(f"Arama hatası: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Arama yapılamadı"
        )


@router.get(
    "/{product_id}",
    summary="Ürün detaylarını getir",
    description="ID ile ürün detaylarını getir"
)
async def get_product_detail(product_id: int):
    """Ürün detaylarını getir"""
    try:
        # TODO: Database'den ID ile getir
        return {
            "status": "success",
            "message": "Detay getirme henüz implementasyon olmadı"
        }
    except Exception as e:
        logger.error(f"Detay getirme hatası: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Detay alınamadı"
        )


@router.post(
    "/",
    summary="Yeni ürün ekle",
    description="Admin tarafından yeni ürün ekle"
)
async def create_product(product: ProductCreate):
    """
    Yeni ürün oluştur
    
    - **barcode**: Barkod (8-14 karakterli)
    - **product_name**: Ürün adı
    - **brand**: Marka (opsiyonel)
    - **risk_level**: Risk seviyesi (safe/risky/dangerous)
    - **contains_gluten**: Gluten içeriyor mu?
    - **source**: Veri kaynağı
    """
    try:
        # Validasyon
        barcode_valid, barcode_msg = validate_barcode(product.barcode)
        if not barcode_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=barcode_msg
            )
        
        name_valid, name_msg = validate_product_name(product.product_name)
        if not name_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=name_msg
            )
        
        # Ürünü ekle
        product_id = db.create_product(product.model_dump())
        
        logger.info(f"✅ Yeni ürün eklendi: {product.product_name} (ID: {product_id})")
        
        return {
            "status": "success",
            "product_id": product_id,
            "message": "Ürün başarıyla eklendi"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ürün oluşturma hatası: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ürün eklenemedi"
        )
