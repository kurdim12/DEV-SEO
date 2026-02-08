@echo off
echo ========================================
echo Starting DevSEO Backend
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/3] Running database migrations...
alembic upgrade head

echo [3/3] Starting FastAPI server...
echo.
echo Backend will be available at: http://localhost:8000
echo API Docs available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
python -m app.main
