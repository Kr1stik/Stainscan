import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/image_analysis_result.dart';
import '../models/stain.dart';
import '../providers/stain_provider.dart';
import '../utils/image_renderer.dart';
import 'stain_details_screen.dart';

class AnalysisResultScreen extends StatelessWidget {
  final Stain stain;
  final String imagePath;
  final List<Detection> detections;
  final double imageWidth;
  final double imageHeight;

  const AnalysisResultScreen({
    Key? key,
    required this.stain,
    required this.imagePath,
    required this.detections,
    required this.imageWidth,
    required this.imageHeight,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: () async {
        Navigator.pop(context);
        return false;
      },
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Analysis Result'),
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_ios),
            onPressed: () => Navigator.pop(context),
          ),
          backgroundColor: Colors.blue.shade600,
          foregroundColor: Colors.white,
        ),
        body: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Image Display with detection overlay
              Container(
                height: 280,
                color: Colors.grey.shade200,
                child: Stack(
                  children: [
                    Positioned.fill(child: buildImageRenderer(imagePath)),
                    _buildDetectionOverlay(),
                  ],
                ),
              ),
              
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Detection Result Card
                    Card(
                      elevation: 2,
                      shadowColor: Colors.blue.withOpacity(0.3),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      child: Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [Colors.blue.shade50, Colors.blue.shade100],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Detected Stain Type',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey,
                                fontWeight: FontWeight.w500,
                                letterSpacing: 0.5,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              stain.name,
                              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: Colors.blue.shade700,
                              ),
                            ),
                            const SizedBox(height: 12),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                _buildResultChip(
                                  label: 'Type',
                                  value: stain.type,
                                  icon: Icons.category,
                                ),
                                _buildResultChip(
                                  label: 'Difficulty',
                                  value: stain.difficulty,
                                  icon: Icons.trending_up,
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 20),
                    
                    // Quick Info
                    Text(
                      'Quick Summary',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.amber.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.amber.shade200),
                      ),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(Icons.info, color: Colors.amber.shade700, size: 20),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              stain.description,
                              style: TextStyle(
                                fontSize: 13,
                                color: Colors.amber.shade900,
                                height: 1.4,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    const SizedBox(height: 20),
                    
                    // Accept / Reject Buttons
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () {
                              context.read<StainProvider>().addAcceptedStain(stain);
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Detection accepted and saved to history')),
                              );
                              Navigator.popUntil(context, (route) => route.isFirst);
                            },
                            icon: const Icon(Icons.check_circle),
                            label: const Text('Accept'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.green.shade600,
                              minimumSize: const Size.fromHeight(48),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () {
                              context.read<StainProvider>().addArchivedStain(stain);
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Detection rejected and moved to archive')),
                              );
                              Navigator.popUntil(context, (route) => route.isFirst);
                            },
                            icon: const Icon(Icons.archive),
                            label: const Text('Reject'),
                            style: OutlinedButton.styleFrom(
                              minimumSize: const Size.fromHeight(48),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    
                    ElevatedButton.icon(
                      onPressed: () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => StainDetailsScreen(stain: stain),
                        ),
                      ),
                      icon: const Icon(Icons.description),
                      label: const Text('View Full Details'),
                      style: ElevatedButton.styleFrom(
                        minimumSize: const Size.fromHeight(48),
                      ),
                    ),
                    
                    const SizedBox(height: 12),
                    
                    OutlinedButton.icon(
                      onPressed: () => Navigator.popUntil(context, (route) => route.isFirst),
                      icon: const Icon(Icons.home),
                      label: const Text('Back to Home'),
                      style: OutlinedButton.styleFrom(
                        minimumSize: const Size.fromHeight(48),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildResultChip({
    required String label,
    required String value,
    required IconData icon,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Icon(icon, size: 16, color: Colors.blue.shade700),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(fontSize: 10, color: Colors.grey),
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.bold,
              color: Colors.blue.shade700,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetectionOverlay() {
    final bool isUnknown = stain.type.toLowerCase() == 'unknown';
    Color badgeColor;
    String labelText;
    String messageText = '';

    if (isUnknown) {
      badgeColor = Colors.redAccent.shade700;
      labelText = 'Not clothing or fabric';
      messageText = 'Please upload a photo of a fabric or garment stain for better results.';
    } else {
      switch (stain.type.toLowerCase()) {
        case 'cooking oil':
        case 'oil':
          badgeColor = Colors.amber.shade700;
          labelText = 'Cooking oil stain';
          break;
        case 'mud':
        case 'mud oil':
          badgeColor = Colors.brown.shade700;
          labelText = 'Mud stain';
          break;
        case 'ink':
        case 'ballpen ink':
          badgeColor = Colors.blue.shade700;
          labelText = 'Ink stain';
          break;
        case 'cotton':
          badgeColor = Colors.indigo.shade700;
          labelText = 'Cotton fabric detected';
          messageText = 'The image appears to show cotton fabric. Stain type could not be identified with the current model.';
          break;
        default:
          badgeColor = Colors.green.shade700;
          labelText = '${stain.type} stain';
          messageText = 'Detected stain type is a good match for fabric stain removal guidance.';
      }
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        return Stack(
          children: [
            if (detections.isNotEmpty)
              ...detections.map((detection) {
                final normalized = detection.normalized(
                  imageWidth: imageWidth,
                  imageHeight: imageHeight,
                );
                final left = normalized.x1.clamp(0.0, 1.0) * constraints.maxWidth;
                final top = normalized.y1.clamp(0.0, 1.0) * constraints.maxHeight;
                final width = (normalized.x2 - normalized.x1).clamp(0.0, 1.0) * constraints.maxWidth;
                final height = (normalized.y2 - normalized.y1).clamp(0.0, 1.0) * constraints.maxHeight;
                return Positioned(
                  left: left,
                  top: top,
                  width: width.clamp(0.0, constraints.maxWidth - left),
                  height: height.clamp(0.0, constraints.maxHeight - top),
                  child: Container(
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: _boxColorForType(detection.type),
                        width: 3,
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Align(
                      alignment: Alignment.topLeft,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: _boxColorForType(detection.type).withOpacity(0.85),
                          borderRadius: const BorderRadius.only(
                            topLeft: Radius.circular(10),
                            bottomRight: Radius.circular(10),
                          ),
                        ),
                        child: Text(
                          '${detection.type} ${(detection.confidence * 100).toStringAsFixed(0)}%',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  ),
                );
              }),
            Positioned(
              left: 16,
              right: 16,
              top: 16,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      color: badgeColor.withOpacity(0.95),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      labelText,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.55),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      messageText,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        );
      },
    );
  }

  Color _boxColorForType(String type) {
    switch (type.toLowerCase()) {
      case 'ink':
        return Colors.blue.shade400;
      case 'mud':
        return Colors.brown.shade400;
      case 'cooking_oil':
      case 'cooking oil':
      case 'oil':
        return Colors.amber.shade600;
      default:
        return Colors.green.shade400;
    }
  }
}
