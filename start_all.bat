@echo off
echo Starting DevSEO Platform...
echo.
echo This will start:
echo   1. Backend API (Port 8000)
echo   2. Background Worker
echo   3. Frontend (Port 3000)
echo.

REM Start backend in new window
start "DevSEO Backend" cmd /k "cd /d %~dp0\backend && venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start worker in new window
start "DevSEO Worker" cmd /k "cd /d %~dp0\backend && venv\Scripts\activate.bat && python -m app.worker"

REM Wait a moment for worker to start
timeout /t 2 /nobreak > nul

REM Start frontend in new window
start "DevSEO Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo All services started!
echo   - Backend API: http://localhost:8000
echo   - Frontend: http://localhost:3000
echo   - API Docs: http://localhost:8000/docs
echo.
echo Close this window or press Ctrl+C to stop monitoring
echo (Note: Services will continue running in separate windows)
pause
