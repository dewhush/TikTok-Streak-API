@echo off
echo.
echo ===============================================
echo       TikTok Streak API Server
echo       Created by: dewhush
echo ===============================================
echo.
echo Starting API server on http://localhost:8000
echo Swagger docs: http://localhost:8000/docs
echo ReDoc: http://localhost:8000/redoc
echo.
echo Press Ctrl+C to stop
echo ===============================================
echo.
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
pause
