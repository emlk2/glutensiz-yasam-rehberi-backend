"""
NLP Analyzer - Gluten risk analizi
"""
from typing import Dict, List, Any, Tuple
from pathlib import Path
import sys
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import db
from utils.logger import logger

try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class NLPAnalyzer:
    """NLP ile gluten risk analizi"""
    
    def __init__(self):
        """NLP Analyzer'ı başlat"""
        self.dangerous_ingredients = db.get_dangerous_ingredients()
        self.risky_keywords = db.get_risky_keywords()
        self.classifier = None
        
        logger.info(f"📊 NLP Analyzer başlatıldı")
        logger.info(f"   ⚠️  Tehlikeli malzeme: {len(self.dangerous_ingredients)}")
        logger.info(f"   🟡 Riskli kelime: {len(self.risky_keywords)}")
        
        # Transformers yükle (opsiyonel)
        if HAS_TRANSFORMERS:
            try:
                logger.debug("🤖 Hugging Face model yükleniyor...")
                # Zero-shot classification modeli
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model="distilbert-base-multilingual-cased"
                )
                logger.info("✅ NLP model hazır")
            except Exception as e:
                logger.warning(f"⚠️  NLP model yüklenemedi: {str(e)}")
                self.classifier = None
    
    def analyze_ingredients(self, ingredients_list: List[str]) -> Dict[str, Any]:
        """
        Malzemeleri analiz et
        
        Args:
            ingredients_list: Malzeme listesi
        
        Returns:
            Analiz sonuçları
        """
        if not ingredients_list:
            return {
                "risk_level": "safe",
                "gluten_found": False,
                "detected_ingredients": [],
                "explanation": "Malzeme bulunamadı",
                "confidence": 1.0
            }
        
        try:
            detected_ingredients = []
            has_dangerous = False
            has_risky = False
            confidence_scores = []
            
            # Her malzemeyi kontrol et
            for ingredient in ingredients_list:
                ingredient_lower = ingredient.lower().strip()
                
                # 1. KURAL TABANLI KONTROLİZE
                # Tehlikeli malzemeleri kontrol et
                for dangerous in self.dangerous_ingredients:
                    if dangerous.lower() in ingredient_lower:
                        detected_ingredients.append({
                            "ingredient": ingredient,
                            "risk_level": "dangerous",
                            "confidence": 0.99,
                            "reason": "Gluten içeren malzeme"
                        })
                        has_dangerous = True
                        confidence_scores.append(0.99)
                        break
                else:
                    # Riskli kelimeleri kontrol et
                    for risky in self.risky_keywords:
                        if risky.lower() in ingredient_lower:
                            detected_ingredients.append({
                                "ingredient": ingredient,
                                "risk_level": "risky",
                                "confidence": 0.85,
                                "reason": "Çapraz bulaş veya belirsiz malzeme"
                            })
                            has_risky = True
                            confidence_scores.append(0.85)
                            break
            
            # 2. BAĞLAMSAL ANALIZ (NLP MODEL)
            # Eğer model varsa ve tehlikeli malzeme bulunmadıysa, daha derinlemesine analiz yap
            if self.classifier and not has_dangerous and ingredients_list:
                try:
                    # Gluten ile ilgili malzemelerin sınıflandırılması
                    gluten_related_labels = ["contains gluten", "gluten-free", "uncertain"]
                    
                    # Her malzemeyi sınıflandır
                    for ingredient in ingredients_list:
                        if ingredient not in [d.get("ingredient") for d in detected_ingredients]:
                            results = self.classifier(
                                ingredient,
                                gluten_related_labels,
                                multi_class=False
                            )
                            
                            # En yüksek score'u al
                            top_label = results["labels"][0]
                            top_score = results["scores"][0]
                            
                            if "gluten" in top_label.lower() and top_score > 0.7:
                                detected_ingredients.append({
                                    "ingredient": ingredient,
                                    "risk_level": "risky",
                                    "confidence": round(top_score, 3),
                                    "reason": f"NLP analiz: {top_label}"
                                })
                                confidence_scores.append(top_score)
                
                except Exception as e:
                    logger.warning(f"⚠️  NLP model analizi başarısız: {str(e)}")
            
            # Risk seviyesini belirle
            if has_dangerous:
                overall_risk = "dangerous"
                explanation = "Gluten içeren malzeme tespit edildi!"
            elif has_risky:
                overall_risk = "risky"
                explanation = "Çapraz bulaş riski veya belirsiz malzeme mevcut"
            else:
                overall_risk = "safe"
                explanation = "Gluten içeren malzeme tespit edilmedi"
            
            # Ortalama güven oranı
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 1.0
            
            return {
                "risk_level": overall_risk,
                "gluten_found": has_dangerous,
                "cross_contamination_risk": has_risky,
                "detected_ingredients": detected_ingredients,
                "explanation": explanation,
                "confidence": round(avg_confidence, 3),
                "recommendations": self._get_recommendations(overall_risk)
            }
        
        except Exception as e:
            logger.error(f"❌ Analiz hatası: {str(e)}", exc_info=True)
            return {
                "risk_level": "unknown",
                "gluten_found": False,
                "error": str(e),
                "explanation": "Analiz yapılamadı"
            }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Metin içerisinde gluten ara (OCR'dan gelen metin)
        
        Args:
            text: Görüntüden çıkarılan metin
        
        Returns:
            Analiz sonuçları
        """
        if not text:
            return {
                "risk_level": "safe",
                "gluten_found": False,
                "explanation": "Metin boş"
            }
        
        try:
            text_lower = text.lower()
            
            # Tehlikeli kelimeleri ara
            dangerous_count = 0
            dangerous_found = []
            
            for ingredient in self.dangerous_ingredients:
                if ingredient.lower() in text_lower:
                    dangerous_count += 1
                    dangerous_found.append(ingredient)
            
            # Riskli kelimeleri ara
            risky_count = 0
            risky_found = []
            
            for keyword in self.risky_keywords:
                if keyword.lower() in text_lower:
                    risky_count += 1
                    risky_found.append(keyword)
            
            # Risk belirle
            if dangerous_count > 0:
                risk_level = "dangerous"
                explanation = f"Gluten içeren malzeme bulundu: {', '.join(dangerous_found)}"
            elif risky_count > 0:
                risk_level = "risky"
                explanation = f"Riskli ifadeler: {', '.join(risky_found)}"
            else:
                risk_level = "safe"
                explanation = "Gluten içeren malzeme bulunamadı"
            
            return {
                "risk_level": risk_level,
                "gluten_found": dangerous_count > 0,
                "cross_contamination_risk": risky_count > 0,
                "dangerous_ingredients_found": dangerous_found,
                "risky_keywords_found": risky_found,
                "explanation": explanation,
                "recommendations": self._get_recommendations(risk_level)
            }
        
        except Exception as e:
            logger.error(f"❌ Metin analizi hatası: {str(e)}")
            return {
                "risk_level": "unknown",
                "error": str(e)
            }
    
    def _get_recommendations(self, risk_level: str) -> List[str]:
        """Risk seviyesine göre tavsiyeleri döndür"""
        recommendations = {
            "safe": [
                "✅ Bu ürün gluten içermediği görülmektedir",
                "📌 Yine de üretici bilgilerini kontrol etmeniz önerilir",
                "💡 Sertifikasyonu varsa tercih etmeyi düşünün"
            ],
            "risky": [
                "⚠️  Çapraz bulaş riski olabilir",
                "📞 Şüpheli durumlarda üreticiyi arayın",
                "📖 Dernek rehberinde kontrol etmeyi deneyin",
                "💡 Hassas iseniz bu ürünü tercih etmeyin"
            ],
            "dangerous": [
                "❌ Bu ürün gluten içermektedir - RISKLI",
                "🚫 Çölyak hastası olarak TÜKETMEYİN",
                "📞 Şüpheyi doğrulamak için üreticiyi arayabilirsiniz",
                "💡 Alternativ ürünler seçin"
            ]
        }
        
        return recommendations.get(risk_level, [])
    
    def calculate_risk_score(self, analysis_result: Dict[str, Any]) -> float:
        """
        Risk puanı hesapla (0-1, 1 en riskli)
        """
        risk_scores = {
            "safe": 0.0,
            "risky": 0.5,
            "dangerous": 1.0,
            "unknown": 0.3
        }
        
        base_score = risk_scores.get(analysis_result.get("risk_level"), 0.5)
        confidence = analysis_result.get("confidence", 0.5)
        
        # Güven oranı ne kadar düşükse, risk puanı artar
        adjusted_score = base_score * (1 + (1 - confidence) * 0.2)
        
        return round(min(adjusted_score, 1.0), 3)


# Global NLP instance
nlp_analyzer = None

def get_nlp_analyzer() -> NLPAnalyzer:
    """NLP analyzer'ı lazily yükle"""
    global nlp_analyzer
    if nlp_analyzer is None:
        nlp_analyzer = NLPAnalyzer()
    return nlp_analyzer
