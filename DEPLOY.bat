@echo off
echo.
echo ========================================
echo   DEPLOYING TO GITHUB
echo ========================================
echo.

cd /d "%~dp0"

echo Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo   SUCCESS!
echo ========================================
echo.
echo Code pushed to: https://github.com/AkarshYash/resume-store-score-tool-.git
echo.
echo NEXT STEPS:
echo 1. Go to https://render.com
echo 2. Click "New +" - "Web Service"
echo 3. Select your GitHub repo
echo 4. Root Directory: backend
echo 5. Build: pip install -r requirements.txt
echo 6. Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
echo 7. Deploy!
echo.
echo OR use Railway for one-click deployment:
echo   npm install -g @railway/cli
echo   railway login
echo   railway up
echo.
pause
