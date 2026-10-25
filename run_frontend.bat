@echo off
cd /d "%~dp0frontend"
if not exist "node_modules" call npm install
echo.
echo Website running at http://localhost:5173
call npm run dev
