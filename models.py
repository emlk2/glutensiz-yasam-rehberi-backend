"""
Pydantic modelleri - Request ve Response veri yapıları
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ==================== Barkod Tarama ====================

class BarcodeRequest(BaseModel):
    """Barkod tarama isteği"""
    barcode: str = Field(..., min_length=8, max_length=14, description="Ürün barkodu")


class ProductResponse(BaseModel):
    """Ürün bilgileri yanıtı"""
    id: int
    barcode: str
    product_name: str
    brand: Optional[str] = None
    risk_level: str  # "safe", "risky", "dangerous"
    contains_gluten: bool
    contains_cross_contamination: bool
    certified_gluten_free: bool
    ingredients_text: Optional[str] = None
    source: str
    added_date: str


class BarcodeResponseSuccess(BaseModel):
    """Başarılı barkod tarama yanıtı"""
    status: str = "success"
    product: ProductResponse


class BarcodeResponseNotFound(BaseModel):
    """Ürün bulunamadı yanıtı"""
    status: str = "not_found"
    message: str = "Ürün veri tabanında bulunamadı. Lütfen içindekiler analizi yapınız."
    suggestion: str = "ingredients_analysis"


# ==================== İçindekiler Analizi ====================

class IngredientAnalysis(BaseModel):
    """Tespit edilen malzeme"""
    ingredient: str
    risk_level: str  # "safe", "risky", "dangerous"
    confidence: float = Field(..., ge=0.0, le=1.0)


class IngredientsAnalysisResponse(BaseModel):
    """İçindekiler analizi yanıtı"""
    status: str = "success"
    extracted_text: str
    analysis: dict = {
        "detected_ingredients": list[IngredientAnalysis],
        "overall_risk_level": str,  # "safe", "risky", "dangerous"
        "gluten_found": bool,
        "cross_contamination_risk": bool,
        "confidence_score": float,
        "explanation": str,
        "recommendations": list[str]
    }


# ==================== Ürün Yönetimi ====================

class ProductCreate(BaseModel):
    """Ürün oluşturma"""
    barcode: str = Field(..., min_length=8, max_length=14)
    product_name: str = Field(..., min_length=1, max_length=255)
    brand: Optional[str] = None
    risk_level: str = Field(..., pattern="^(safe|risky|dangerous)$")
    contains_gluten: bool
    contains_cross_contamination: bool = False
    certified_gluten_free: bool = False
    ingredients_text: Optional[str] = None
    source: str


class ProductUpdate(BaseModel):
    """Ürün güncelleme"""
    product_name: Optional[str] = None
    brand: Optional[str] = None
    risk_level: Optional[str] = None
    contains_gluten: Optional[bool] = None
    contains_cross_contamination: Optional[bool] = None
    certified_gluten_free: Optional[bool] = None
    ingredients_text: Optional[str] = None


class ProductSearchResponse(BaseModel):
    """Ürün arama yanıtı"""
    status: str = "success"
    results: list[dict]
    total: int


# ==================== Hata Yanıtları ====================

class ErrorResponse(BaseModel):
    """Hata yanıtı"""
    status: str = "error"
    error_code: str
    message: str
    details: Optional[dict] = None


# ==================== Admin ====================

class AdminLoginRequest(BaseModel):
    """Admin giriş isteği"""
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    """Admin giriş yanıtı"""
    status: str = "success"
    token: str
    expires_in: int


# ==================== Tarama Geçmişi ====================

class ScanHistoryEntry(BaseModel):
    """Tarama geçmişi kaydı"""
    scan_id: str
    user_id: str = "anonymous"
    barcode: Optional[str] = None
    product_name: str
    risk_level: str
    timestamp: datetime
    method: str  # "barcode" or "ocr"
