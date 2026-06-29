@echo off
echo ============================================================
echo Moving Resume Intelligence Platform to D: Drive
echo ============================================================
echo.

echo Creating directory on D: drive...
mkdir "D:\Resume_Intelligence_Platform" 2>nul

echo Copying project files...
xcopy /E /I /Y "backend" "D:\Resume_Intelligence_Platform\backend"
xcopy /E /I /Y "frontend" "D:\Resume_Intelligence_Platform\frontend"
xcopy /E /I /Y "docs" "D:\Resume_Intelligence_Platform\docs"
xcopy /E /I /Y "scripts" "D:\Resume_Intelligence_Platform\scripts"
copy /Y "*.md" "D:\Resume_Intelligence_Platform\"
copy /Y "*.bat" "D:\Resume_Intelligence_Platform\"

echo.
echo ============================================================
echo Project moved successfully to D:\Resume_Intelligence_Platform
echo ============================================================
echo.
echo Next steps:
echo 1. cd /d D:\Resume_Intelligence_Platform
echo 2. Run: setup_and_run.bat
echo.
pause
