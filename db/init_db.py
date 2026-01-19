"""
SQLite Veritabanı Initialization
"""
import sqlite3
from pathlib import Path
import sys

# Parent dizini ekle
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


def init_database():
    """Veritabanını oluştur ve tabloları başlat"""
    
    db_path = Path(settings.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ==================== TABLOLAR ====================
    
    # 1. ÜRÜNLER TABLOSU
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT UNIQUE NOT NULL,
        product_name TEXT NOT NULL,
        brand TEXT,
        risk_level TEXT CHECK(risk_level IN ('safe', 'risky', 'dangerous')) NOT NULL,
        contains_gluten BOOLEAN NOT NULL,
        contains_cross_contamination BOOLEAN DEFAULT 0,
        ingredients_text TEXT,
        certified_gluten_free BOOLEAN DEFAULT 0,
        source TEXT,
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 2. GLUTEN TEMİZLEYİCİLERİ TABLOSU
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flagged_ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ingredient TEXT UNIQUE NOT NULL,
        risk_level TEXT CHECK(risk_level IN ('dangerous', 'risky', 'safe')) NOT NULL,
        category TEXT,
        description TEXT,
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 3. İNDEKSLER
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_barcode ON products(barcode);
    """)
    
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_product_name ON products(product_name);
    """)
    
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_ingredient ON flagged_ingredients(ingredient);
    """)
    
    # ==================== BAŞLANGIÇ VERİLERİ ====================
    
    # Gluten tetikleyicileri
    gluten_ingredients = [
        # Tehlikeli - Gluten içerir
        ("Buğday", "dangerous", "Tahıl", "100% gluten içerir"),
        ("Arpa", "dangerous", "Tahıl", "100% gluten içerir"),
        ("Çavdar", "dangerous", "Tahıl", "100% gluten içerir"),
        ("Spelt", "dangerous", "Tahıl", "Buğday türü, gluten içerir"),
        ("Kamut", "dangerous", "Tahıl", "Buğday türü, gluten içerir"),
        ("Malt", "dangerous", "İçerik", "Arpa'dan türetilir"),
        ("Gluten", "dangerous", "İçerik", "Doğrudan gluten"),
        ("Buğday Nişastası", "dangerous", "İçerik", "Buğday'dan türetilir"),
        ("Buğday Ezmesi", "dangerous", "İçerik", "Buğday ürünü"),
        ("Buğday Unu", "dangerous", "İçerik", "Buğday ürünü"),
        
        # Riskli - Çapraz bulaş veya belirsiz
        ("Aynı tesiste işlenir", "risky", "Proses", "Çapraz bulaş riski"),
        ("Çapraz bulaş uyarısı", "risky", "Proses", "Gluten içeren ürünlerle temas"),
        ("Trace amounts", "risky", "Miktarı", "Eser miktarlar"),
        ("May contain", "risky", "Belirsiz", "Gluten içeriyor olabilir"),
        ("Gluten içerebilir", "risky", "Belirsiz", "Gluten içeriyor olabilir"),
    ]
    
    for ingredient, risk_level, category, description in gluten_ingredients:
        cursor.execute("""
        INSERT OR IGNORE INTO flagged_ingredients 
        (ingredient, risk_level, category, description)
        VALUES (?, ?, ?, ?)
        """, (ingredient, risk_level, category, description))
    
    # Örnek güvenli ürünler
    safe_products = [
        ("8696000000001", "Glutensiz Ekmek", "ABC Marka", "safe", False, False, True,
         "Un, Su, Tuz", "colyak.org.tr"),
        ("8696000000002", "Glutensiz Makarna", "XYZ Marka", "safe", False, False, True,
         "Mısır Unu, Su", "colyak.org.tr"),
    ]
    
    for barcode, name, brand, risk, gluten, cross, certified, ingredients, source in safe_products:
        cursor.execute("""
        INSERT OR IGNORE INTO products
        (barcode, product_name, brand, risk_level, contains_gluten, 
         contains_cross_contamination, certified_gluten_free, ingredients_text, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (barcode, name, brand, risk, gluten, cross, certified, ingredients, source))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Veritabanı başarıyla oluşturuldu: {db_path}")


if __name__ == "__main__":
    init_database()
