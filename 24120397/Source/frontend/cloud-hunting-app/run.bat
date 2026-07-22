@echo off
title Start Cloud Hunting App
echo ===========================================
echo       STARTING CLOUD HUNTING (VITE)
echo ===========================================
echo.

:: Move to script directory
cd /d "%~dp0"

echo [*] Checking and installing dependencies...
call npm install

echo.
echo [*] Opening browser...
:: Open default browser
start http://localhost:5173

echo [*] Starting Development Server...
echo.
:: Run server
npm run dev

pause
