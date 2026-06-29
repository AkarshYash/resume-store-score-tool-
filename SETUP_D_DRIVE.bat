@echo off
cls
echo ============================================================
echo Resume Intelligence Platform - Fresh Setup on D: Drive
echo ============================================================
echo.

cd /d D:\Resume_Intelligence_Platform\backend

echo Step 1: Creating NEW virtual environment...
python -m venv venv_new

echo.
echo Step 2: Activating virtual environment...
call venv_new\Scripts\activate.bat

echo.
echo Step 3: Installing all dependencies...
echo This will take a few minutes...
echo.

pip install fastapi uvicorn[standard] sqlalchemy pydantic pydantic-settings python-dotenv python-multipart email-validator aiofiles

echo.
echo Step 4: Creating database...
python -c "from app.database import init_db; init_db(); print('✓ Database created!')"

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo To start the backend:
echo   cd /d D:\Resume_Intelligence_Platform\backend
echo   venv_new\Scripts\activate
echo   python run.py
echo.
pause
