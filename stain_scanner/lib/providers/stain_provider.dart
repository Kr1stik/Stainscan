import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../models/stain.dart';

class StainProvider extends ChangeNotifier {
  List<Stain> _acceptedStains = [];
  List<Stain> _archivedStains = [];
  
  List<Stain> get acceptedStains => _acceptedStains;
  List<Stain> get archivedStains => _archivedStains;
  
  StainProvider() {
    _loadStains();
  }
  
  Future<void> _loadStains() async {
    final prefs = await SharedPreferences.getInstance();
    final acceptedList = prefs.getStringList('accepted_stains') ?? [];
    final archivedList = prefs.getStringList('archived_stains') ?? [];

    _acceptedStains = acceptedList
        .map((stainJson) => Stain.fromJson(jsonDecode(stainJson)))
        .toList();

    _archivedStains = archivedList
        .map((stainJson) => Stain.fromJson(jsonDecode(stainJson)))
        .toList();

    notifyListeners();
  }
  
  Future<void> addAcceptedStain(Stain stain) async {
    final acceptedStain = Stain(
      id: stain.id,
      name: stain.name,
      type: stain.type,
      description: stain.description,
      removalMethods: stain.removalMethods,
      materials: stain.materials,
      difficulty: stain.difficulty,
      imagePath: stain.imagePath,
      detectedAt: stain.detectedAt,
      status: 'accepted',
    );
    _acceptedStains.insert(0, acceptedStain);
    await _saveAcceptedStains();
    notifyListeners();
  }

  Future<void> addArchivedStain(Stain stain) async {
    final archivedStain = Stain(
      id: stain.id,
      name: stain.name,
      type: stain.type,
      description: stain.description,
      removalMethods: stain.removalMethods,
      materials: stain.materials,
      difficulty: stain.difficulty,
      imagePath: stain.imagePath,
      detectedAt: stain.detectedAt,
      status: 'archived',
    );
    _archivedStains.insert(0, archivedStain);
    await _saveArchivedStains();
    notifyListeners();
  }

  Future<void> removeAcceptedStain(String id) async {
    _acceptedStains.removeWhere((stain) => stain.id == id);
    await _saveAcceptedStains();
    notifyListeners();
  }

  Future<void> removeArchivedStain(String id) async {
    _archivedStains.removeWhere((stain) => stain.id == id);
    await _saveArchivedStains();
    notifyListeners();
  }

  Future<void> clearAcceptedStains() async {
    _acceptedStains.clear();
    await _saveAcceptedStains();
    notifyListeners();
  }

  Future<void> clearArchivedStains() async {
    _archivedStains.clear();
    await _saveArchivedStains();
    notifyListeners();
  }
  
  Future<void> _saveAcceptedStains() async {
    final prefs = await SharedPreferences.getInstance();
    final stainsList = _acceptedStains
        .map((stain) => jsonEncode(stain.toJson()))
        .toList();
    await prefs.setStringList('accepted_stains', stainsList);
  }

  Future<void> _saveArchivedStains() async {
    final prefs = await SharedPreferences.getInstance();
    final stainsList = _archivedStains
        .map((stain) => jsonEncode(stain.toJson()))
        .toList();
    await prefs.setStringList('archived_stains', stainsList);
  }
}
