import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  static const String _backendBaseUrl = 'http://10.0.2.2:8000';
  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';
  static const String _usernameKey = 'username';

  Future<Map<String, dynamic>> login(String username, String password) async {
    final url = Uri.parse('$_backendBaseUrl/api/auth/login/');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'password': password}),
    );

    if (response.statusCode == 200) {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      await saveCredentials(body, username);
      return {'success': true, 'body': body};
    }

    return {
      'success': false,
      'message': response.statusCode == 401
          ? 'Invalid username or password.'
          : 'Login failed. Please try again.',
    };
  }

  Future<Map<String, dynamic>> register(
      String username, String email, String password) async {
    final url = Uri.parse('$_backendBaseUrl/api/auth/register/');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode == 201) {
      return {'success': true};
    }

    final responseBody = jsonDecode(response.body) as Map<String, dynamic>;
    String errorMessage = 'Registration failed.';
    
    if (responseBody.containsKey('detail')) {
      errorMessage = responseBody['detail'];
    } else if (responseBody.isNotEmpty) {
      // Get the first error message from the serializer
      final firstKey = responseBody.keys.first;
      final firstError = responseBody[firstKey];
      errorMessage = firstError is List ? firstError[0] : firstError.toString();
    }

    return {
      'success': false,
      'message': errorMessage,
    };
  }

  Future<void> saveCredentials(Map<String, dynamic> body, String username) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_accessTokenKey, body['access'] as String);
    await prefs.setString(_refreshTokenKey, body['refresh'] as String);
    await prefs.setString(_usernameKey, username);
  }

  Future<String?> getAccessToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_accessTokenKey);
  }

  Future<String?> getUsername() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_usernameKey);
  }

  Future<void> clearCredentials() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_accessTokenKey);
    await prefs.remove(_refreshTokenKey);
    await prefs.remove(_usernameKey);
  }
}
