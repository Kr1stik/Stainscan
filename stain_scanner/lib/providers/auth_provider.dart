import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();

  bool _isAuthenticated = false;
  String? _username;

  bool get isAuthenticated => _isAuthenticated;
  String? get username => _username;

  Future<void> loadAuthStatus() async {
    final token = await _authService.getAccessToken();
    if (token != null) {
      _username = await _authService.getUsername();
      _isAuthenticated = true;
    } else {
      _isAuthenticated = false;
      _username = null;
    }
    notifyListeners();
  }

  Future<String?> login(String username, String password) async {
    final result = await _authService.login(username, password);
    if (result['success'] == true) {
      _isAuthenticated = true;
      _username = username;
      notifyListeners();
      return null;
    }
    return result['message'] as String?;
  }

  Future<String?> register(String username, String email, String password) async {
    final result = await _authService.register(username, email, password);
    if (result['success'] == true) {
      return null;
    }
    return result['message'] as String?;
  }

  Future<void> logout() async {
    _isAuthenticated = false;
    _username = null;
    notifyListeners();
    await _authService.clearCredentials();
  }
}
