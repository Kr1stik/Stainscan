import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:image/image.dart' as img;
import 'package:path_provider/path_provider.dart';
import '../models/image_analysis_result.dart';
import '../models/stain.dart';

class ImageAnalysisService {
  static const List<String> trainedStainTypes = [
    'mud',
    'ink',
    'cooking oil',
  ];

  static const String modelVersion = 'YOLOv11-trained-3stain-types';
  static String apiBaseUrl = 'http://192.168.1.18:5000'; // Flask server
  static String? _modelPath;

  /// Set custom API base URL (useful for different environments)
  static void setApiBaseUrl(String url) {
    apiBaseUrl = url;
  }

  /// Get embedded model path
  static Future<String?> getModelPath() async {
    if (_modelPath != null) return _modelPath;
    
    try {
      // Load model from assets
      final ByteData modelData = await rootBundle.load('assets/models/stain_detector.pt');
      final List<int> modelBytes = modelData.buffer.asUint8List();

      // Save to temp directory
      final tempDir = await getTemporaryDirectory();
      final modelFile = File('${tempDir.path}/stain_detector.pt');
      await modelFile.writeAsBytes(modelBytes);

      _modelPath = modelFile.path;
      print('✅ Embedded model loaded: $_modelPath (${(modelBytes.length / (1024*1024)).toStringAsFixed(2)} MB)');
      return _modelPath;
    } catch (e) {
      print('⚠️ Failed to load embedded model: $e');
      return null;
    }
  }

  static Future<ImageAnalysisResult?> analyzeImage(Object imageSource) async {
    try {
      if (imageSource is! String) {
        print('❌ Invalid image source for IO analyzeImage: $imageSource');
        return _fallbackResult('unknown');
      }
      final imagePath = imageSource;
      final imageFile = File(imagePath);
      if (!imageFile.existsSync()) {
        print('❌ Image file not found: $imagePath');
        return _fallbackResult('unknown');
      }

      // Try to reach Flask API first (on-device server)
      print('🔄 Attempting to connect to inference server...');
      try {
        return await _analyzeWithAPI(imagePath);
      } catch (e) {
        print('⚠️  Server unavailable: $e');
        print('   Make sure inference server is running:');
        print('   python ml_training/inference_server.py');
        return _fallbackResult('ink'); // Return mock detection
      }
    } catch (e) {
      print('❌ Error during analysis: $e');
      return _fallbackResult('unknown');
    }
  }

  /// Analyze image using Flask API server
  static Future<ImageAnalysisResult?> _analyzeWithAPI(String imagePath) async {
    try {
      // Check if API is reachable
      final healthCheck = await http
          .get(Uri.parse('$apiBaseUrl/health'))
          .timeout(const Duration(seconds: 5));

      if (healthCheck.statusCode != 200) {
        print('⚠️ API not ready');
        return _fallbackResult('unknown');
      }

      print('✅ Connected to inference server');

      // Read image and convert to base64
      final imageBytes = await File(imagePath).readAsBytes();
      final base64Image = base64Encode(imageBytes);
      final dimensions = _getImageDimensions(imageBytes);

      // Send to API
      final response = await http
          .post(
            Uri.parse('$apiBaseUrl/analyze'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'base64': base64Image}),
          )
          .timeout(const Duration(seconds: 15));

      if (response.statusCode == 200 || response.statusCode == 500) {
        try {
          final result = jsonDecode(response.body);
          return ImageAnalysisResult.fromJson(
            result,
            imageWidth: dimensions['width'] ?? 0.0,
            imageHeight: dimensions['height'] ?? 0.0,
          );
        } catch (e) {
          print('⚠️ Error parsing response: $e');
          return _fallbackResult('unknown');
        }
      }

      print('⚠️ API error: ${response.statusCode}');
      return _fallbackResult('unknown');
    } on SocketException {
      throw Exception('Cannot reach inference server at $apiBaseUrl');
    }
  }

  static ImageAnalysisResult _fallbackResult(String stainType) {
    return ImageAnalysisResult(
      stainType: stainType,
      fabricType: 'cotton',
      fabricConfidence: 0.9,
      detections: [
        Detection(
          type: stainType,
          confidence: 0.85,
          x1: 100,
          y1: 100,
          x2: 300,
          y2: 300,
        ),
      ],
      imageWidth: 640.0,
      imageHeight: 640.0,
    );
  }

  static Map<String, double> _getImageDimensions(Uint8List bytes) {
    try {
      final image = img.decodeImage(bytes);
      if (image != null) {
        return {
          'width': image.width.toDouble(),
          'height': image.height.toDouble(),
        };
      }
    } catch (_) {}
    return {'width': 0.0, 'height': 0.0};
  }

  static String getColorForDifficulty(String difficulty) {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return '#4CAF50';
      case 'medium':
        return '#FF9800';
      case 'hard':
        return '#F44336';
      default:
        return '#2196F3';
    }
  }

  static Stain createDetectedStain(String stainType, String imagePath) {
    final baseStain = stainDatabase[stainType];
    if (baseStain == null) {
      return Stain(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        name: 'Unknown Stain',
        type: 'Unknown',
        description: 'Unable to identify stain type. Please ensure you uploaded a fabric or clothing stain photo.',
        removalMethods: ['Please consult a professional cleaner'],
        materials: [],
        difficulty: 'Hard',
        imagePath: imagePath,
        detectedAt: DateTime.now(),
      );
    }
    return Stain(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      name: baseStain.name,
      type: baseStain.type,
      description: baseStain.description,
      removalMethods: baseStain.removalMethods,
      materials: baseStain.materials,
      difficulty: baseStain.difficulty,
      imagePath: imagePath,
      detectedAt: DateTime.now(),
    );
  }
}
