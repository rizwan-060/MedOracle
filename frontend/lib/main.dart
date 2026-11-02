import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'core/routing/app_router.dart';
import 'core/theme/app_theme.dart';

/// MedOracle - agentic clinical decision-support front end.
///
/// The intake flow is the first surface; it is routed with `go_router`
/// (see `core/routing/app_router.dart`).
void main() {
  runApp(const ProviderScope(child: MedOracleApp()));
}

/// Root application widget.
class MedOracleApp extends StatefulWidget {
  const MedOracleApp({super.key});

  @override
  State<MedOracleApp> createState() => _MedOracleAppState();
}

class _MedOracleAppState extends State<MedOracleApp> {
  late final GoRouter _router = createAppRouter();

  @override
  void dispose() {
    _router.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'MedOracle',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      routerConfig: _router,
    );
  }
}
