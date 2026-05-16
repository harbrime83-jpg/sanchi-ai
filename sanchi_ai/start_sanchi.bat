@echo off
title Sanchi AI - Starting...
color 0B

echo.
echo  ╔═══════════════════════════════════════╗
echo  ║                                       ║
echo  ║        SANCHI AI - Loading...          ║
echo  ║                                       ║
echo  ╚═══════════════════════════════════════╝
echo.

cd /d "%~dp0"
python main.py

if %errorlevel% neq 0 (
    echo.
    echo  [!] GUI failed. Starting console mode...
    echo.
    python main.py --mode console
)

pause