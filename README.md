# Backend - Glutensiz Yaşam Rehberi API

FastAPI tabanlı backend uygulaması. Barkod tarama, OCR analizi ve ürün yönetimi işlevlerini sağlar.

## 🚀 Kurulum

### 1. Python Environment Oluştur
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 3. Environment Dosyası Oluştur
```bash
cp .env.example .env
# .env dosyasını gerekirse düzenle
```

### 4. Veritabanını Başlat
```bash
python -c "from db.init_db import init_database; init_database()"
```

## 🏃 Çalıştırma

```bash
# Development modu (auto-reload)
python main.py

# veya uvicorn ile
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API şu adreste erişebilir:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 📚 API Endpoints

### Barkod Tarama
```
POST /api/v1/scan/barcode
```

### İçindekiler Analizi
```
POST /api/v1/analyze/ingredients
```

### Ürün Arama
```
GET /api/v1/products/search?q=ekmek&limit=10
```

Detaylı API dokümantasyonu için `/docs`'a ziyaret et.

## 📂 Dosya Yapısı

```
backend/
├── main.py              # FastAPI ana dosyası
├── config.py            # Konfigürasyon
├── models.py            # Pydantic modelleri
├── requirements.txt     # Bağımlılıklar
│
├── routes/              # API endpoint'leri
│   ├── barcode.py
│   ├── ingredients.py
│   └── products.py
│
├── services/            # İşlem logikleri
│   ├── ocr_engine.py
│   ├── nlp_analyzer.py
│   └── barcode_service.py
│
├── utils/               # Yardımcı fonksiyonlar
│   ├── logger.py
│   ├── validators.py
│   └── helpers.py
│
└── db/                  # Veritabanı
    ├── database.py
    ├── init_db.py
    └── gluten_db.db
```

## 🔧 Konfigürasyon

`.env` dosyasında ayarlanabilir:

- `API_HOST` - API dinleme adresi
- `API_PORT` - API portu
- `DATABASE_PATH` - Veritabanı dosyasının yolu
- `CORS_ORIGINS` - İzin verilen domain'ler
- `LOG_LEVEL` - Log seviyesi

## 📦 Bağımlılıklar

- **FastAPI** - Web framework
- **EasyOCR** - Optik karakter tanıması
- **Transformers** - NLP modelleri
- **SQLite** - Veritabanı
- **Loguru** - Logging

## 🐛 Debugging

Loglar şu konumlarda:
- **Console:** Gerçek zamanlı loglar
- **File:** `logs/app.log`

## ⚙️ Production Deployment

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## 📝 Lisans

MIT
