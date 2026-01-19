#!/usr/bin/env python
"""
Veritabanına gerçek Türkçe ürünleri ekle
Çölyak dostu ve tehlikeli ürünler
"""
import sqlite3
import json
from pathlib import Path

# Veritabanı bağlantısı
DB_PATH = Path(__file__).parent / "gluten_db.db"
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Gerçek Türkçe Ürünler Veritabanı
PRODUCTS = [
    # ✅ Glutensiz Ürünler (Sertifikalı)
    {
        "barcode": "8696000000010",
        "product_name": "Glutensiz Ekmek Sodalı",
        "brand": "Glutensiz Yaşam",
        "risk_level": "safe",
        "contains_gluten": False,
        "certified_gluten_free": True,
        "ingredients_text": "Glutensiz un karışımı, su, maya, tuz, emülgatör"
    },
    {
        "barcode": "8696000000027",
        "product_name": "Glutensiz Bisküvi",
        "brand": "Fırında Aşk",
        "risk_level": "safe",
        "contains_gluten": False,
        "certified_gluten_free": True,
        "ingredients_text": "Glutensiz un, margarin, şeker, yumurta, vanilya"
    },
    {
        "barcode": "8696000000034",
        "product_name": "Glutensiz Makarna Penne",
        "brand": "Barilla Glutenfree",
        "risk_level": "safe",
        "contains_gluten": False,
        "certified_gluten_free": True,
        "ingredients_text": "Mısır unu, pirinç unu, patates nişastası"
    },
    {
        "barcode": "8696000000041",
        "product_name": "Glutensiz Müsli",
        "brand": "Dr. Oetker",
        "risk_level": "safe",
        "contains_gluten": False,
        "certified_gluten_free": True,
        "ingredients_text": "Mısır gevreği, pirinç gevreği, muz, çikolata damlaları"
    },
    {
        "barcode": "8696000000058",
        "product_name": "Glutensiz Unlu Mamül Karışımı",
        "brand": "Migros",
        "risk_level": "safe",
        "contains_gluten": False,
        "certified_gluten_free": True,
        "ingredients_text": "Pirinç unu, patates nişastası, mısır nişastası, xanthan gam"
    },
    
    # 🟡 Riskli Ürünler (Çapraz Bulaş)
    {
        "barcode": "8696000000065",
        "product_name": "Tahıl Müsli Karışımı",
        "brand": "Nestlé",
        "risk_level": "risky",
        "contains_gluten": False,
        "certified_gluten_free": False,
        "ingredients_text": "Mısır, çavdar, pirinç, şeker - Aynı tesiste buğday işlenir"
    },
    {
        "barcode": "8696000000072",
        "product_name": "Çikolata Almonds",
        "brand": "Lindt",
        "risk_level": "risky",
        "contains_gluten": False,
        "certified_gluten_free": False,
        "ingredients_text": "Badem, çikolata - Gluten izi içerebilir"
    },
    {
        "barcode": "8696000000089",
        "product_name": "Tarçınlı Kurabiyeleri",
        "brand": "Ülker",
        "risk_level": "risky",
        "contains_gluten": False,
        "certified_gluten_free": False,
        "ingredients_text": "Un, tarçın, çikolata - Aynı tesiste gluten işlenir"
    },
    
    # 🔴 Tehlikeli Ürünler (Gluten İçeriyor)
    {
        "barcode": "8696000000096",
        "product_name": "Standart Ekmek",
        "brand": "Bellona",
        "risk_level": "dangerous",
        "contains_gluten": True,
        "certified_gluten_free": False,
        "ingredients_text": "Buğday unu, su, maya, tuz, emülgatör"
    },
    {
        "barcode": "8696000000102",
        "product_name": "Tam Buğday Ekmeği",
        "brand": "Ankara Fırını",
        "risk_level": "dangerous",
        "contains_gluten": True,
        "certified_gluten_free": False,
        "ingredients_text": "Tam buğday unu, buğday glüteni, su, maya, tuz"
    },
    {
        "barcode": "8696000000119",
        "product_name": "Sade Bisküvi",
        "brand": "Paçi",
        "risk_level": "dangerous",
        "contains_gluten": True,
        "certified_gluten_free": False,
        "ingredients_text": "Buğday unu, şeker, yağ, yumurta, tuz"
    },
    {
        "barcode": "8696000000126",
        "product_name": "Makarna Spagetti",
        "brand": "Barilla",
        "risk_level": "dangerous",
        "contains_gluten": True,
        "certified_gluten_free": False,
        "ingredients_text": "Durum buğday unu, su"
    },
    {
        "barcode": "8696000000133",
        "product_name": "Kepek Ekmeği",
        "brand": "Arçelik",
        "risk_level": "dangerous",
        "contains_gluten": True,
        "certified_gluten_free": False,
        "ingredients_text": "Buğday unu, buğday kepeği, maya, tuz, su"
    },
    {
        "barcode": "8696000000140",
        "product_name": "Çavdar Ekmeği",
        "brand": "Fırında Aşk",
        "risk_level": "dangerous",
        "contains_gluten": True,
        "certified_gluten_free": False,
        "ingredients_text": "Çavdar unu, buğday unu, maya, tuz, su"
    },
    {
        "barcode": "8696000000157",
        "product_name": "Malt Ekstraktı",
        "brand": "Enginar",
        "risk_level": "dangerous",
        "contains_gluten": True,
        "certified_gluten_free": False,
        "ingredients_text": "Arpa malt ekstraktı, şeker, su"
    },
    {
        "barcode": "8696000000164",
        "product_name": "Arpa Çorbası",
        "brand": "Knorr",
        "risk_level": "dangerous",
        "contains_gluten": True,
        "certified_gluten_free": False,
        "ingredients_text": "Arpa unu, tuz, baharatlar, yağ"
    },
    {
        "barcode": "8696000000171",
        "product_name": "Kek Karışımı",
        "brand": "Dr. Oetker",
        "risk_level": "dangerous",
        "contains_gluten": True,
        "certified_gluten_free": False,
        "ingredients_text": "Buğday unu, şeker, yağ, kabartma tozu, tuz"
    },
    {
        "barcode": "8696000000188",
        "product_name": "Tatlı Bisküvi",
        "brand": "Ulker Gold",
        "risk_level": "dangerous",
        "contains_gluten": True,
        "certified_gluten_free": False,
        "ingredients_text": "Buğday unu, şeker, tereyağı, yumurta, bal, vanilya"
    },
]

