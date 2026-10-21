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
class MedOracleApp extends ConsumerWidget {
  const MedOracleApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final GoRouter router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'MedOracle',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      routerConfig: router,
    );
  }
}

