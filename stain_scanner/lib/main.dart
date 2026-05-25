import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'providers/stain_provider.dart';
import 'providers/auth_provider.dart';
import 'screens/home_screen.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => StainProvider()),
        ChangeNotifierProvider(create: (_) => AuthProvider()),
      ],
      child: MaterialApp(
        title: 'Stain Scanner',
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.blue,
            brightness: Brightness.light,
          ),
          textTheme: GoogleFonts.poppinsTextTheme(),
          appBarTheme: AppBarTheme(
            backgroundColor: Colors.blue.shade600,
            foregroundColor: Colors.white,
            elevation: 0,
            centerTitle: false,
          ),
        ),
        home: const AuthDeciderScreen(),
      ),
    );
  }
}

class AuthDeciderScreen extends StatefulWidget {
  const AuthDeciderScreen({super.key});

  @override
  State<AuthDeciderScreen> createState() => _AuthDeciderScreenState();
}

class _AuthDeciderScreenState extends State<AuthDeciderScreen> {
  bool _isLoading = true;
  String? _deepLinkUsername;
  StreamSubscription<Uri?>? _linkSubscription;

  @override
  void initState() {
    super.initState();
    _loadAuth();
    if (!kIsWeb) {
      _initDeepLinks();
    }
  }

  @override
  void dispose() {
    _linkSubscription?.cancel();
    super.dispose();
  }

  Future<void> _loadAuth() async {
    // Skip authentication for web
    if (!mounted) return;
    setState(() {
      _isLoading = false;
    });
  }

  Future<void> _initDeepLinks() async {
    if (kIsWeb) return; // Skip on web platform
    
    try {
      // Deep links only work on mobile platforms
      // final initialUri = await getInitialUri();
      // _processDeepLink(initialUri);
    } catch (_) {
      // ignore invalid initial URI
    }

    // _linkSubscription = uriLinkStream.listen((uri) {
    //   _processDeepLink(uri);
    // }, onError: (_) {
    //   // ignore stream errors
    // });
  }

  void _processDeepLink(Uri? uri) {
    if (uri == null) return;
    if (uri.scheme == 'stainapp' && uri.host == 'login') {
      final username = uri.queryParameters['username'];
      if (username != null && username.isNotEmpty) {
        setState(() {
          _deepLinkUsername = Uri.decodeComponent(username);
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // Skip loading check for web
    if (_isLoading && !kIsWeb) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    // Go directly to HomeScreen (skip login)
    return const HomeScreen();
  }
}
