import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:image/image.dart' as img;
import 'package:image_picker/image_picker.dart';
import '../models/image_analysis_result.dart';
import '../models/stain.dart';

class ImageAnalysisService {
  static const List<String> trainedStainTypes = [
    'oil',
    'mud',
    'ink',
  ];

  static const String apiBaseUrl = 'http://localhost:5000';

  static Future<ImageAnalysisResult?> analyzeImage(Object imageSource) async {
    try {
      if (imageSource is! XFile) {
        print('⚠️ Web analyzeImage received unsupported source: $imageSource');
        return _fallbackResult('unknown');
      }
      final imageFile = imageSource;
      final bytes = await imageFile.readAsBytes();
      final base64Image = base64Encode(bytes);

      final response = await http
          .post(
            Uri.parse('$apiBaseUrl/analyze'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'base64': base64Image}),
          )
          .timeout(
            const Duration(seconds: 15),
            onTimeout: () {
              throw TimeoutException('Detection server took too long to respond');
            },
          );

      if (response.statusCode == 200 || response.statusCode == 500) {
        // Accept both 200 and 500 responses - server returns results even on error
        try {
          final result = jsonDecode(response.body);
          final dimensions = _getImageDimensions(bytes);
          return ImageAnalysisResult.fromJson(
            result,
            imageWidth: dimensions['width'] ?? 0.0,
            imageHeight: dimensions['height'] ?? 0.0,
          );
        } catch (e) {
          print('⚠️ Error parsing API response: $e');
          return _fallbackResult('unknown');
        }
      }

      print('⚠️ API error: ${response.statusCode}');
      return _fallbackResult('unknown');
    } catch (e) {
      print('⚠️ Web API detection error: $e');
      return _fallbackResult('unknown');
    }
  }

  static ImageAnalysisResult _fallbackResult(String stainType) {
    return ImageAnalysisResult(
      stainType: stainType,
      fabricType: 'unknown',
      fabricConfidence: 0.0,
      detections: [],
      imageWidth: 0.0,
      imageHeight: 0.0,
    );
  }

  static Map<String, double> _getImageDimensions(Uint8List bytes) {
    try {
      final image = img.decodeImage(bytes);
      if (image != null) {
        return {'width': image.width.toDouble(), 'height': image.height.toDouble()};
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
        description: 'Unable to identify stain type',
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
