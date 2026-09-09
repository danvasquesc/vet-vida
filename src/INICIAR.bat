@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py backend\server.py
) else (
    python backend\server.py
)
pause