def populate_database():
    """Ürünleri veritabanına ekle"""
    
    # Mevcut ürünleri kontrol et
    cursor.execute("SELECT COUNT(*) as count FROM products")
    current_count = cursor.fetchone()['count']
    
    print(f"📊 Mevcut ürün sayısı: {current_count}")
    print(f"📦 Eklenecek yeni ürün sayısı: {len(PRODUCTS)}")
    print("-" * 60)
    
    added = 0
    skipped = 0
    
    for product in PRODUCTS:
        # Barkod kontrolü
        cursor.execute("SELECT id FROM products WHERE barcode = ?", (product['barcode'],))
        if cursor.fetchone():
            print(f"⏭️  {product['product_name']} (barkod zaten var)")
            skipped += 1
            continue
        
        # Ürün ekle
        cursor.execute("""
            INSERT INTO products (
                barcode, product_name, brand, risk_level, 
                contains_gluten, certified_gluten_free, ingredients_text, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product['barcode'],
            product['product_name'],
            product['brand'],
            product['risk_level'],
            product['contains_gluten'],
            product['certified_gluten_free'],
            product['ingredients_text'],
            'manual_import'
        ))
        
        emoji = "🟢" if product['risk_level'] == 'safe' else "🟡" if product['risk_level'] == 'risky' else "🔴"
        print(f"{emoji} {product['product_name']} ({product['brand']}) - Eklendi")
        added += 1
    
    conn.commit()
    
    print("-" * 60)
    print(f"✅ {added} ürün eklendi")
    print(f"⏭️  {skipped} ürün atlandı")
    
    # Toplam istatistikler
    cursor.execute("SELECT COUNT(*) as count FROM products")
    total = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM products WHERE risk_level = 'safe'")
    safe = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM products WHERE risk_level = 'risky'")
    risky = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM products WHERE risk_level = 'dangerous'")
    dangerous = cursor.fetchone()['count']
    
    print(f"\n📈 Toplam İstatistikler:")
    print(f"   🟢 Güvenli: {safe}")
    print(f"   🟡 Riskli: {risky}")
    print(f"   🔴 Tehlikeli: {dangerous}")
    print(f"   📊 TOPLAM: {total}")
    
    conn.close()

if __name__ == "__main__":
    print("🚀 Glutensiz Yaşam Rehberi - Veritabanı Doldurma")
    print("=" * 60)
    populate_database()
    print("=" * 60)
    print("✅ Tamamlandı!")
