import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:medoracle/core/routing/app_router.dart';
import 'package:medoracle/core/routing/route_names.dart';
import 'package:medoracle/features/doctors/screens/doctor_recommendation_screen.dart';
import 'package:medoracle/features/intake_wizard/screens/first_assessment_screen.dart';
import 'package:medoracle/features/intake_wizard/screens/risk_trajectory_screen.dart';
import 'package:medoracle/features/risk/screens/risk_analysis_screen.dart';

void main() {
  Future<void> tapAndSettle(WidgetTester tester, Finder finder) async {
    await tester.ensureVisible(finder);
    await tester.pumpAndSettle();
    await tester.tap(finder);
    await tester.pumpAndSettle();
  }

  testWidgets('results flow is fully navigable', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    final GoRouter router = createAppRouter();
    addTearDown(router.dispose);

    await tester.pumpWidget(MaterialApp.router(routerConfig: router));
    // Let the mock profile load finish before leaving Step 1.
    await tester.pumpAndSettle(const Duration(milliseconds: 600));
    expect(router.routeInformationProvider.value.uri.path,
        RouteNames.step1Profile);

    // Step 5 hands over to the first assessment screen.
    router.go(RouteNames.resultsReasoning);
    await tester.pumpAndSettle();
    expect(find.text('HOW OUR AI REACHED THIS RESULT'), findsOneWidget);

    // Primary CTA -> risk trajectory (pushed on top of the reasoning screen).
    await tapAndSettle(tester, find.text('View risk trajectory'));
    expect(find.text('NEXT 12 MONTHS'), findsOneWidget);

    // The pushed page keeps the reasoning screen on the stack.
    router.pop();
    await tester.pumpAndSettle();
    expect(find.text('HOW OUR AI REACHED THIS RESULT'), findsOneWidget);

    // Primary CTA -> risk trajectory again.
    await tapAndSettle(tester, find.text('View risk trajectory'));
    expect(find.text('NEXT 12 MONTHS'), findsOneWidget);

    // Primary CTA -> care finder.
    await tapAndSettle(tester, find.text('Find a cardiologist near me'));
    expect(find.text('CARE NEAR YOU'), findsOneWidget);

    // Back to the trajectory.
    await tapAndSettle(tester, find.text('Back to risk trajectory'));
    expect(find.text('NEXT 12 MONTHS'), findsOneWidget);

    // Back to the results hub.
    await tapAndSettle(tester, find.text('Back to results'));
    expect(find.text('YOUR RESULT'), findsOneWidget);
    expect(router.routeInformationProvider.value.uri.path,
        RouteNames.resultsReports);

    // Hub -> reasoning again.
    await tapAndSettle(tester, find.text('How we reached this result'));
    expect(find.text('HOW OUR AI REACHED THIS RESULT'), findsOneWidget);

    // Close returns to the hub.
    await tapAndSettle(tester, find.text('Close'));
    expect(find.text('YOUR RESULT'), findsOneWidget);
  });

  testWidgets('intake wizard advances and hands over to the results',
      (WidgetTester tester) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    final GoRouter router = createAppRouter();
    addTearDown(router.dispose);

    await tester.pumpWidget(MaterialApp.router(routerConfig: router));
    await tester.pumpAndSettle(const Duration(milliseconds: 600));

    router.go(RouteNames.step2Clinical);
    await tester.pumpAndSettle();
    expect(find.text('Next: Medications & Family'), findsOneWidget);

    await tapAndSettle(tester, find.text('Next: Medications & Family'));
    expect(find.text('Next: Symptoms'), findsOneWidget);

    await tapAndSettle(tester, find.text('Next: Symptoms'));
    expect(find.text('Next: Labs & Vitals'), findsOneWidget);

    await tapAndSettle(tester, find.text('Next: Labs & Vitals'));
    expect(find.text('Next: Review & Confirm'), findsOneWidget);

    await tapAndSettle(tester, find.text('Next: Review & Confirm'));
    expect(find.text('Submit Assessment'), findsOneWidget);

    await tapAndSettle(tester, find.text('Submit Assessment'));
    expect(find.text('HOW OUR AI REACHED THIS RESULT'), findsOneWidget);
  });

  testWidgets('first assessment screen renders', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
    await tester.pumpWidget(
      const MaterialApp(home: FirstAssessmentScreen()),
    );
    await tester.pumpAndSettle();
    expect(find.text('Visual reasoning map'), findsOneWidget);
    expect(find.text('The 3 specialist checks'), findsOneWidget);
    expect(find.text('What our AI debated'), findsOneWidget);
  });

  testWidgets('risk trajectory screen renders', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
    await tester.pumpWidget(
      const MaterialApp(home: RiskTrajectoryScreen()),
    );
    await tester.pumpAndSettle();
    expect(find.text('Your heart risk is rising'), findsOneWidget);
    expect(find.text('WHAT HELPS MOST'), findsOneWidget);
  });

  testWidgets('results hub renders', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
    await tester.pumpWidget(const MaterialApp(home: RiskAnalysisScreen()));
    await tester.pumpAndSettle();
    expect(find.text('Your heart risk is high'), findsOneWidget);
  });

  testWidgets('care finder renders', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
    await tester.pumpWidget(
      const MaterialApp(home: DoctorRecommendationScreen()),
    );
    await tester.pumpAndSettle();
    expect(find.text('Cardiologists near you'), findsOneWidget);
  });

  testWidgets('screens survive a small viewport', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(360, 640);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
    for (final Widget screen in <Widget>[
      const FirstAssessmentScreen(),
      const RiskTrajectoryScreen(),
      const RiskAnalysisScreen(),
      const DoctorRecommendationScreen(),
    ]) {
      await tester.pumpWidget(MaterialApp(home: screen));
      await tester.pumpAndSettle();
    }
  });
}
