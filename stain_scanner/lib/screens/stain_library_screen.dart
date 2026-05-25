import 'package:flutter/material.dart';
import '../models/stain.dart';
import 'stain_details_screen.dart';

class StainLibraryScreen extends StatefulWidget {
  const StainLibraryScreen({Key? key}) : super(key: key);

  @override
  State<StainLibraryScreen> createState() => _StainLibraryScreenState();
}

class _StainLibraryScreenState extends State<StainLibraryScreen> {
  late List<Stain> _stains;
  late List<Stain> _filteredStains;
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _stains = stainDatabase.values.toList();
    _filteredStains = _stains;
  }

  void _filterStains(String query) {
    setState(() {
      _searchQuery = query;
      _filteredStains = _stains.where((stain) {
        return stain.name.toLowerCase().contains(query.toLowerCase()) ||
            stain.type.toLowerCase().contains(query.toLowerCase()) ||
            stain.description.toLowerCase().contains(query.toLowerCase());
      }).toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Stain Library'),
        elevation: 0,
        backgroundColor: Colors.blue.shade600,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          // Search Bar
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              onChanged: _filterStains,
              decoration: InputDecoration(
                hintText: 'Search stains...',
                prefixIcon: Icon(Icons.search, color: Colors.blue.shade600),
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: Icon(Icons.clear, color: Colors.blue.shade600),
                        onPressed: () => _filterStains(''),
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: Colors.blue.shade200, width: 1),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: Colors.blue.shade200, width: 1),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: Colors.blue.shade600, width: 2),
                ),
                filled: true,
                fillColor: Colors.blue.shade50,
              ),
            ),
          ),
          
          // Stains List
          Expanded(
            child: _filteredStains.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.search_off, size: 48, color: Colors.grey.shade300),
                        const SizedBox(height: 12),
                        Text(
                          'No stains found',
                          style: TextStyle(color: Colors.grey.shade600),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    itemCount: _filteredStains.length,
                    itemBuilder: (context, index) {
                      final stain = _filteredStains[index];
                      return Card(
                        margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                        elevation: 1,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        child: ExpansionTile(
                          title: Text(
                            stain.name,
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          subtitle: Text(stain.type, style: const TextStyle(fontSize: 12)),
                          trailing: Chip(
                            label: Text(stain.difficulty, style: const TextStyle(fontSize: 11)),
                            backgroundColor: _getDifficultyColor(stain.difficulty),
                          ),
                          children: [
                            Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    stain.description,
                                    style: Theme.of(context).textTheme.bodyMedium,
                                  ),
                                  const SizedBox(height: 12),
                                  SizedBox(
                                    width: double.infinity,
                                    child: ElevatedButton(
                                      onPressed: () => Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                          builder: (context) => StainDetailsScreen(
                                            stain: stain,
                                            isFromLibrary: true,
                                          ),
                                        ),
                                      ),
                                      child: const Text('View Details'),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Color _getDifficultyColor(String difficulty) {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return Colors.green.shade100;
      case 'medium':
        return Colors.orange.shade100;
      case 'hard':
        return Colors.red.shade100;
      default:
        return Colors.blue.shade100;
    }
  }
}
