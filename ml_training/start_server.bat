@echo off
REM Start the Stain Detection API Server (Windows)

cd /d "%~dp0"

echo.
echo ========================================
echo Stain Detection API Server Startup
echo ========================================
echo.
echo Looking for virtual environment...

if exist "venv_gpu\Scripts\activate.bat" (
    call "venv_gpu\Scripts\activate.bat"
) else if exist "venv_gpu_311\Scripts\activate.bat" (
    call "venv_gpu_311\Scripts\activate.bat"
) else (
    echo Error: No Python virtual environment found.
    echo Create one using: python -m venv venv_gpu
    pause
    exit /b 1
)

if %ERRORLEVEL% NEQ 0 (
    echo Error: Could not activate Python environment
    pause
    exit /b 1
)

echo.
echo Installing required Python packages if missing...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install flask flask-cors ultralytics pillow opencv-python >nul 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install Python dependencies.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting Flask server on http://localhost:5000
echo ========================================
echo.
echo To test the API:

echo   curl http://localhost:5000/health

echo.

echo Press Ctrl+C to stop the server.

echo.

python inference_server.py

pause
