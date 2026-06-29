@echo off
cls
color 0A
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║   AI RESUME INTELLIGENCE PLATFORM - QUICK LAUNCHER           ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 🚀 Starting your AI Resume Intelligence Platform...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ ERROR: Python not found!
    echo.
    echo 📥 Install Python 3.10+ from: https://python.org
    echo.
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ ERROR: Node.js not found!
    echo.
    echo 📥 Install Node.js 18+ from: https://nodejs.org
    echo.
    pause
    exit /b 1
)

echo ✅ Python installed: 
python --version
echo ✅ Node.js installed: 
node --version
echo.
echo ────────────────────────────────────────────────────────────────
echo.

REM Backend Setup
echo 🔧 STEP 1: Setting up Backend...
cd /d "%~dp0backend"

if not exist venv (
    echo    Creating virtual environment...
    python -m venv venv
)

echo    Activating virtual environment...
call venv\Scripts\activate.bat

echo    Installing dependencies (this may take a moment)...
pip install --quiet --upgrade pip
pip install --quiet fastapi uvicorn[standard] sqlalchemy pydantic pydantic-settings python-dotenv python-multipart email-validator aiofiles

if errorlevel 1 (
    color 0C
    echo.
    echo ❌ Failed to install backend dependencies!
    echo.
    echo 💡 TRY THIS:
    echo    1. Make sure you have internet connection
    echo    2. Run: pip cache purge
    echo    3. Run this script again
    echo.
    pause
    exit /b 1
)

echo    Creating database...
python -c "from app.database import init_db; init_db(); print('   ✅ Database ready!')" 2>nul

echo.
echo ✅ Backend setup complete!
echo.
echo ────────────────────────────────────────────────────────────────
echo.

REM Start Backend
echo 🚀 Starting Backend Server...
echo.
echo    Backend API: http://localhost:8000
echo    API Docs:    http://localhost:8000/docs
echo.
echo ────────────────────────────────────────────────────────────────
echo.
echo 📝 NEXT: Open a NEW terminal and run frontend:
echo.
echo    1. Open NEW Command Prompt
echo    2. Run: cd /d "%~dp0frontend"
echo    3. Run: npm install
echo    4. Run: npm run dev
echo    5. Open: http://localhost:5173
echo.
echo OR simply double-click: START_FRONTEND.bat
echo.
echo ────────────────────────────────────────────────────────────────
echo.
echo Press Ctrl+C to stop the backend
echo.
echo ════════════════════════════════════════════════════════════════
echo.

python run.py

pause
