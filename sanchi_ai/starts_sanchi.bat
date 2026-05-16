@echo off
title Sanchi AI
color 0D

echo.
echo   Starting Sanchi AI...
echo.

cd /d "%~dp0"
python sanchi_app.py

if %errorlevel% neq 0 (
    echo.
    echo   Trying console mode...
    python sanchi_app.py --console
)

pause