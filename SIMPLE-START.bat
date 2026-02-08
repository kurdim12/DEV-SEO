@echo off
echo ========================================
echo   DevSEO - Quick Start (No Docker!)
echo ========================================
echo.
echo This will start DevSEO using SQLite
echo (No Docker or PostgreSQL needed)
echo.

:menu
echo.
echo What would you like to do?
echo.
echo [1] First Time Setup (Run once)
echo [2] Start Backend Server
echo [3] Start Frontend Server
echo [4] Start Both (Backend + Frontend)
echo [5] Open in Browser
echo [0] Exit
echo.
set /p choice="Choose (0-5): "

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto backend
if "%choice%"=="3" goto frontend
if "%choice%"=="4" goto both
if "%choice%"=="5" goto browser
if "%choice%"=="0" goto end
goto menu

:setup
echo.
echo ========================================
echo   Setting Up DevSEO...
echo ========================================
echo.

echo [1/4] Setting up Python backend...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo.

echo [2/4] Creating database...
alembic upgrade head
echo.

echo [3/4] Setting up Node.js frontend...
cd ..\frontend
call npm install
echo.

echo [4/4] Setup complete!
echo.
echo ========================================
echo   Ready to go!
echo ========================================
echo.
echo Next steps:
echo 1. Choose option [4] to start both servers
echo 2. Choose option [5] to open in browser
echo.
pause
cd ..
goto menu

:backend
echo.
echo Starting Backend Server...
start "DevSEO Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && echo Backend running at http://localhost:8000 && python -m app.main"
echo.
echo Backend server starting...
echo Wait 5 seconds, then press any key to continue
timeout /t 5 /nobreak >nul
goto menu

:frontend
echo.
echo Starting Frontend Server...
start "DevSEO Frontend" cmd /k "cd /d %~dp0frontend && echo Frontend running at http://localhost:3000 && npm run dev"
echo.
echo Frontend server starting...
echo Wait 5 seconds, then press any key to continue
timeout /t 5 /nobreak >nul
goto menu

:both
echo.
echo Starting Both Servers...
echo.
start "DevSEO Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && echo Backend running at http://localhost:8000 && python -m app.main"
timeout /t 2 /nobreak >nul
start "DevSEO Frontend" cmd /k "cd /d %~dp0frontend && echo Frontend running at http://localhost:3000 && npm run dev"
echo.
echo ========================================
echo   Servers Starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Wait 10 seconds for servers to start,
echo then choose option [5] to open in browser
echo.
pause
goto menu

:browser
echo.
echo Opening DevSEO in browser...
start http://localhost:3000
echo.
echo If nothing opens, manually go to:
echo http://localhost:3000
echo.
pause
goto menu

:end
echo.
echo Goodbye!
echo.
echo To stop servers, close their windows or press Ctrl+C
echo.
pause
exit
