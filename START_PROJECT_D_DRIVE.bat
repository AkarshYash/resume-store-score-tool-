@echo off
cls
echo ============================================================
echo Resume Intelligence Platform - Starting from D: Drive
echo ============================================================
echo.

cd /d D:\Resume_Intelligence_Platform\backend

echo Step 1: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 2: Installing dependencies (if needed)...
pip install fastapi uvicorn[standard] sqlalchemy pydantic pydantic-settings python-dotenv python-multipart email-validator aiofiles

if errorlevel 1 (
    echo.
    echo Note: Some packages may already be installed
)

echo.
echo Step 3: Creating database...
python -c "from app.database import init_db; init_db(); print('Database ready!')"

echo.
echo ============================================================
echo Starting Backend Server
echo ============================================================
echo.
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.
echo IMPORTANT: After the server starts, open a NEW Command Prompt and run:
echo   cd /d D:\Resume_Intelligence_Platform\frontend
echo   npm install
echo   npm run dev
echo.
echo Then open in browser: http://localhost:5173
echo ============================================================
echo.

python run.py
pause
