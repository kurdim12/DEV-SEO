@echo off
echo ========================================
echo DevSEO - Full Stack Setup
echo ========================================
echo.
echo This script will help you start DevSEO
echo.

:menu
echo Please choose an option:
echo.
echo [1] Start Docker (PostgreSQL + Redis)
echo [2] Setup Backend (First time only)
echo [3] Start Backend Server
echo [4] Setup Frontend (First time only)
echo [5] Start Frontend Server
echo [6] Open Application in Browser
echo [7] View Logs/Status
echo [0] Exit
echo.
set /p choice="Enter your choice (0-7): "

if "%choice%"=="1" goto docker
if "%choice%"=="2" goto setup_backend
if "%choice%"=="3" goto start_backend
if "%choice%"=="4" goto setup_frontend
if "%choice%"=="5" goto start_frontend
if "%choice%"=="6" goto open_browser
if "%choice%"=="7" goto logs
if "%choice%"=="0" goto end

echo Invalid choice. Please try again.
echo.
goto menu

:docker
echo.
echo Starting Docker containers...
docker compose up -d
echo.
echo Docker containers started!
echo - PostgreSQL: localhost:5432
echo - Redis: localhost:6379
echo.
pause
goto menu

:setup_backend
echo.
echo Setting up backend...
cd backend
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
alembic upgrade head
echo.
echo Backend setup complete!
echo.
pause
goto menu

:start_backend
echo.
echo Starting backend server...
start cmd /k "cd /d %~dp0 && start-backend.bat"
echo Backend server starting in new window...
timeout /t 2 /nobreak >nul
goto menu

:setup_frontend
echo.
echo Setting up frontend...
cd frontend
npm install
echo.
echo Frontend setup complete!
echo.
pause
goto menu

:start_frontend
echo.
echo Starting frontend server...
start cmd /k "cd /d %~dp0 && start-frontend.bat"
echo Frontend server starting in new window...
timeout /t 2 /nobreak >nul
goto menu

:open_browser
echo.
echo Opening DevSEO in browser...
start http://localhost:3000
timeout /t 1 /nobreak >nul
goto menu

:logs
echo.
echo Checking Docker status...
docker compose ps
echo.
echo To see backend logs: Open the Backend Server window
echo To see frontend logs: Open the Frontend Server window
echo.
pause
goto menu

:end
echo.
echo Goodbye!
exit
