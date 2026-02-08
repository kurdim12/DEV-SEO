@echo off
echo Starting DevSEO Background Worker...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python -m app.worker
pause
