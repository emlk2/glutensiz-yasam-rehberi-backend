#!/usr/bin/env python
"""
Backend API Runner
"""
import subprocess
import sys
from pathlib import Path

backend_dir = Path(__file__).parent

# Gerekli paketler
required_packages = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "pydantic-settings",
    "python-multipart",
    "loguru",
    "python-dotenv"
]

print("📦 Gerekli paketler yükleniyor...")
for package in required_packages:
    subprocess.run(
        [sys.executable, "-m", "pip", "install", package, "-q"],
        cwd=backend_dir,
        check=False
    )

print("✅ Paketler hazır!")
print("\n" + "=" * 60)
print("🚀 API BAŞLATILIYOR...")
print("=" * 60)
print("\n📍 http://localhost:8000")
print("📚 Swagger UI: http://localhost:8000/docs")
print("📖 ReDoc: http://localhost:8000/redoc")
print("\n" + "=" * 60 + "\n")

# API'yi başlat
subprocess.run(
    [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
    cwd=backend_dir
)
