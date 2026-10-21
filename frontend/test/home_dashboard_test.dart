import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:medoracle/core/routing/app_router.dart';
import 'package:medoracle/core/routing/route_names.dart';
import 'package:medoracle/features/assessment/screens/assessment_main_finding_screen.dart';
import 'package:medoracle/features/dashboard/screens/home_dashboard_screen.dart';

void main() {
  const Size phone = Size(390, 844);

  Future<void> setPhone(WidgetTester tester, Size size) async {
    tester.view.physicalSize = size;
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
  }

  Future<GoRouter> pumpDashboard(WidgetTester tester) async {
    final GoRouter router = createAppRouter();
    addTearDown(router.dispose);
    await tester.pumpWidget(
      ProviderScope(child: MaterialApp.router(routerConfig: router)),
    );
    // Let the mock profile load finish before leaving Step 1.
    await tester.pumpAndSettle(const Duration(milliseconds: 600));
    router.go(RouteNames.home);
    await tester.pumpAndSettle();
    return router;
  }

  testWidgets('dashboard renders the hub content', (WidgetTester tester) async {
    await setPhone(tester, phone);
    await pumpDashboard(tester);

    expect(find.byType(HomeDashboardScreen), findsOneWidget);
    expect(find.text('Hello, Hafsa'), findsOneWidget);
    expect(find.text('LATEST RESULT'), findsOneWidget);
    expect(find.text('24'), findsOneWidget);
    expect(find.text('Coronary Artery Disease Risk'), findsOneWidget);
    expect(find.text('High urgency'), findsOneWidget);
    expect(find.text('View Full Report'), findsOneWidget);
    expect(find.text('Quick actions'), findsOneWidget);
    expect(find.text('Start New Assessment'), findsOneWidget);
    expect(find.text('Simulate Lifestyle'), findsOneWidget);
    expect(find.text('Find Specialists'), findsOneWidget);
    expect(find.text('Recent assessments'), findsOneWidget);
    expect(find.text('Type 2 Diabetes Check'), findsOneWidget);
    expect(find.text('General Wellness'), findsOneWidget);
    expect(find.text('Completed'), findsNWidgets(2));
    expect(find.text('Home'), findsOneWidget);
    expect(find.text('History'), findsOneWidget);
    expect(find.text('Doctors'), findsOneWidget);
    expect(find.text('Profile'), findsOneWidget);
  });

  testWidgets('start new assessment routes to the Profile step',
      (WidgetTester tester) async {
    await setPhone(tester, phone);
    final GoRouter router = await pumpDashboard(tester);

    await tester.tap(find.text('Start New Assessment'));
    await tester.pumpAndSettle();

    expect(router.routeInformationProvider.value.uri.path,
        RouteNames.step1Profile);
  });

  testWidgets('view full report routes to the main finding',
      (WidgetTester tester) async {
    await setPhone(tester, phone);
    final GoRouter router = await pumpDashboard(tester);

    await tester.tap(find.text('View Full Report'));
    await tester.pumpAndSettle();

    expect(router.routeInformationProvider.value.uri.path,
        RouteNames.resultsReports);
    expect(find.byType(AssessmentMainFindingScreen), findsOneWidget);
    expect(find.text('Main finding'), findsOneWidget);
  });

  testWidgets('dashboard survives a small viewport', (WidgetTester tester) async {
    await setPhone(tester, const Size(360, 640));
    await pumpDashboard(tester);

    expect(find.byType(HomeDashboardScreen), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
