@echo off
cls
echo ============================================================
echo    AI Resume Intelligence Platform - Complete Launcher
echo ============================================================
echo.
echo This script will:
echo   1. Setup Python virtual environment (if needed)
echo   2. Install backend dependencies
echo   3. Create database
echo   4. Start backend server
echo   5. Give instructions for frontend
echo.
echo ============================================================
echo.

REM Store original directory
set "ORIGINAL_DIR=%CD%"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.10 or higher from python.org
    pause
    exit /b 1
)

echo [1/6] Checking Python installation...
python --version
echo.

REM Navigate to backend
cd /d "%~dp0backend"

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [2/6] Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
) else (
    echo [2/6] Virtual environment already exists!
)
echo.

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)
echo.

REM Upgrade pip
echo [4/6] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

REM Install minimal dependencies first (lightweight)
echo [5/6] Installing backend dependencies...
echo Installing core packages (this may take a few minutes)...
pip install fastapi uvicorn[standard] sqlalchemy pydantic pydantic-settings python-dotenv python-multipart email-validator aiofiles --quiet

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo.
    echo POSSIBLE CAUSES:
    echo   - Not enough disk space
    echo   - No internet connection
    echo   - pip cache issues
    echo.
    echo SOLUTIONS:
    echo   1. Check available disk space
    echo   2. Try: pip cache purge
    echo   3. Try manual install: pip install fastapi uvicorn sqlalchemy
    echo.
    pause
    exit /b 1
)

echo Core dependencies installed successfully!
echo.

REM Initialize database
echo [6/6] Creating database...
python -c "from app.database import init_db; init_db(); print('✓ Database created successfully!')"
if errorlevel 1 (
    echo WARNING: Could not initialize database automatically.
    echo The database will be created on first server start.
)
echo.

echo ============================================================
echo ✓ Backend setup complete!
echo ============================================================
echo.
echo Starting backend server...
echo.
echo Backend will run on: http://localhost:8000
echo API Documentation:   http://localhost:8000/docs
echo.
echo ============================================================
echo NEXT STEP - FRONTEND SETUP:
echo ============================================================
echo.
echo After the backend starts, open a NEW terminal and run:
echo.
echo   cd "%ORIGINAL_DIR%\frontend"
echo   npm install
echo   npm run dev
echo.
echo Then open: http://localhost:5173
echo.
echo ============================================================
echo.
echo Press Ctrl+C to stop the backend server
echo.
echo ============================================================
echo.

REM Start the server
python run.py

REM If server stops, pause to show any errors
pause
