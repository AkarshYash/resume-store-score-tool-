@echo off
echo ============================================================
echo Resume Intelligence Platform - Complete Setup and Run
echo ============================================================
echo.

echo Step 1: Setting up Python virtual environment...
cd backend
if not exist venv (
    python -m venv venv
    echo Virtual environment created!
) else (
    echo Virtual environment already exists!
)
echo.

echo Step 2: Installing backend dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install fastapi uvicorn[standard] sqlalchemy pydantic pydantic-settings python-dotenv python-multipart email-validator aiofiles

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo Please make sure Python is installed and accessible.
    pause
    exit /b 1
)

echo.
echo Step 3: Creating database...
python -c "from app.database import init_db; init_db(); print('Database created successfully!')"

echo.
echo ============================================================
echo Backend setup complete!
echo ============================================================
echo.
echo Starting backend server on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
echo After the server starts, open a NEW terminal and run:
echo cd /d D:\Resume_Intelligence_Platform\frontend
echo npm install
echo npm run dev
echo.
echo ============================================================
echo.

python run.py
