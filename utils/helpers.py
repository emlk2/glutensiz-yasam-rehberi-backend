"""
Yardımcı fonksiyonlar
"""
from typing import Dict, Any, Optional


def format_product_response(product: Dict[str, Any]) -> Dict[str, Any]:
    """Ürün yanıtını format et"""
    return {
        "id": product["id"],
        "barcode": product["barcode"],
        "product_name": product["product_name"],
        "brand": product.get("brand"),
        "risk_level": product["risk_level"],
        "contains_gluten": bool(product["contains_gluten"]),
        "contains_cross_contamination": bool(product["contains_cross_contamination"]),
        "certified_gluten_free": bool(product["certified_gluten_free"]),
        "ingredients_text": product.get("ingredients_text"),
        "source": product.get("source"),
        "added_date": product["added_date"]
    }


def get_risk_emoji(risk_level: str) -> str:
    """Risk seviyesine göre emoji döndür"""
    emojis = {
        "safe": "🟢",
        "risky": "🟡",
        "dangerous": "🔴"
    }
    return emojis.get(risk_level, "⚪")


def get_risk_message(risk_level: str) -> str:
    """Risk seviyesine göre mesaj döndür"""
    messages = {
        "safe": "Bu ürün güvenli görünüyor ✅",
        "risky": "Bu ürün riskli olabilir ⚠️",
        "dangerous": "Bu ürün gluten içeriyor ❌"
    }
    return messages.get(risk_level, "Bilinmiyor")


def calculate_confidence_percentage(confidence: float) -> str:
    """Güven oranını yüzde olarak format et"""
    percentage = round(confidence * 100, 1)
    return f"%{percentage}"
