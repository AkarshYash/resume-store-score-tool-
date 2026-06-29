@echo off
cls
echo ============================================================
echo    AI Resume Intelligence Platform - Frontend Launcher
echo ============================================================
echo.

REM Navigate to frontend directory
cd /d "%~dp0frontend"

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH!
    echo.
    echo Please install Node.js 18+ from: https://nodejs.org
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking Node.js installation...
node --version
npm --version
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo [2/3] Installing frontend dependencies...
    echo This will take a few minutes on first run...
    echo.
    call npm install
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies!
        echo.
        echo POSSIBLE CAUSES:
        echo   - No internet connection
        echo   - Insufficient disk space
        echo   - npm cache issues
        echo.
        echo SOLUTIONS:
        echo   1. Check internet connection
        echo   2. Try: npm cache clean --force
        echo   3. Try: npm install --legacy-peer-deps
        echo.
        pause
        exit /b 1
    )
    echo.
    echo ✓ Dependencies installed successfully!
) else (
    echo [2/3] Dependencies already installed!
)
echo.

echo [3/3] Starting frontend development server...
echo.
echo ============================================================
echo Frontend will run on: http://localhost:5173
echo Backend API should be:  http://localhost:8000
echo ============================================================
echo.
echo Press Ctrl+C to stop the frontend server
echo.
echo ============================================================
echo.

REM Start the development server
call npm run dev

pause
