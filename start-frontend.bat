@echo off
echo ========================================
echo Starting DevSEO Frontend
echo ========================================
echo.

cd /d "%~dp0frontend"

echo Starting Next.js development server...
echo.
echo Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.
npm run dev
