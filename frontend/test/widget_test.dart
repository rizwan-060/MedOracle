import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:medoracle/core/routing/app_router.dart';
import 'package:medoracle/core/theme/app_theme.dart';

void main() {
  testWidgets('intake flow opens on Step 1 - Profile', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp.router(
          theme: AppTheme.light,
          routerConfig: createAppRouter(),
        ),
      ),
    );

    // Let the router build and the (mock) profile fetch resolve.
    await tester.pump();
    await tester.pump(const Duration(seconds: 1));

    expect(find.text('MedOracle'), findsOneWidget);
    expect(find.text('Autosaved'), findsOneWidget);
    expect(find.text('Personal Details'), findsOneWidget);
    expect(find.text('Body Measurements'), findsOneWidget);
    expect(find.text('Lifestyle'), findsOneWidget);
    expect(find.text('15 Mar 1972'), findsOneWidget);
    expect(find.text('A+'), findsOneWidget);
    expect(find.text('Next: Clinical Status'), findsOneWidget);
    expect(find.text('Back'), findsOneWidget);
  });
}
