import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/image_analysis_service.dart';
import 'analysis_result_screen.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({Key? key}) : super(key: key);

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  bool _isAnalyzing = false;
  final ImagePicker _imagePicker = ImagePicker();

  Future<void> _pickGalleryImage() async {
    final image = await _imagePicker.pickImage(source: ImageSource.gallery);
    if (image == null) return;

    setState(() => _isAnalyzing = true);

    try {
      final analysisFuture = ImageAnalysisService.analyzeImage(
        kIsWeb ? image : image.path,
      );
      // Reduced loading delay for faster response (500ms min)
      final minLoading = Future.delayed(const Duration(milliseconds: 500));

      final analysisResult = await Future.wait([
        analysisFuture,
        minLoading,
      ]).then((results) => results[0] as dynamic);

      final detectedStain = ImageAnalysisService.createDetectedStain(
        analysisResult?.stainType ?? 'unknown',
        image.path,
      );

      if (!mounted) return;
      setState(() => _isAnalyzing = false);

      await Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => AnalysisResultScreen(
            stain: detectedStain,
            imagePath: image.path,
            detections: analysisResult?.detections ?? [],
            imageWidth: analysisResult?.imageWidth ?? 0.0,
            imageHeight: analysisResult?.imageHeight ?? 0.0,
          ),
        ),
      );
    } catch (e) {
      if (mounted) {
        setState(() => _isAnalyzing = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Upload Stain Photo'),
        elevation: 0,
        backgroundColor: Colors.blue.shade600,
        foregroundColor: Colors.white,
      ),
      body: Stack(
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.photo_library,
                    size: 84,
                    color: Colors.blue.shade400,
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'Upload fabric or clothing stain photos only',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'The app detects mud, ink, and cooking oil stains. It also checks whether the image contains cotton fabric or clothing before returning results.',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.grey.shade700,
                        ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 36),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _isAnalyzing ? null : _pickGalleryImage,
                      icon: const Icon(Icons.photo_library),
                      label: const Padding(
                        padding: EdgeInsets.symmetric(vertical: 16),
                        child: Text('Upload from Gallery', style: TextStyle(fontSize: 16)),
                      ),
                      style: ElevatedButton.styleFrom(
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (_isAnalyzing)
            Positioned.fill(
              child: Container(
                color: Colors.black.withOpacity(0.45),
                child: Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const CircularProgressIndicator(),
                      const SizedBox(height: 18),
                      Text(
                        'Analyzing the stain…',
                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                              color: Colors.white,
                            ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
