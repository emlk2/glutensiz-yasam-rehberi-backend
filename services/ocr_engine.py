"""
OCR Engine - EasyOCR ile metin tanıma
"""
import io
from pathlib import Path
from typing import Optional, Dict, Any
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False

from utils.logger import logger


class OCREngine:
    """EasyOCR ile metin tanıma motoru"""
    
    def __init__(self, languages: list = ["tr", "en"]):
        """
        OCR Engine'i başlat
        
        Args:
            languages: Tanımlanacak diller (Türkçe + İngilizce)
        """
        self.languages = languages
        self.reader = None
        
        if HAS_EASYOCR:
            try:
                logger.info(f"🚀 EasyOCR yükleniyor (Diller: {', '.join(languages)})...")
                self.reader = easyocr.Reader(languages, gpu=False)
                logger.info("✅ EasyOCR hazır")
            except Exception as e:
                logger.error(f"❌ EasyOCR yükleme hatası: {str(e)}")
                self.reader = None
        else:
            logger.warning("⚠️  EasyOCR kurulu değil. Kurulum: pip install easyocr")
    
    def extract_text_from_image(self, image_bytes: bytes) -> Optional[str]:
        """
        Görselden metin çıkart
        
        Args:
            image_bytes: Görüntü dosyasının binary verisi
        
        Returns:
            Çıkarılan metin veya None (hata durumunda)
        """
        if not self.reader:
            logger.error("❌ OCR Engine başlatılmamış")
            return None
        
        try:
            # PIL ile görseli yükle
            from PIL import Image
            
            image = Image.open(io.BytesIO(image_bytes))
            logger.debug(f"📸 Görüntü yüklendi: {image.size}")
            
            # OCR işlemini yap
            logger.debug("🔍 Metin tanıması başlatılıyor...")
            results = self.reader.readtext(image, detail=0)  # detail=0: sadece metin
            
            # Sonuçları birleştir
            extracted_text = "\n".join(results)
            
            logger.info(f"✅ Metin tanıması başarılı ({len(extracted_text)} karakter)")
            return extracted_text
            
        except Exception as e:
            logger.error(f"❌ OCR hatası: {str(e)}", exc_info=True)
            return None
    
    def extract_text_with_confidence(self, image_bytes: bytes) -> Optional[Dict[str, Any]]:
        """
        Metin ve güven oranı ile çıkart
        
        Returns:
            {
                "text": "Çıkarılan metin",
                "confidence": 0.95,
                "details": [{"text": "kelime", "confidence": 0.98}, ...]
            }
        """
        if not self.reader:
            return None
        
        try:
            from PIL import Image
            
            image = Image.open(io.BytesIO(image_bytes))
            results = self.reader.readtext(image, detail=1)  # detail=1: metin + güven
            
            # Metin ve güven oranlarını ayıkla
            texts = []
            confidences = []
            details = []
            
            for (bbox, text, confidence) in results:
                texts.append(text)
                confidences.append(confidence)
                details.append({
                    "text": text,
                    "confidence": round(confidence, 3)
                })
            
            # Ortalama güven oranı
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            full_text = "\n".join(texts)
            
            logger.info(f"✅ OCR tamamlandı (Güven: %{avg_confidence*100:.1f})")
            
            return {
                "text": full_text,
                "confidence": round(avg_confidence, 3),
                "details": details,
                "line_count": len(texts)
            }
        
        except Exception as e:
            logger.error(f"❌ OCR hatası: {str(e)}", exc_info=True)
            return None
    
    def extract_ingredients_from_text(self, text: str) -> Optional[list]:
        """
        Metin içerisinden malzemeleri ayıkla
        Tipik format: "İçindekiler: madde1, madde2, madde3..."
        
        Args:
            text: OCR'dan çıkarılan metin
        
        Returns:
            Malzeme listesi
        """
        if not text:
            return []
        
        try:
            # Türkçe anahtar kelimeleri ara
            keywords = ["İçindekiler", "Bileşim", "Malzeme", "İçeriği", "Bileşenleri"]
            
            text_lower = text.lower()
            start_index = -1
            
            # Anahtar kelimeyi bul
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    start_index = text_lower.index(keyword.lower())
                    break
            
            if start_index == -1:
                logger.warning("⚠️  İçindekiler bölümü bulunamadı")
                return []
            
            # İçindekiler kısmını al
            ingredients_text = text[start_index:]
            
            # Satır sonlarına göre böl
            lines = ingredients_text.split("\n")
            if lines:
                first_line = lines[0]
                
                # Virgül veya başka ayırıcılarla böl
                raw_ingredients = []
                for separator in [",", ";", "•", "-"]:
                    if separator in first_line:
                        raw_ingredients = first_line.split(separator)
                        break
                
                # Boş ve gereksiz olanları temizle
                cleaned = []
                for item in raw_ingredients:
                    item = item.strip()
                    # Anahtar kelimeleri kaldır
                    for keyword in keywords:
                        item = item.replace(keyword, "").replace(":", "").strip()
                    
                    if item and len(item) > 1:
                        cleaned.append(item)
                
                logger.info(f"✅ {len(cleaned)} malzeme bulundu")
                return cleaned
            
            return []
        
        except Exception as e:
            logger.error(f"❌ Malzeme ayıklama hatası: {str(e)}")
            return []


# Global OCR instance
ocr_engine = None

def get_ocr_engine() -> OCREngine:
    """OCR engine'ini lazily yükle"""
    global ocr_engine
    if ocr_engine is None:
        ocr_engine = OCREngine()
    return ocr_engine
