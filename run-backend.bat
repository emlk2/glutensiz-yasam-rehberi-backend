@echo off
REM Backend - API sunucusu başlatma

cd /d "%~dp0"

echo Checking database...
venv\Scripts\python.exe test_setup.py

if errorlevel 1 (
    echo Backend setup failed!
    exit /b 1
)

echo.
echo ============================================================
echo Backend API başlatılıyor...
echo ============================================================
echo.
echo API URL: http://localhost:8000
echo Swagger UI: http://localhost:8000/docs
echo.

venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
