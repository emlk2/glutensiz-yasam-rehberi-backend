"""
İçindekiler analizi endpoint'leri
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from typing import List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ocr_engine import get_ocr_engine
from services.nlp_analyzer import get_nlp_analyzer
from utils.logger import logger
from utils.helpers import get_risk_emoji


router = APIRouter(prefix="/api/v1/analyze", tags=["Ingredients Analysis"])


@router.post(
    "/ingredients",
    summary="İçindekiler OCR + NLP analizi",
    description="Ürün paketinin içindekiler kısmının fotoğrafını yükle ve AI ile analiz et"
)
async def analyze_ingredients(image: UploadFile = File(...)):
    """
    İçindekiler analizi endpoint'i (OCR + NLP)
    
    - **image**: İçindekiler kısmının fotoğrafı (JPG, PNG, max 5MB)
    
    Çalışma sırası:
    1. EasyOCR ile metin tanıması
    2. Malzemelerin çıkarılması
    3. NLP ile gluten risk analizi
    """
    try:
        # Dosya türü kontrolü
        if image.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Yalnızca JPG ve PNG dosyaları desteklenir"
            )
        
        # Dosya boyutu kontrolü (max 5MB)
        contents = await image.read()
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Dosya 5MB'dan küçük olmalıdır"
            )
        
        logger.info(f"📸 İçindekiler analizi başlatılıyor: {image.filename}")
        
        # 1. OCR - Metin tanıması
        ocr_engine = get_ocr_engine()
        
        if not ocr_engine.reader:
            logger.warning("⚠️  EasyOCR yüklenmedi, mock analiz döndürülüyor")
            return {
                "status": "warning",
                "message": "EasyOCR kurulu değil",
                "note": "pip install easyocr ile yükleyiniz",
                "extracted_text": "MOCK: Buğday Unu, Su, Tuz, Şeker",
                "analysis": {
                    "detected_ingredients": [
                        {"ingredient": "Buğday Unu", "risk_level": "dangerous", "confidence": 0.95},
                    ],
                    "overall_risk_level": "dangerous",
                    "gluten_found": True,
                    "cross_contamination_risk": False,
                    "confidence_score": 0.95,
                    "explanation": "Buğday unu gluten içerir",
                    "recommendations": [
                        "❌ Bu ürün gluten içermektedir - RISKLI",
                        "🚫 Çölyak hastası olarak TÜKETMEYİN"
                    ]
                }
            }
        
        # OCR ile metin çıkart
        ocr_result = ocr_engine.extract_text_with_confidence(contents)
        
        if not ocr_result or not ocr_result.get("text"):
            logger.warning("❌ OCR metni çıkaramadı")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Görüntüden metin çıkarılamadı. Daha net bir fotoğraf deneyin."
            )
        
        extracted_text = ocr_result["text"]
        ocr_confidence = ocr_result["confidence"]
        
        logger.info(f"✅ OCR başarılı: {len(extracted_text)} karakter, %{ocr_confidence*100:.1f} güven")
        
        # 2. Malzemeleri çıkart
        ingredients_list = ocr_engine.extract_ingredients_from_text(extracted_text)
        
        logger.info(f"📋 {len(ingredients_list)} malzeme bulundu")
        
        # 3. NLP - Gluten risk analizi
        nlp_analyzer = get_nlp_analyzer()
        
        if ingredients_list:
            # Malzeme listesi varsa analiz et
            analysis_result = nlp_analyzer.analyze_ingredients(ingredients_list)
        else:
            # Malzeme listesi yoksa, ham metin üzerinde analiz yap
            analysis_result = nlp_analyzer.analyze_text(extracted_text)
        
        # Risk puanı hesapla
        risk_score = nlp_analyzer.calculate_risk_score(analysis_result)
        
        logger.info(f"🎯 Risk Seviyesi: {analysis_result['risk_level']} (Puan: {risk_score})")
        
        # Yanıt oluştur
        return {
            "status": "success",
            "extracted_text": extracted_text,
            "ocr_confidence": ocr_confidence,
            "analysis": {
                **analysis_result,
                "risk_score": risk_score
            },
            "debug": {
                "ingredients_extracted": ingredients_list,
                "ocr_line_count": ocr_result.get("line_count", 0)
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ İçindekiler analizi hatası: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analiz yapılamadı"
        )


@router.post(
    "/text",
    summary="Metin analizi",
    description="Doğrudan metin girerek gluten analizi yap"
)
async def analyze_text(text: str):
    """
    Doğrudan metin analizi (OCR olmaksızın)
    
    Kullanım: /api/v1/analyze/text?text=Buğday%20unu,%20su,%20tuz
    """
    try:
        if not text or len(text) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Metin en az 2 karakterden oluşmalıdır"
            )
        
        logger.info(f"📝 Metin analizi: {text[:50]}...")
        
        nlp_analyzer = get_nlp_analyzer()
        analysis_result = nlp_analyzer.analyze_text(text)
        risk_score = nlp_analyzer.calculate_risk_score(analysis_result)
        
        return {
            "status": "success",
            "input_text": text,
            "analysis": {
                **analysis_result,
                "risk_score": risk_score
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Metin analizi hatası: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analiz yapılamadı"
        )


@router.get(
    "/test",
    summary="Test endpoint",
    description="API bağlantısını test et"
)
async def test_endpoint():
    """Basit test endpoint'i"""
    ocr_engine = get_ocr_engine()
    nlp_analyzer = get_nlp_analyzer()
    
    return {
        "status": "success",
        "message": "Analiz API'si çalışıyor ✅",
        "ocr_ready": ocr_engine.reader is not None,
        "nlp_ready": nlp_analyzer is not None,
        "test_url": "/api/v1/analyze/text?text=Buğday%20unu"
    }
