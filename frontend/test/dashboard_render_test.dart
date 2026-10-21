import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:medoracle/core/theme/app_theme.dart';
import 'package:medoracle/features/dashboard/screens/home_dashboard_screen.dart';
import 'package:medoracle/features/dashboard/widgets/dashboard_bottom_nav.dart';
import 'package:medoracle/features/dashboard/widgets/dashboard_metric_cards.dart';
import 'package:medoracle/features/dashboard/widgets/dashboard_recent_activity.dart';
import 'package:medoracle/features/dashboard/widgets/dashboard_risk_gauge.dart';

/// Renders the Home Dashboard at the design reference's 390px canvas and
/// writes a PNG to `build/verification/home_dashboard.png` so the screen can
/// be compared side by side with the `v8 - Home - Health Dashboard` frame of
/// `design_refs/MedOracle v3.1 - Intake Flow.html`.
///
/// Run with:  flutter test test/dashboard_render_test.dart
void main() {
  testWidgets('renders the dashboard and captures a PNG', (
    WidgetTester tester,
  ) async {
    const Size canvas = Size(390, 1088);
    tester.view.physicalSize = canvas;
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    // Load the bundled typeface so the capture matches the design reference.
    final FontLoader loader = FontLoader('Plus Jakarta Sans')
      ..addFont(rootBundle.load('assets/fonts/PlusJakartaSans.ttf'));
    await loader.load();

    final GlobalKey boundaryKey = GlobalKey();

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          debugShowCheckedModeBanner: false,
          theme: AppTheme.light,
          home: RepaintBoundary(
            key: boundaryKey,
            child: const HomeDashboardScreen(),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // ------------------------------------------------------------------
    // Geometry assertions against the design reference.
    // ------------------------------------------------------------------
    // The dashboard canvas is 390 wide, so the content column is 350 wide
    // (390 - 2 * 20 of page padding).
    expect(tester.getSize(find.byKey(boundaryKey)).width, 390);

    // Header bar: 72px content row inset by 8px, so the 44px avatar and
    // bell are vertically centred on y = 44.
    final Rect greeting = tester.getRect(find.text('Hello, Hafsa'));
    expect(greeting.center.dy, closeTo(44, 1));

    // Hero metric card: 6px below the 80px header, inset by 20px.
    final Rect hero = tester.getRect(find.byType(DashboardHeroMetricCard));
    expect(hero.left, 20);
    expect(hero.right, 370);
    expect(hero.top, 80);

    // The eyebrow inside the hero card is centred.
    final Rect eyebrow = tester.getRect(find.text('LATEST RESULT'));
    expect(eyebrow.center.dx, closeTo(195, 1));
    expect(eyebrow.top, 106);

    // The gauge is 280 x 164 and sits 10px below the eyebrow.
    final Rect gauge = tester.getRect(find.byType(DashboardRiskGauge));
    expect(gauge.size, const Size(280, 164));
    expect(gauge.top, 132);

    // Condition name, urgency pill and the report CTA follow the gauge.
    final Rect condition = tester.getRect(find.text('Coronary Artery Disease Risk'));
    expect(condition.top, 302);
    expect(condition.center.dx, closeTo(195, 1));

    final Rect urgency = tester.getRect(find.text('High urgency'));
    expect(urgency.top, 346);

    final Rect report = tester.getRect(find.text('View Full Report'));
    expect(report.top, 404);

    // "Quick actions" sits 28px below the hero card.
    final Rect quickActions = tester.getRect(find.text('Quick actions'));
    expect(quickActions.top, 488);

    // The primary action card is 350 x 80 and starts 12px below the header.
    final Rect primary =
        tester.getRect(find.byType(DashboardPrimaryActionCard));
    expect(primary.size, const Size(350, 80));
    expect(primary.top, 524);

    // The two compact cards share the row: 169 wide each. The reference
    // wraps "See how habits lower risk" onto two lines, so the cards are
    // 144 tall rather than their 132px minimum.
    final Finder compactFinder = find.byType(DashboardCompactActionCard);
    expect(compactFinder, findsNWidgets(2));
    expect(tester.getSize(compactFinder.at(0)).height, 144);
    expect(tester.getSize(compactFinder.at(0)).width, 169);
    expect(tester.getTopLeft(compactFinder.at(0)).dy, 616);
    expect(tester.getTopLeft(compactFinder.at(1)).dx, 201);

    // "Recent assessments" and the list that follows it.
    final Rect recent = tester.getRect(find.text('Recent assessments'));
    expect(recent.top, 788);

    final Rect list = tester.getRect(find.byType(DashboardRecentActivity));
    expect(list.top, 824);
    // 76px for the first row plus the 1px hairline plus 76px for the second.
    expect(list.height, 153);

    // The bottom navigation bar is 8 + 58 + 22 + a 1px top border = 89.
    expect(tester.getSize(find.byType(DashboardBottomNavBar)).height, 89);
    expect(tester.getTopLeft(find.byType(DashboardBottomNavBar)).dy, 999);

    // The primary call to action is the first quick action.
    expect(find.text('Start New Assessment'), findsOneWidget);
    expect(find.text('Recent assessments'), findsOneWidget);

    // ------------------------------------------------------------------
    // PNG capture for visual comparison with the reference frame.
    // ------------------------------------------------------------------
    await tester.runAsync(() async {
      final RenderRepaintBoundary boundary = boundaryKey.currentContext!
          .findRenderObject()! as RenderRepaintBoundary;
      final ui.Image image = await boundary.toImage(pixelRatio: 2.0);
      final ByteData? bytes =
          await image.toByteData(format: ui.ImageByteFormat.png);
      image.dispose();

      final Directory outDir = Directory('build/verification');
      if (!outDir.existsSync()) {
        outDir.createSync(recursive: true);
      }
      File('build/verification/home_dashboard.png')
          .writeAsBytesSync(bytes!.buffer.asUint8List());

      expect(bytes.lengthInBytes, greaterThan(1000));
    });
  });
}
