@echo off
REM Quick training script for annotated datasets
REM This script handles everything: organizing datasets and training

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo YOLOv11 TRAINING ON ANNOTATED DATASETS
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import ultralytics" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

:menu
cls
echo.
echo ============================================================
echo YOLOv11 DATASET TRAINING
echo ============================================================
echo.
echo Your annotated datasets should be in:
echo   datasets/raw/oil/     (cooking oil stain images)
echo   datasets/raw/mud/     (mud stain images)
echo   datasets/raw/ink/     (ink stain images)
echo.
echo.
echo 1. Organize & Train (RECOMMENDED)
echo    - Auto-detects your dataset format
echo    - Splits into train/val/test
echo    - Starts training immediately
echo.
echo 2. Just Verify Organization
echo    - Check if datasets are ready
echo    - Don't start training
echo.
echo 3. Train on Already Organized Data
echo    - Use existing processed/ folder
echo.
echo 4. View Configuration
echo    - Check model size, epochs, etc.
echo.
echo 5. Exit
echo.
set /p choice="Enter choice (1-5): "

if "%choice%"=="1" goto train
if "%choice%"=="2" goto verify
if "%choice%"=="3" goto train_existing
if "%choice%"=="4" goto config
if "%choice%"=="5" goto end

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

:train
cls
echo.
echo ============================================================
echo ORGANIZE DATASETS & START TRAINING
echo ============================================================
echo.
echo This script will:
echo 1. Detect your dataset format (class folders, flat, etc.)
echo 2. Organize images into train/val/test splits
echo 3. Verify the organization
echo 4. Start YOLOv11 training
echo.
echo Press ENTER to continue (or CTRL+C to cancel)...
pause >nul

python scripts/organize_and_train.py

if errorlevel 1 (
    echo ERROR: Training failed!
    pause
) else (
    echo.
    echo ============================================================
    echo ✓ TRAINING COMPLETE!
    echo ============================================================
    echo.
    echo Your model is saved here:
    echo   runs/classify/stain_detection_yolov11/weights/best.pt
    echo.
    echo Next steps:
    echo   1. Evaluate: python scripts/evaluate_yolov11.py
    echo   2. Test image: python scripts/inference_yolov11.py --model runs/classify/stain_detection_yolov11/weights/best.pt --image ^<image.jpg^>
    echo.
    pause
)
goto menu

:verify
cls
echo.
echo ============================================================
echo VERIFY DATASET ORGANIZATION
echo ============================================================
echo.
python scripts/organize_and_train.py --verify-only

if errorlevel 1 (
    echo ERROR: Verification failed!
    pause
) else (
    echo.
    echo ✓ Dataset is ready for training
    echo.
    echo Run option 1 to start training.
    pause
)
goto menu

:train_existing
cls
echo.
echo ============================================================
echo TRAIN ON ORGANIZED DATA
echo ============================================================
echo.
echo Using datasets from: datasets/processed/
echo.
python scripts/train_yolov11.py --data-path datasets/processed

if errorlevel 1 (
    echo ERROR: Training failed!
    pause
) else (
    echo.
    echo ✓ TRAINING COMPLETE!
    pause
)
goto menu

:config
cls
echo.
echo ============================================================
echo CONFIGURATION (config.yaml)
echo ============================================================
echo.
type config.yaml
echo.
pause
goto menu

:end
echo.
echo ============================================================
echo QUICK SETUP SUMMARY
echo ============================================================
echo.
echo 1. Place datasets in: datasets/raw/
echo    - oil/, mud/, ink/
echo.
echo 2. Run this script and choose option 1
echo    python train_dataset.bat
echo.
echo 3. Training will start automatically
echo.
echo 4. Results saved to:
echo    runs/classify/stain_detection_yolov11/weights/best.pt
echo.
echo ============================================================
echo.
endlocal
