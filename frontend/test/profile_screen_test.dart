import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:medoracle/core/theme/app_theme.dart';
import 'package:medoracle/features/profile/screens/profile_screen.dart';

/// Pumps Step 1 on its own (no router) inside a phone-sized surface.
Future<void> _pumpProfile(WidgetTester tester) async {
  tester.view.physicalSize = const Size(390, 900);
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.reset);

  await tester.pumpWidget(
    ProviderScope(
      child: MaterialApp(
        theme: AppTheme.light,
        home: const ProfileScreen(),
      ),
    ),
  );
  // Router-free build + resolve the mock profile fetch.
  await tester.pump();
  await tester.pump(const Duration(seconds: 1));
}

void main() {
  testWidgets('Step 1 renders all three sections and the seeded patient', (
    WidgetTester tester,
  ) async {
    await _pumpProfile(tester);

    expect(find.text('Personal Details'), findsOneWidget);
    expect(find.text('Body Measurements'), findsOneWidget);
    expect(find.text('Lifestyle'), findsOneWidget);

    // Personal Details opens first: date of birth, gender, blood group.
    expect(find.text('Date of Birth'), findsOneWidget);
    expect(find.text('15 Mar 1972'), findsOneWidget);
    expect(find.text('Male'), findsOneWidget);
    expect(find.text('A+'), findsOneWidget);

    // Collapsed sections expose no fields yet.
    expect(find.text('Height'), findsNothing);
    expect(find.text('Smoking Status'), findsNothing);
  });

  testWidgets('expanding a section closes the previously open one', (
    WidgetTester tester,
  ) async {
    await _pumpProfile(tester);

    await tester.tap(find.text('Body Measurements'));
    await tester.pumpAndSettle();

    // Body Measurements is now the open section: its fields are visible and
    // Personal Details has collapsed.
    expect(find.text('Height'), findsOneWidget);
    expect(find.text('Weight'), findsOneWidget);
    expect(find.text('Waist Circumference'), findsOneWidget);
    expect(find.text('Date of Birth'), findsNothing);

    await tester.tap(find.text('Lifestyle'));
    await tester.pumpAndSettle();

    expect(find.text('Smoking Status'), findsOneWidget);
    expect(find.text('Never'), findsOneWidget);
    expect(find.text('Former'), findsOneWidget);
    expect(find.text('Current'), findsOneWidget);
    expect(find.text('Height'), findsNothing);
  });

  testWidgets('editing a measurement autosaves', (WidgetTester tester) async {
    await _pumpProfile(tester);

    await tester.tap(find.text('Body Measurements'));
    await tester.pumpAndSettle();

    await tester.enterText(find.byType(TextField).first, '175');
    await tester.pump();

    // The header switches to "Saving..." while the mock save is in flight.
    expect(find.text('Saving...'), findsOneWidget);

    await tester.pump(const Duration(seconds: 1));
    expect(find.text('Autosaved'), findsOneWidget);
  });
}
