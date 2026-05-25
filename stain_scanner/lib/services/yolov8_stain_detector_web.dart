import 'dart:typed_data';

class YOLOv8StainDetector {
  static const String modelPath = 'assets/models/stain_detector.tflite';
  static const int inputSize = 640;
  static const double confidenceThreshold = 0.3;
  static const double iouThreshold = 0.45;
  static const List<String> stainClasses = ['oil', 'mud', 'ink'];

  static Future<String?> detectStainType(Uint8List imageBytes) async {
    print('⚠️ Web fallback: TFLite inference is not supported on Chrome/web.');
    return null;
  }
}
