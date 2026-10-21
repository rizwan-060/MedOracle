import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:medoracle/core/theme/app_theme.dart';
import 'package:medoracle/features/profile/screens/profile_screen.dart';

/// Renders Step 1 at the design reference's exact 390 x 844 canvas and writes a
/// PNG to `build/verification/step1_profile.png` so the screen can be compared
/// side by side with `design_refs/MedOracle v3.1 - Intake Flow.html`.
///
/// Run with:  flutter test test/step1_render_test.dart
void main() {
  testWidgets('renders Step 1 at 390x844 and captures a PNG', (
    WidgetTester tester,
  ) async {
    const Size canvas = Size(390, 844);
    tester.view.physicalSize = canvas;
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    final GlobalKey boundaryKey = GlobalKey();

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          debugShowCheckedModeBanner: false,
          theme: AppTheme.light,
          home: RepaintBoundary(
            key: boundaryKey,
            child: const ProfileScreen(),
          ),
        ),
      ),
    );

    // Let the mock profile load, then settle the layout.
    await tester.pump();
    await tester.pump(const Duration(seconds: 1));
    // Note: no `pumpAndSettle` - the focused-field caret blinks forever.
    await tester.pump(const Duration(milliseconds: 100));

    // ------------------------------------------------------------------
    // Geometry assertions against the design reference.
    // ------------------------------------------------------------------
    final Finder header = find.text('MedOracle');
    expect(header, findsOneWidget);
    expect(tester.getSize(find.byKey(boundaryKey)), canvas);

    // Page padding is 20px; the open card sits 36px from the edge (20 + 16).
    final Rect cardTopLeft = tester.getRect(find.text('Personal Details'));
    expect(cardTopLeft.left, 36);

    // Footer actions span the content width (390 - 2 * 20 = 350).
    final Size ctaSize = tester.getSize(find.text('Next: Clinical Status'));
    expect(ctaSize.height, greaterThan(0));

    // ------------------------------------------------------------------
    // PNG capture for visual comparison with the reference frame.
    // ------------------------------------------------------------------
    // `toImage` needs the real event loop, so it must run inside `runAsync`.
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
      File('build/verification/step1_profile.png')
          .writeAsBytesSync(bytes!.buffer.asUint8List());

      expect(bytes.lengthInBytes, greaterThan(1000));
    });
  });
}
