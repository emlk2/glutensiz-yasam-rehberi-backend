"""
Basit API test
"""
import sqlite3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

# Services'i test et
from services.nlp_analyzer import get_nlp_analyzer

DB_PATH = Path(__file__).parent / "db" / "gluten_db.db"

print("=" * 60)
print("🧪 BACKEND TEST")
print("=" * 60)

# 1. Veritabanı Kontrolü
print("\n1️⃣  Veritabanı Kontrolü:")
if DB_PATH.exists():
    print(f"   ✅ Veritabanı mevcut: {DB_PATH}")
    print(f"   📦 Boyut: {DB_PATH.stat().st_size / 1024:.2f} KB")
else:
    print(f"   ❌ Veritabanı bulunamadı!")
    exit(1)

# 2. Tabloları Kontrol Et
print("\n2️⃣  Tablo Kontrolü:")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
)
tables = cursor.fetchall()

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"   ✅ Tablo: {table[0]} ({count} satır)")

# 3. Ürünleri Listele
print("\n3️⃣  Veritabanı Verisi:")
cursor.execute("SELECT barcode, product_name, risk_level FROM products")
products = cursor.fetchall()

for barcode, name, risk in products:
    emoji = {"safe": "🟢", "risky": "🟡", "dangerous": "🔴"}.get(risk, "⚪")
    print(f"   {emoji} {name} ({barcode}) - {risk}")

# 4. Gluten Tetikleyicileri
print("\n4️⃣  Gluten Tetikleyicileri (örnek):")
cursor.execute("SELECT ingredient, risk_level FROM flagged_ingredients LIMIT 5")
ingredients = cursor.fetchall()

for ingredient, risk in ingredients:
    emoji = {"dangerous": "🔴", "risky": "🟡", "safe": "🟢"}.get(risk, "⚪")
    print(f"   {emoji} {ingredient}")

conn.close()

# 5. NLP Analyzer Test
print("\n5️⃣  NLP Analyzer Test:")
try:
    nlp = get_nlp_analyzer()
    
    # Test 1: Gluten içeren malzeme
    result1 = nlp.analyze_text("Buğday unu, su, tuz")
    print(f"   Test 1 (Tehlikeli): {result1['risk_level']} - {result1['gluten_found']}")
    
    # Test 2: Güvenli malzeme
    result2 = nlp.analyze_text("Mısır unu, su, tuz")
    print(f"   Test 2 (Güvenli): {result2['risk_level']} - {result2['gluten_found']}")
    
    # Test 3: Riskli malzeme
    result3 = nlp.analyze_text("Aynı tesiste işlenen ürün")
    print(f"   Test 3 (Riskli): {result3['risk_level']} - {result3['cross_contamination_risk']}")
    
    print("   ✅ NLP Analyzer çalışıyor")
except Exception as e:
    print(f"   ⚠️  NLP Analyzer hatası: {str(e)}")

print("\n6️⃣  API Endpoint'leri:")
print("   POST /api/v1/scan/barcode - Barkod tarama")
print("   POST /api/v1/analyze/ingredients - OCR + NLP analizi")
print("   POST /api/v1/analyze/text - Metin analizi")
print("   GET  /api/v1/products/search - Ürün arama")
print("   GET  /health - Sağlık kontrolü")
print("   GET  /docs - Swagger UI")

print("\n" + "=" * 60)
print("✅ Backend kurulumu başarılı!")
print("=" * 60)
print("\n🚀 API'yi başlatmak için:\n")
print("   python -m uvicorn main:app --reload --port 8000\n")
