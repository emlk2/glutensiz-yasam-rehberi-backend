#!/usr/bin/env python3
"""
Backend API Starter
"""
import subprocess
import sys
from pathlib import Path

backend_dir = Path(__file__).parent / "backend"

print("=" * 60)
print("🚀 BACKEND API BAŞLATILIYOR")
print("=" * 60)
print("\n📍 Dizin:", backend_dir)
print("🔗 API URL: http://localhost:8000")
print("📚 Docs: http://localhost:8000/docs")
print("\n" + "=" * 60)
print()

# Eksik paketleri yükle
print("Gerekli paketler yükleniyor...")
subprocess.run(
    [str(backend_dir / "venv" / "Scripts" / "python.exe"), "-m", "pip", "install", 
     "python-multipart", "aiofiles", "--quiet"],
    cwd=backend_dir,
    capture_output=True
)

# API'yi başlat
print("✅ Hazır!\n")
subprocess.run(
    [str(backend_dir / "venv" / "Scripts" / "python.exe"), "-m", "uvicorn", 
     "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
    cwd=backend_dir
)
