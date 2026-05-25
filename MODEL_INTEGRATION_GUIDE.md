# Stain Detection Model Integration Guide

## Current Status
✅ **Training Complete**: YOLOv8m model trained on 900 images (300 each: Cooking Oil, Mud, Ballpen Ink)
✅ **Model Copied**: Trained model located at `stain_scanner/assets/models/stain_detector.pt`
✅ **Flutter App Updated**: ImageAnalysisService configured for trained stain types

## Model Details
- **Architecture**: YOLOv8 Medium (YOLOv8m)
- **Framework**: PyTorch
- **Training Data**: 900 images (80% train, 20% val split)
- **Classes**: 3 (oil=0, mud=1, ink=2)
- **Training Results**: `ml_training/runs/detect/stain_detection/stain_detection_yolov11-5/`
- **Best Model**: `weights/best.pt`

## Integration Steps for Mobile Deployment

### Step 1: Convert PyTorch to TFLite (Required for Mobile)
The current `stain_detector.pt` is a PyTorch model. For mobile deployment, convert to TensorFlow Lite:

```bash
cd ml_training
python -m pip install torch torchvision onnx onnx-simplifier tf2onnx tensorflow

# Convert PyTorch to ONNX
python -c "
import torch
from ultralytics import YOLO
model = YOLO('runs/detect/stain_detection/stain_detection_yolov11-5/weights/best.pt')
model.export(format='tflite', imgsz=640)
"

# This generates: best.tflite
# Copy to Flutter: copy best.tflite stain_scanner/assets/models/
```

### Step 2: Add TFLite Dependencies to Flutter
Update `stain_scanner/pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # Existing dependencies...
  
  # ML Model inference
  tflite_flutter: ^0.10.0
  tflite_flutter_helper: ^0.0.5
```

Then run: `flutter pub get`

### Step 3: Implement Inference in Dart
Update `stain_scanner/lib/services/image_analysis_service.dart`:

```dart
import 'package:tflite_flutter/tflite_flutter.dart';

class ImageAnalysisService {
  static Interpreter? _interpreter;
  static const String modelPath = 'assets/models/stain_detector.tflite';
  
  static Future<void> initializeModel() async {
    try {
      _interpreter = await Interpreter.fromAsset(modelPath);
      print('✓ Model loaded successfully');
    } catch (e) {
      print('✗ Failed to load model: $e');
    }
  }
  
  static Future<String?> analyzeImage(Uint8List imageBytes) async {
    if (_interpreter == null) {
      await initializeModel();
    }
    
    // Preprocess image
    var imageInput = prepareImage(imageBytes);
    
    // Run inference
    var output = List.filled(1 * 84 * 8400, 0.0).reshape([1, 84, 8400]);
    _interpreter!.run([imageInput], output);
    
    // Post-process and extract detections
    return postProcessDetections(output);
  }
  
  static String? postProcessDetections(List<dynamic> output) {
    // Parse YOLO detections and return stain type
    // Return highest confidence detection from: oil, mud, ink
    const stainNames = ['oil', 'mud', 'ink'];
    // ... detection parsing logic
    return 'oil'; // Example
  }
}
```

### Step 4: Call Model on App Startup
Update `stain_scanner/lib/main.dart`:

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await ImageAnalysisService.initializeModel();
  runApp(const MyApp());
}
```

## Current Model Performance
Check `ml_training/runs/detect/stain_detection/stain_detection_yolov11-5/results.csv` for:
- Training/validation losses
- Precision & Recall metrics
- mAP50 & mAP50-95 scores

## Files Modified
- ✅ `stain_scanner/pubspec.yaml` - Added model asset
- ✅ `stain_scanner/lib/services/image_analysis_service.dart` - Updated for trained model
- ✅ `stain_scanner/assets/models/stain_detector.pt` - Trained model added
- ⏳ `stain_scanner/lib/services/image_analysis_service.dart` - Needs TFLite inference implementation

## Next Steps
1. Convert `best.pt` to `best.tflite`
2. Add TFLite dependencies to pubspec.yaml
3. Implement actual inference in ImageAnalysisService
4. Test on device/emulator
5. Optimize model size if needed

## Model Training Logs
- Training started: Epoch 1-100 on 900 images
- Current checkpoint: `stain_detection_yolov11-5`
- All training data: Cooking Oil (300), Mud (300), Ballpen Ink (300)
- Batch size: 8, GPU: RTX 4050
