@echo off
REM Quick Start Script for YOLOv11 ML Training Pipeline on Windows

setlocal enabledelayedexpansion

:menu
cls
echo.
echo ============================================================
echo STAIN DETECTION with YOLOv11 - QUICK START
echo ============================================================
echo.
echo 1. Install dependencies
echo 2. Prepare dataset
echo 3. Train YOLOv11 model
echo 4. Evaluate model
echo 5. Run inference (single image)
echo 6. Run batch inference
echo 7. View configuration
echo 8. View YOLOv11 documentation
echo 9. Exit
echo.
set /p choice="Enter choice (1-9): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto prepare
if "%choice%"=="3" goto train
if "%choice%"=="4" goto evaluate
if "%choice%"=="5" goto inference
if "%choice%"=="6" goto batch
if "%choice%"=="7" goto config
if "%choice%"=="8" goto docs
if "%choice%"=="9" goto end

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

:install
echo.
echo Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Installation failed!
    pause
) else (
    echo Dependencies installed successfully!
    pause
)
goto menu

:prepare
echo.
echo Choose format:
echo 1. Directory structure (train/val/test folders)
echo 2. Numpy arrays
set /p format="Enter choice (1-2): "

if "%format%"=="1" (
    python scripts\prepare_dataset.py --format directory
) else if "%format%"=="2" (
    python scripts\prepare_dataset.py --format numpy
) else (
    echo Invalid choice.
)
pause
goto menu

:train
echo.YOLOv11 model training...
echo (Recommended GPU for faster training)
echo.
echo Configuration options:
echo - Model size: n(nano), s(small), m(medium), l(large), x(xlarge)
echo - Edit config.yaml to customize
echo.
python scripts\train_yolov11minutes depending on dataset size)
python scripts\train_model.py
pauseYOLOv11 model...
python scripts\evaluate_yolov11.py
pause
goto menu

:inference
echo.
set /p image="Enter path to image: "
if not exist "%image%" (
    echo Image not found!
    pause
    goto menu
)

set /p model="Enter path to model (or press Enter for best.pt): "
if "%model%"=="" (
    set "model=runs/classify/stain_detection_yolov11/weights/best.pt"
)

if not exist "%model%" (
    echo Model not found: %model%
    pause
    goto menu
)

python scripts\inference_yolov11.py --model "%model%" --image "%image%"
pause
goto menu

:bocs
echo.
echo Opening YOLOv11 README...
start notepad README_YOLOV11.md
pause
goto menu

:end
echo.
echo Training with YOLOv11 - Next Steps:
echo 1. Organize images in datasets/raw/ (by stain type)
echo 2. Run: python scripts/prepare_dataset.py --format directory
echo 3. Run: python scripts/train_yolov11.py
echo 4. Run: python scripts/evaluate_yolov11.py
echo 5. Run: python scripts/inference_yolov11.py
echo.
echo For more information, see README_YOLOV11.md
set /p model="Enter path to model (or press Enter for best.pt): "
if "%model%"=="" (
    set "model=runs/classify/stain_detection_yolov11/weights/best.pt"
)

set /p output="Enter output JSON file (or press Enter to skip): "
if "%output%"=="" (
    python scripts\inference_yolov11.py --model "%model%" --batch "%batch_dir%"
) else (
    python scripts\inference_yolov11.py --model "%model%" --batch "%batch_dir%" --output "%output
set /p model="Enter path to model (or press Enter for latest): "
if "%model%"=="" (
    python scripts\inference.py --image "%image%" || echo No model found. Train a model first.
) else (
    python scripts\inference.py --model "%model%" --image "%image%"
)
pause
goto menu

:config
echo.
type config.yaml
pause
goto menu

:dataset
echo.
echo Opening DATASET_SETUP.md...
start notepad DATASET_SETUP.md
pause
goto menu

:end
echo.
echo Goodbye!
echo.
endlocal
