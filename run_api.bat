@echo off
echo ============================================
echo   TikTok Streak API Server
echo ============================================
echo.
echo Starting API server on http://localhost:8000
echo Swagger docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo ============================================
echo.
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
pause
