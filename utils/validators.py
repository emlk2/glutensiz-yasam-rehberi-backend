"""
Input validasyon fonksiyonları
"""
import re
from typing import Tuple


def validate_barcode(barcode: str) -> Tuple[bool, str]:
    """
    Barkod validasyonu
    EAN-8, EAN-12, EAN-13 ve EAN-14 destekler
    """
    # Sadece sayılar
    if not barcode.isdigit():
        return False, "Barkod sadece rakamlardan oluşmalıdır"
    
    # Uzunluk kontrolü
    if len(barcode) not in [8, 12, 13, 14]:
        return False, "Barkod 8, 12, 13 veya 14 rakamdan oluşmalıdır"
    
    return True, "Geçerli"


def validate_product_name(name: str) -> Tuple[bool, str]:
    """Ürün adı validasyonu"""
    if not name or len(name) < 1:
        return False, "Ürün adı boş olamaz"
    
    if len(name) > 255:
        return False, "Ürün adı 255 karakteri aşamaz"
    
    return True, "Geçerli"


def validate_risk_level(risk_level: str) -> Tuple[bool, str]:
    """Risk seviyesi validasyonu"""
    valid_levels = ["safe", "risky", "dangerous"]
    
    if risk_level not in valid_levels:
        return False, f"Risk seviyesi {valid_levels} arasında olmalıdır"
    
    return True, "Geçerli"


def validate_email(email: str) -> Tuple[bool, str]:
    """Email validasyonu"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email):
        return True, "Geçerli"
    else:
        return False, "Geçersiz email adresi"
