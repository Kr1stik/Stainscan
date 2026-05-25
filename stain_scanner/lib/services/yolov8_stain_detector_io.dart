import 'dart:typed_data';
import 'dart:io';
import 'package:image/image.dart' as img;
import 'package:tflite_flutter/tflite_flutter.dart';

class YOLOv8StainDetector {
  static const String modelPath = 'assets/models/stain_detector.tflite';
  static const int inputSize = 640;
  static const double confidenceThreshold = 0.3; // Lowered for better detection
  static const double iouThreshold = 0.45;

  static Interpreter? _interpreter;
  static bool _isInitialized = false;

  static const List<String> stainClasses = [
    'oil',
    'mud',
    'ink',
  ];

  static Future<String?> detectStainType(Uint8List imageBytes) async {
    try {
      if (!_isInitialized) {
        await _initializeInterpreter();
      }
      if (_interpreter == null) {
        print('❌ Interpreter not loaded - returning null');
        return null;
      }

      final image = img.decodeImage(imageBytes);
      if (image == null) {
        print('❌ Failed to decode image');
        return null;
      }

      final resized = img.copyResize(image,
          width: inputSize,
          height: inputSize,
          interpolation: img.Interpolation.linear);
      final input = _imageToInput(resized);

      final outputTensors = _interpreter!.getOutputTensors();
      Map<int, Object> outputs = {};
      int outputIndex = 0;
      for (var tensor in outputTensors) {
        final shape = tensor.shape;
        if (shape.length == 3 && shape[0] == 1 && shape[1] == 84 && shape[2] == 8400) {
          final buffer = List.generate(
            shape[0],
            (_) => List.generate(
              shape[1],
              (_) => List.filled(shape[2], 0.0),
            ),
          );
          outputs[outputIndex] = buffer;
        } else {
          final totalSize = shape.fold<int>(1, (a, b) => a * b);
          final buffer = List.filled(totalSize, 0.0);
          outputs[outputIndex] = buffer;
        }
        outputIndex++;
      }

      _interpreter!.runForMultipleInputs([input], outputs);
      final firstOutput = outputs[0];
      final detections = _parseDetections(firstOutput);
      if (detections.isEmpty) {
        return null;
      }
      final bestDetection = detections.reduce((a, b) =>
          a['confidence'] > b['confidence'] ? a : b);
      return stainClasses[bestDetection['class_id']];
    } catch (e) {
      print('❌ Detection error: $e');
      return null;
    }
  }

  static Future<void> _initializeInterpreter() async {
    try {
      print('📦 Loading TFLite model from: $modelPath');
      _interpreter = await Interpreter.fromAsset(modelPath);
      _isInitialized = true;
      print('✅ Model loaded successfully');
    } catch (e) {
      print('❌ Failed to load model: $e');
      _isInitialized = true;
    }
  }

  static List<List<List<List<double>>>> _imageToInput(img.Image image) {
    final input = List.generate(1, (_) =>
        List.generate(inputSize, (_) =>
            List.generate(inputSize, (_) =>
                List.generate(3, (_) => 0.0))));
    for (int y = 0; y < inputSize; y++) {
      for (int x = 0; x < inputSize; x++) {
        final pixel = image.getPixelSafe(x, y);
        input[0][y][x][0] = pixel.r.toDouble() / 255.0;
        input[0][y][x][1] = pixel.g.toDouble() / 255.0;
        input[0][y][x][2] = pixel.b.toDouble() / 255.0;
      }
    }
    return input;
  }

  static List<Map<String, dynamic>> _parseDetections(dynamic output) {
    final detections = <Map<String, dynamic>>[];
    try {
      List<List<List<double>>>? predictions;
      if (output is List<List<List<double>>>) {
        predictions = output;
      } else if (output is List<List<double>>) {
        predictions = [output];
      } else if (output is List<double>) {
        if (output.length == 84 * 8400) {
          predictions = [];
          List<List<double>> batch = [];
          for (int i = 0; i < 84; i++) {
            List<double> row = [];
            for (int j = 0; j < 8400; j++) {
              row.add(output[i * 8400 + j]);
            }
            batch.add(row);
          }
          predictions.add(batch);
        }
      }
      if (predictions == null || predictions.isEmpty) {
        return detections;
      }
      final pred = predictions[0];
      final numAnchors = pred[0].length;
      for (int i = 0; i < numAnchors; i++) {
        final conf = pred[4][i];
        if (conf < confidenceThreshold) continue;
        double maxClassConf = 0.0;
        int classId = 0;
        for (int c = 0; c < stainClasses.length && (5 + c) < pred.length; c++) {
          final classConf = pred[5 + c][i] * conf;
          if (classConf > maxClassConf) {
            maxClassConf = classConf;
            classId = c;
          }
        }
        if (maxClassConf > confidenceThreshold) {
          final x = pred[0][i];
          final y = pred[1][i];
          final w = pred[2][i];
          final h = pred[3][i];
          detections.add({
            'class_id': classId,
            'class_name': stainClasses[classId],
            'confidence': maxClassConf,
            'x': x,
            'y': y,
            'width': w,
            'height': h,
          });
        }
      }
      return _applyNMS(detections, iouThreshold);
    } catch (e) {
      print('⚠️  Error parsing detections: $e');
      return detections;
    }
  }

  static List<Map<String, dynamic>> _applyNMS(
      List<Map<String, dynamic>> detections, double iouThreshold) {
    if (detections.isEmpty) return detections;
    detections.sort((a, b) =>
        (b['confidence'] as double).compareTo(a['confidence'] as double));
    final result = <Map<String, dynamic>>[];
    final used = List.filled(detections.length, false);
    for (int i = 0; i < detections.length; i++) {
      if (used[i]) continue;
      result.add(detections[i]);
      for (int j = i + 1; j < detections.length; j++) {
        if (used[j]) continue;
        final iou = _calculateIOU(detections[i], detections[j]);
        if (iou > iouThreshold) {
          used[j] = true;
        }
      }
    }
    return result;
  }

  static double _calculateIOU(Map<String, dynamic> box1,
      Map<String, dynamic> box2) {
    final x1 = box1['x'] as double;
    final y1 = box1['y'] as double;
    final w1 = box1['width'] as double;
    final h1 = box1['height'] as double;
    final x2 = box2['x'] as double;
    final y2 = box2['y'] as double;
    final w2 = box2['width'] as double;
    final h2 = box2['height'] as double;
    final xLeft = [x1 - w1 / 2, x2 - w2 / 2].reduce((a, b) => a > b ? a : b);
    final xRight = [x1 + w1 / 2, x2 + w2 / 2].reduce((a, b) => a < b ? a : b);
    final yTop = [y1 - h1 / 2, y2 - h2 / 2].reduce((a, b) => a > b ? a : b);
    final yBottom = [y1 + h1 / 2, y2 + h2 / 2].reduce((a, b) => a < b ? a : b);
    if (xRight < xLeft || yBottom < yTop) return 0.0;
    final intersection = (xRight - xLeft) * (yBottom - yTop);
    final union = w1 * h1 + w2 * h2 - intersection;
    return intersection / union;
  }
}
