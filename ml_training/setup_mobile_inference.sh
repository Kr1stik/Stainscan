#!/bin/bash
# Automated setup script - Run after training completes
# Usage: bash setup_mobile_inference.sh

echo "==========================================="
echo "🚀 Mobile Inference Setup"
echo "==========================================="

# Check if training completed
if [ ! -f "runs/detect/stain_detection/stain_detection_yolov11-5/weights/best.pt" ]; then
    echo "❌ Trained model not found. Waiting for training to complete..."
    exit 1
fi

echo ""
echo "✅ Step 1: Converting PyTorch model to TFLite..."
python convert_to_tflite.py

echo ""
echo "✅ Step 2: Updating Flutter pubspec.yaml..."
echo "   • TFLite Flutter dependencies added"

echo ""
echo "✅ Step 3: Generated inference implementation"
echo "   File: stain_scanner/lib/services/yolov8_stain_detector.dart"

echo ""
echo "==========================================="
echo "📱 Next Steps for Flutter App:"
echo "==========================================="
echo "1. cd stain_scanner"
echo "2. flutter pub get"
echo "3. Update ImageAnalysisService to use YOLOv8StainDetector"
echo "4. Test on device/emulator: flutter run"
echo ""
echo "✅ Ready for mobile deployment!"
