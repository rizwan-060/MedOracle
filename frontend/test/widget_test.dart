import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:medoracle/features/onboarding/screens/onboarding_screen.dart';
import 'package:medoracle/features/splash/screens/splash_screen.dart';
import 'package:medoracle/main.dart';

void main() {
  testWidgets('App starts on SplashScreen and transitions to OnboardingScreen',
      (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: MedOracleApp()));

    // Starts on SplashScreen
    expect(find.byType(SplashScreen), findsOneWidget);
    expect(find.text('MedOracle'), findsOneWidget);

    // Pump past the 2.2s splash duration
    await tester.pump(const Duration(milliseconds: 2500));
    await tester.pump(const Duration(milliseconds: 200));

    // Now on OnboardingScreen
    expect(find.byType(OnboardingScreen), findsOneWidget);
    expect(find.text('Understand Your\nHealth, Earlier'), findsOneWidget);
    expect(find.text('Early signals'), findsOneWidget);
    expect(find.text('Clear insights'), findsOneWidget);
    expect(find.text('Private by design'), findsOneWidget);
  });

  testWidgets('OnboardingScreen navigates across 3 slides',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: OnboardingScreen(),
        ),
      ),
    );
    await tester.pump(const Duration(milliseconds: 100));

    // Slide 1: Welcome & Early signals
    expect(find.text('Understand Your\nHealth, Earlier'), findsOneWidget);
    expect(find.text('Next'), findsOneWidget);

    // Tap Next -> animate to Slide 2
    await tester.tap(find.text('Next'));
    for (int i = 0; i < 15; i++) {
      await tester.pump(const Duration(milliseconds: 40));
    }

    // Slide 2: Many Perspectives. One Clear View.
    expect(find.text('Many Perspectives.\nOne Clear View.'), findsOneWidget);
    expect(find.text('Health\nAssessment'), findsOneWidget);
    expect(find.text('What you feel'), findsOneWidget);
    expect(find.text('Next'), findsOneWidget);

    // Tap Next -> animate to Slide 3
    await tester.tap(find.text('Next'));
    for (int i = 0; i < 15; i++) {
      await tester.pump(const Duration(milliseconds: 40));
    }

    // Slide 3: Explore What Your Choices Could Change
    expect(find.text('Explore What Your\nChoices Could Change'), findsOneWidget);
    expect(find.text('Health Trajectory'), findsOneWidget);
    expect(find.text('ILLUSTRATIVE'), findsOneWidget);
    expect(find.text('Get Started'), findsOneWidget);
  });
}
