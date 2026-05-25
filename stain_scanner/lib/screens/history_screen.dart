import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/stain_provider.dart';
import '../services/image_analysis_service.dart';
import '../utils/image_renderer.dart';
import 'stain_details_screen.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({Key? key}) : super(key: key);

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  bool _showArchived = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Detection History'),
        elevation: 0,
        backgroundColor: Colors.blue.shade600,
        foregroundColor: Colors.white,
        actions: [
          Consumer<StainProvider>(
            builder: (context, provider, _) {
              final items = _showArchived ? provider.archivedStains : provider.acceptedStains;
              return items.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.delete_sweep),
                      onPressed: () => _showClearDialog(context),
                      tooltip: _showArchived ? 'Clear archived' : 'Clear history',
                    )
                  : const SizedBox();
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                color: Colors.grey.shade100,
              ),
              padding: const EdgeInsets.all(4),
              child: Row(
                children: [
                  Expanded(
                    child: Material(
                      color: Colors.transparent,
                      child: InkWell(
                        onTap: () => setState(() => _showArchived = false),
                        borderRadius: BorderRadius.circular(10),
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(10),
                            color: !_showArchived ? Colors.blue.shade600 : Colors.transparent,
                          ),
                          child: Center(
                            child: Text(
                              'Accepted',
                              style: TextStyle(
                                color: !_showArchived ? Colors.white : Colors.grey.shade700,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Material(
                      color: Colors.transparent,
                      child: InkWell(
                        onTap: () => setState(() => _showArchived = true),
                        borderRadius: BorderRadius.circular(10),
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(10),
                            color: _showArchived ? Colors.blue.shade600 : Colors.transparent,
                          ),
                          child: Center(
                            child: Text(
                              'Archived',
                              style: TextStyle(
                                color: _showArchived ? Colors.white : Colors.grey.shade700,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          Expanded(
            child: Consumer<StainProvider>(
              builder: (context, provider, _) {
                final items = _showArchived ? provider.archivedStains : provider.acceptedStains;
                if (items.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          _showArchived ? Icons.archive : Icons.history,
                          size: 64,
                          color: Colors.grey.shade300,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          _showArchived ? 'No Archived Items' : 'No Detection History',
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            color: Colors.grey.shade600,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          _showArchived ? 'Rejected detections appear here' : 'Accepted detections appear here',
                          style: TextStyle(color: Colors.grey.shade500),
                        ),
                      ],
                    ),
                  );
                }

                return ListView.builder(
                  padding: const EdgeInsets.all(8),
                  itemCount: items.length,
                  itemBuilder: (context, index) {
                    final stain = items[index];
                    final diffColor = ImageAnalysisService.getColorForDifficulty(stain.difficulty);
                    final color = Color(int.parse('0xFF${diffColor.replaceFirst('#', '')}'));
                    return Card(
                      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      child: ListTile(
                        leading: ClipRRect(
                          borderRadius: BorderRadius.circular(12),
                          child: stain.imagePath.isNotEmpty
                              ? SizedBox(
                                  width: 56,
                                  height: 56,
                                  child: buildImageRenderer(stain.imagePath),
                                )
                              : Container(
                                  width: 56,
                                  height: 56,
                                  color: Colors.grey.shade200,
                                  child: Icon(Icons.image, color: Colors.grey.shade500),
                                ),
                        ),
                        title: Text(stain.name, style: const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const SizedBox(height: 4),
                            Text(stain.type, style: const TextStyle(fontSize: 12)),
                            const SizedBox(height: 2),
                            Text(
                              '${stain.difficulty} - ${stain.detectedAt.hour}:${stain.detectedAt.minute.toString().padLeft(2, '0')}',
                              style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
                            ),
                          ],
                        ),
                        trailing: Icon(Icons.chevron_right, color: Colors.grey.shade400),
                        onTap: () => Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => StainDetailsScreen(stain: stain),
                          ),
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  void _showClearDialog(BuildContext context) {
    final provider = context.read<StainProvider>();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(_showArchived ? 'Clear Archive' : 'Clear History'),
        content: Text(_showArchived
            ? 'Are you sure you want to clear all archived items?'
            : 'Are you sure you want to clear all accepted history?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              if (_showArchived) {
                provider.clearArchivedStains();
              } else {
                provider.clearAcceptedStains();
              }
              Navigator.pop(context);
            },
            child: const Text('Clear', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}
