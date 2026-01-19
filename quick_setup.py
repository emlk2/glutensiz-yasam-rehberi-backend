"""
Hızlı test ve database initialization
"""
import sqlite3
from pathlib import Path

# Veritabanı yolunu belirle
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "gluten_db.db"

# db klasörünü oluştur
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Veritabanını oluştur
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("🚀 Veritabanı oluşturuluyor...")

# ÜRÜNLER TABLOSU
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

# GLUTEN TEMİZLEYİCİLERİ TABLOSU
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

# İNDEKSLER
cursor.execute("CREATE INDEX IF NOT EXISTS idx_barcode ON products(barcode);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_name ON products(product_name);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_ingredient ON flagged_ingredients(ingredient);")

# BAŞLANGIÇ VERİLERİ - Gluten Tetikleyicileri
gluten_ingredients = [
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

# ÖRNEK GÜVENLİ ÜRÜNLER
safe_products = [
    ("8696000000001", "Glutensiz Ekmek", "ABC Marka", "safe", False, False, True,
     "Un, Su, Tuz", "colyak.org.tr"),
    ("8696000000002", "Glutensiz Makarna", "XYZ Marka", "safe", False, False, True,
     "Mısır Unu, Su", "colyak.org.tr"),
    ("8696000000003", "Sade Ekmek", "Normal Marka", "dangerous", True, False, False,
     "Buğday Unu, Su, Tuz", "manual"),
]

for barcode, name, brand, risk, gluten, cross, certified, ingredients, source in safe_products:
    cursor.execute("""
    INSERT OR IGNORE INTO products
    (barcode, product_name, brand, risk_level, contains_gluten, 
     contains_cross_contamination, certified_gluten_free, ingredients_text, source)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (barcode, name, brand, risk, gluten, cross, certified, ingredients, source))

conn.commit()

# İSTATİSTİKLER
cursor.execute("SELECT COUNT(*) FROM products")
total_products = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM flagged_ingredients")
total_ingredients = cursor.fetchone()[0]

conn.close()

print(f"✅ Veritabanı başarıyla oluşturuldu!")
print(f"📍 Konum: {DB_PATH}")
print(f"📊 Ürün sayısı: {total_products}")
print(f"🏷️  Gluten tetikleyici sayısı: {total_ingredients}")
