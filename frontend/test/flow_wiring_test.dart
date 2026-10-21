import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:medoracle/core/routing/app_router.dart';
import 'package:medoracle/core/routing/route_names.dart';
import 'package:medoracle/features/assessment/screens/assessment_main_finding_screen.dart';
import 'package:medoracle/features/doctors/screens/doctor_recommendation_screen.dart';
import 'package:medoracle/features/intake_wizard/screens/clinical_status_screen.dart';
import 'package:medoracle/features/intake_wizard/screens/first_assessment_screen.dart';
import 'package:medoracle/features/intake_wizard/screens/labs_vitals_screen.dart';
import 'package:medoracle/features/intake_wizard/screens/medications_family_screen.dart';
import 'package:medoracle/features/intake_wizard/screens/review_confirm_screen.dart';
import 'package:medoracle/features/intake_wizard/screens/risk_trajectory_screen.dart';
import 'package:medoracle/features/intake_wizard/screens/symptoms_screen.dart';
import 'package:medoracle/features/risk/screens/risk_analysis_screen.dart';

void main() {
  const Size phone = Size(390, 844);

  Future<void> setPhone(WidgetTester tester, Size size) async {
    tester.view.physicalSize = size;
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
  }

  Future<void> tapAndSettle(WidgetTester tester, Finder finder) async {
    await tester.ensureVisible(finder);
    await tester.pumpAndSettle();
    await tester.tap(finder);
    await tester.pumpAndSettle();
  }

  Widget withScope(Widget child) =>
      ProviderScope(child: MaterialApp(home: child));

  testWidgets('intake wizard walks Steps 2A-5 and submits into the results',
      (WidgetTester tester) async {
    await setPhone(tester, phone);

    final GoRouter router = createAppRouter();
    addTearDown(router.dispose);

    await tester.pumpWidget(
      ProviderScope(child: MaterialApp.router(routerConfig: router)),
    );
    // Let the mock profile load finish before leaving Step 1.
    await tester.pumpAndSettle(const Duration(milliseconds: 600));
    expect(router.routeInformationProvider.value.uri.path,
        RouteNames.step1Profile);

    // Step 2A - Clinical Status
    router.go(RouteNames.step2Clinical);
    await tester.pumpAndSettle();
    await tapAndSettle(tester, find.text('Next: Medications & Family'));

    // Step 2B - Medications & Family
    expect(router.routeInformationProvider.value.uri.path,
        RouteNames.step2Medications);
    await tapAndSettle(tester, find.text('Save & Continue'));

    // Step 3 - Symptoms
    expect(router.routeInformationProvider.value.uri.path,
        RouteNames.step3Symptoms);
    await tapAndSettle(tester, find.text('Next: Labs & Vitals'));

    // Step 4 - Labs & Vitals
    expect(router.routeInformationProvider.value.uri.path,
        RouteNames.step4Labs);
    await tapAndSettle(tester, find.text('Next: Review & Confirm'));

    // Step 5 - Review & Confirm
    expect(router.routeInformationProvider.value.uri.path,
        RouteNames.step5Review);
    await tapAndSettle(tester, find.text('Submit Assessment'));

    // Submission lands on Screen 6A, the main finding.
    expect(router.routeInformationProvider.value.uri.path,
        RouteNames.resultsReports);
    expect(find.text('Main finding'), findsOneWidget);
    expect(find.text('View risk trajectory'), findsOneWidget);
  });

  testWidgets('results flow is fully navigable', (WidgetTester tester) async {
    await setPhone(tester, phone);

    final GoRouter router = createAppRouter();
    addTearDown(router.dispose);

    await tester.pumpWidget(
      ProviderScope(child: MaterialApp.router(routerConfig: router)),
    );
    await tester.pumpAndSettle(const Duration(milliseconds: 600));

    // Screen 6A (main finding) -> risk trajectory.
    router.go(RouteNames.resultsReports);
    await tester.pumpAndSettle();
    expect(find.byType(AssessmentMainFindingScreen), findsOneWidget);
    await tapAndSettle(tester, find.text('View risk trajectory'));
    expect(find.byType(RiskTrajectoryScreen), findsOneWidget);
    expect(find.text('NEXT 12 MONTHS'), findsOneWidget);

    // Primary CTA -> care finder.
    await tapAndSettle(tester, find.text('Find a cardiologist near me'));
    expect(find.byType(DoctorRecommendationScreen), findsOneWidget);
    expect(find.text('CARE NEAR YOU'), findsOneWidget);

    // Back to the trajectory.
    await tapAndSettle(tester, find.text('Back to risk trajectory'));
    expect(find.text('NEXT 12 MONTHS'), findsOneWidget);

    // Secondary CTA -> back to Screen 6A.
    await tapAndSettle(tester, find.text('Back to results'));
    expect(find.byType(AssessmentMainFindingScreen), findsOneWidget);
    expect(find.text('Main finding'), findsOneWidget);
    expect(router.routeInformationProvider.value.uri.path,
        RouteNames.resultsReports);

    // Close returns to Step 5 of the wizard.
    await tapAndSettle(tester, find.text('Close'));
    expect(router.routeInformationProvider.value.uri.path,
        RouteNames.step5Review);

    // The explainable AI screen stays reachable on its own route.
    router.go(RouteNames.resultsReasoning);
    await tester.pumpAndSettle();
    expect(find.byType(FirstAssessmentScreen), findsOneWidget);
    expect(find.text('HOW OUR AI REACHED THIS RESULT'), findsOneWidget);

    // Primary CTA -> risk trajectory, pushed on top of the reasoning screen.
    await tapAndSettle(tester, find.text('View risk trajectory'));
    expect(find.byType(RiskTrajectoryScreen), findsOneWidget);
    expect(find.text('NEXT 12 MONTHS'), findsOneWidget);

    // The pushed page keeps the reasoning screen on the stack.
    router.pop();
    await tester.pumpAndSettle();
    expect(find.byType(FirstAssessmentScreen), findsOneWidget);
  });

  testWidgets('first assessment screen renders', (WidgetTester tester) async {
    await setPhone(tester, phone);
    await tester.pumpWidget(withScope(const FirstAssessmentScreen()));
    await tester.pumpAndSettle();
    expect(find.text('Visual reasoning map'), findsOneWidget);
    expect(find.text('The 3 specialist checks'), findsOneWidget);
    expect(find.text('What our AI debated'), findsOneWidget);
  });

  testWidgets('risk trajectory screen renders', (WidgetTester tester) async {
    await setPhone(tester, phone);
    await tester.pumpWidget(withScope(const RiskTrajectoryScreen()));
    await tester.pumpAndSettle();
    expect(find.text('Your heart risk is rising'), findsOneWidget);
    expect(find.text('WHAT HELPS MOST'), findsOneWidget);
  });

  testWidgets('main finding screen renders', (WidgetTester tester) async {
    await setPhone(tester, phone);
    await tester.pumpWidget(withScope(const AssessmentMainFindingScreen()));
    await tester.pumpAndSettle();
    expect(find.text('Main finding'), findsOneWidget);
    expect(find.text('Coronary Artery Disease Risk'), findsOneWidget);
    expect(find.text('How sure we are'), findsOneWidget);
    expect(find.text('Doctor to see'), findsOneWidget);
    expect(find.text('Cardiology'), findsOneWidget);
    expect(find.text('View risk trajectory'), findsOneWidget);
  });

  testWidgets('results hub renders', (WidgetTester tester) async {
    await setPhone(tester, phone);
    await tester.pumpWidget(withScope(const RiskAnalysisScreen()));
    await tester.pumpAndSettle();
    expect(find.text('Your heart risk is high'), findsOneWidget);
  });

  testWidgets('care finder renders', (WidgetTester tester) async {
    await setPhone(tester, phone);
    await tester.pumpWidget(withScope(const DoctorRecommendationScreen()));
    await tester.pumpAndSettle();
    expect(find.text('Cardiologists near you'), findsOneWidget);
  });

  testWidgets('intake step screens render', (WidgetTester tester) async {
    await setPhone(tester, phone);
    for (final Widget screen in <Widget>[
      const ClinicalStatusScreen(),
      const MedicationsFamilyScreen(),
      const SymptomsScreen(),
      const LabsVitalsScreen(),
      const ReviewConfirmScreen(),
    ]) {
      await tester.pumpWidget(withScope(screen));
      await tester.pumpAndSettle();
    }
  });

  testWidgets('screens survive a small viewport', (WidgetTester tester) async {
    await setPhone(tester, const Size(360, 640));
    for (final Widget screen in <Widget>[
      const ClinicalStatusScreen(),
      const MedicationsFamilyScreen(),
      const SymptomsScreen(),
      const LabsVitalsScreen(),
      const ReviewConfirmScreen(),
      const FirstAssessmentScreen(),
      const RiskTrajectoryScreen(),
      const AssessmentMainFindingScreen(),
      const RiskAnalysisScreen(),
      const DoctorRecommendationScreen(),
    ]) {
      await tester.pumpWidget(withScope(screen));
      await tester.pumpAndSettle();
    }
  });
}
