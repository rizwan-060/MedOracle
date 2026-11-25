import 'dart:math' as math;

import 'package:material_ui/material_ui.dart';

import '../../../core/theme/app_colors.dart';
import 'onboarding_type.dart';

/// Illustration frame and canvas painters used by the Welcome cards.
///
/// Every painter receives a logical `300 x 150` canvas and scales it to the
/// available box, so all coordinates stay tied to the design reference.
class WelcomeIllustration extends StatelessWidget {
  const WelcomeIllustration({super.key, required this.painter});

  final CustomPainter painter;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 158,
      width: double.infinity,
      child: Container(
        clipBehavior: Clip.antiAlias,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppColors.onboardingPeachSurface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: AppColors.onboardingPeachBorder,
            width: 2,
          ),
        ),
        child: CustomPaint(painter: painter, size: Size.infinite),
      ),
    );
  }
}

abstract final class _CanvasKit {
  static Paint fill(Color color) => Paint()
    ..color = color
    ..style = PaintingStyle.fill;

  static Paint stroke(
    Color color,
    double width, {
    StrokeCap cap = StrokeCap.round,
    StrokeJoin join = StrokeJoin.round,
  }) =>
      Paint()
        ..color = color
        ..style = PaintingStyle.stroke
        ..strokeWidth = width
        ..strokeCap = cap
        ..strokeJoin = join;

  static void text(
    Canvas canvas,
    String label,
    Offset anchor,
    TextStyle style, {
    TextAlign align = TextAlign.left,
  }) {
    final TextPainter painter = TextPainter(
      text: TextSpan(text: label, style: style),
      textAlign: align,
      textDirection: TextDirection.ltr,
    )..layout();

    final double dx = switch (align) {
      TextAlign.center => anchor.dx - painter.width / 2,
      TextAlign.right => anchor.dx - painter.width,
      _ => anchor.dx,
    };
    painter.paint(canvas, Offset(dx, anchor.dy - painter.height / 2));
  }

  static void check(
    Canvas canvas,
    Offset a,
    Offset b,
    Offset c,
    Paint paint,
  ) {
    canvas.drawPath(
      Path()
        ..moveTo(a.dx, a.dy)
        ..lineTo(b.dx, b.dy)
        ..lineTo(c.dx, c.dy),
      paint,
    );
  }
}

/// Card 1: answers flowing into a single report.
class ReportIllustrationPainter extends CustomPainter {
  const ReportIllustrationPainter();

  @override
  void paint(Canvas canvas, Size size) {
    canvas.save();
    canvas.scale(size.width / 300, size.height / 150);

    for (final double y in <double>[32, 75, 118]) {
      const double x = 26;
      canvas.drawCircle(
        Offset(x, y),
        9,
        _CanvasKit.fill(AppColors.headerText),
      );
      _CanvasKit.check(
        canvas,
        Offset(x - 4, y),
        Offset(x - 1, y + 3),
        Offset(x + 4, y - 4),
        _CanvasKit.stroke(AppColors.authInputSurface, 2),
      );
    }

    _CanvasKit.text(
      canvas,
      'About you',
      const Offset(42, 36),
      OnboardingType.sans(11, FontWeight.w500, AppColors.headerText),
    );
    _CanvasKit.text(
      canvas,
      'Daily habits',
      const Offset(42, 79),
      OnboardingType.sans(11, FontWeight.w500, AppColors.headerText),
    );
    _CanvasKit.text(
      canvas,
      'Health history',
      const Offset(42, 122),
      OnboardingType.sans(11, FontWeight.w500, AppColors.headerText),
    );

    canvas.drawPath(
      Path()
        ..moveTo(134, 75)
        ..lineTo(164, 75)
        ..moveTo(156, 67)
        ..lineTo(165, 75)
        ..lineTo(156, 83),
      _CanvasKit.stroke(AppColors.onboardingAmber, 3),
    );

    final RRect report = RRect.fromRectAndRadius(
      const Rect.fromLTWH(180, 10, 106, 130),
      const Radius.circular(14),
    );
    canvas.drawRRect(report, _CanvasKit.fill(AppColors.authInputSurface));
    canvas.drawRRect(
      report,
      _CanvasKit.stroke(AppColors.headerText, 2.5),
    );

    _CanvasKit.text(
      canvas,
      'Your report',
      const Offset(233, 34),
      OnboardingType.sans(11, FontWeight.w500, AppColors.headerText),
      align: TextAlign.center,
    );

    final Path heart = Path()
      ..moveTo(233, 86)
      ..cubicTo(212, 72, 211, 56, 222, 53)
      ..cubicTo(229, 51, 233, 56, 233, 59)
      ..cubicTo(233, 56, 237, 51, 244, 53)
      ..cubicTo(255, 56, 254, 72, 233, 86)
      ..close();
    canvas.drawPath(
      heart,
      _CanvasKit.fill(
        AppColors.onboardingHeartFill.withValues(alpha: 0.7),
      ),
    );
    canvas.drawPath(
      heart,
      _CanvasKit.stroke(AppColors.onboardingHeartStroke, 2),
    );

    canvas.drawPath(
      Path()
        ..moveTo(202, 102)
        ..lineTo(222, 102)
        ..lineTo(227, 93)
        ..lineTo(234, 111)
        ..lineTo(240, 99)
        ..lineTo(246, 99),
      _CanvasKit.stroke(AppColors.headerText, 2),
    );

    canvas.drawRRect(
      RRect.fromRectAndRadius(
        const Rect.fromLTWH(196, 120, 74, 6),
        const Radius.circular(3),
      ),
      _CanvasKit.fill(AppColors.headerText.withValues(alpha: 0.25)),
    );

    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant ReportIllustrationPainter oldDelegate) => false;
}

/// Card 2: five agents reaching the agreed answer.
class ConsensusIllustrationPainter extends CustomPainter {
  const ConsensusIllustrationPainter();

  static const List<double> _doctorX = <double>[40, 95, 150, 205, 260];

  @override
  void paint(Canvas canvas, Size size) {
    canvas.save();
    canvas.scale(size.width / 300, size.height / 150);

    final Paint connector = _CanvasKit.stroke(AppColors.onboardingAmber, 2.5);
    for (final double x in _doctorX) {
      if (x == 150) {
        canvas.drawLine(
          const Offset(150, 70),
          const Offset(150, 100),
          connector,
        );
      } else {
        canvas.drawPath(
          Path()
            ..moveTo(x, 70)
            ..lineTo(x, 92)
            ..cubicTo(x, 97, (x + 150) / 2, 100, 150, 100),
          connector,
        );
      }
    }

    for (final double x in _doctorX) {
      canvas.drawCircle(
        Offset(x, 48),
        17,
        _CanvasKit.fill(AppColors.authInputSurface),
      );
      canvas.drawCircle(
        Offset(x, 48),
        17,
        _CanvasKit.stroke(AppColors.headerText, 2.5),
      );

      canvas.drawCircle(
        Offset(x, 44),
        5,
        _CanvasKit.fill(AppColors.headerText),
      );

      canvas.drawPath(
        Path()
          ..moveTo(x - 9, 58)
          ..addArc(
            Rect.fromLTWH(x - 9, 51, 18, 14),
            math.pi,
            math.pi,
          )
          ..close(),
        _CanvasKit.fill(AppColors.headerText),
      );

      canvas.drawPath(
        Path()
          ..moveTo(x - 4, 56)
          ..lineTo(x - 4, 61)
          ..cubicTo(x - 4, 65, x + 4, 65, x + 4, 61)
          ..lineTo(x + 4, 56),
        _CanvasKit.stroke(AppColors.authInputSurface, 1.6),
      );
    }

    canvas.drawRRect(
      RRect.fromRectAndRadius(
        const Rect.fromLTWH(96, 100, 108, 34),
        const Radius.circular(17),
      ),
      _CanvasKit.fill(AppColors.headerText),
    );
    _CanvasKit.check(
      canvas,
      const Offset(112, 117),
      const Offset(118, 123),
      const Offset(128, 111),
      _CanvasKit.stroke(AppColors.authInputSurface, 3.5),
    );
    _CanvasKit.text(
      canvas,
      'Agreed',
      const Offset(138, 121),
      OnboardingType.sans(12, FontWeight.w600, AppColors.authInputSurface),
      align: TextAlign.center,
    );

    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant ConsensusIllustrationPainter oldDelegate) =>
      false;
}

/// Card 3: two ten-year trajectories.
class TrajectoryIllustrationPainter extends CustomPainter {
  const TrajectoryIllustrationPainter();

  @override
  void paint(Canvas canvas, Size size) {
    canvas.save();
    canvas.scale(size.width / 300, size.height / 150);

    canvas.drawPath(
      Path()
        ..moveTo(30, 20)
        ..lineTo(30, 112)
        ..lineTo(282, 112),
      _CanvasKit.stroke(
        AppColors.headerText.withValues(alpha: 0.35),
        2,
      ),
    );

    final Path changed = Path()
      ..moveTo(30, 96)
      ..cubicTo(100, 90, 170, 62, 270, 26);
    _drawDottedPath(
      canvas,
      changed,
      _CanvasKit.stroke(AppColors.onboardingAmber, 3.5),
      dash: 2,
      gap: 8,
    );

    canvas.drawPath(
      Path()
        ..moveTo(30, 96)
        ..cubicTo(100, 96, 170, 94, 270, 90),
      _CanvasKit.stroke(AppColors.headerText, 5),
    );

    canvas.drawCircle(
      const Offset(270, 26),
      6,
      _CanvasKit.fill(AppColors.onboardingPeachSurface),
    );
    canvas.drawCircle(
      const Offset(270, 26),
      6,
      _CanvasKit.stroke(AppColors.onboardingAmber, 2.5),
    );
    canvas.drawCircle(
      const Offset(270, 90),
      8,
      _CanvasKit.fill(AppColors.headerText),
    );

    _CanvasKit.text(
      canvas,
      'If nothing changes',
      const Offset(112, 48),
      OnboardingType.sans(
        11,
        FontWeight.w500,
        AppColors.headerText.withValues(alpha: 0.7),
      ),
      align: TextAlign.center,
    );
    _CanvasKit.text(
      canvas,
      'With small changes',
      const Offset(168, 108),
      OnboardingType.sans(11, FontWeight.w500, AppColors.headerText),
      align: TextAlign.center,
    );
    _CanvasKit.text(
      canvas,
      'Today',
      const Offset(30, 136),
      OnboardingType.sans(
        10.5,
        FontWeight.w400,
        AppColors.headerText.withValues(alpha: 0.75),
      ),
    );
    _CanvasKit.text(
      canvas,
      'In 10 years',
      const Offset(282, 136),
      OnboardingType.sans(
        10.5,
        FontWeight.w400,
        AppColors.headerText.withValues(alpha: 0.75),
      ),
      align: TextAlign.right,
    );

    canvas.restore();
  }

  void _drawDottedPath(
    Canvas canvas,
    Path path,
    Paint paint, {
    required double dash,
    required double gap,
  }) {
    final metric = path.computeMetrics().first;
    double distance = 0;
    while (distance < metric.length) {
      final double end = math.min(distance + dash, metric.length);
      canvas.drawPath(metric.extractPath(distance, end), paint);
      distance += dash + gap;
    }
  }

  @override
  bool shouldRepaint(covariant TrajectoryIllustrationPainter oldDelegate) =>
      false;
}

/// Tiny custom check drawn at the start of each pill.
class PillCheckPainter extends CustomPainter {
  const PillCheckPainter();

  @override
  void paint(Canvas canvas, Size size) {
    canvas.save();
    canvas.scale(size.width / 16, size.height / 16);
    _CanvasKit.check(
      canvas,
      const Offset(3.5, 8.5),
      const Offset(6.5, 11.5),
      const Offset(12.5, 4.5),
      _CanvasKit.stroke(AppColors.deepInk, 2),
    );
    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant PillCheckPainter oldDelegate) => false;
}

/// One of the five selectable agent icons in the care-team wheel.
class AgentGlyph extends StatelessWidget {
  const AgentGlyph({super.key, required this.index, required this.selected});

  final int index;
  final bool selected;

  static const List<Color> _fills = <Color>[
    AppColors.pastelMist,
    AppColors.pastelSage,
    AppColors.pastelSand,
    AppColors.pastelBlush,
    AppColors.pastelButter,
  ];
  static const List<Color> _strokes = <Color>[
    AppColors.onboardingSlateSoft,
    AppColors.mutedGreen,
    AppColors.alertMedium,
    AppColors.terraCotta,
    AppColors.onboardingAmber,
  ];

  @override
  Widget build(BuildContext context) {
    final Color fill = _fills[index % _fills.length];
    final Color stroke = _strokes[index % _strokes.length];

    Widget shape = Container(
      width: 64,
      height: 64,
      decoration: BoxDecoration(
        color: fill,
        borderRadius: BorderRadius.circular(index == 1 ? 20 : 32),
        border: Border.all(color: stroke, width: 2),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.deepInk.withValues(alpha: 0.18),
            offset: const Offset(0, 4),
            blurRadius: 6,
          ),
        ],
      ),
      child: Icon(
        <IconData>[
          Icons.monitor_heart_outlined,
          Icons.history_edu_outlined,
          Icons.eco_outlined,
          Icons.trending_up_rounded,
          Icons.alt_route_rounded,
        ][index % 5],
        size: 26,
        color: stroke,
      ),
    );

    if (index == 2 || index == 4) {
      shape = ClipPath(
        clipper: index == 2 ? const _HexagonClipper() : const _OctagonClipper(),
        child: shape,
      );
    }

    return Transform.scale(scale: selected ? 1.08 : 1, child: shape);
  }
}

class _HexagonClipper extends CustomClipper<Path> {
  const _HexagonClipper();

  @override
  Path getClip(Size size) {
    final Path path = Path();
    for (int i = 0; i < 6; i++) {
      final double angle = (math.pi / 3) * i - math.pi / 2;
      final Offset point = Offset(
        size.width / 2 + size.width / 2 * math.cos(angle),
        size.height / 2 + size.height / 2 * math.sin(angle),
      );
      if (i == 0) {
        path.moveTo(point.dx, point.dy);
      } else {
        path.lineTo(point.dx, point.dy);
      }
    }
    path.close();
    return path;
  }

  @override
  bool shouldReclip(covariant CustomClipper<Path> oldClipper) => false;
}

class _OctagonClipper extends CustomClipper<Path> {
  const _OctagonClipper();

  @override
  Path getClip(Size size) {
    final Path path = Path();
    for (int i = 0; i < 8; i++) {
      final double angle = (math.pi / 4) * i + math.pi / 8;
      final Offset point = Offset(
        size.width / 2 + size.width / 2 * math.cos(angle),
        size.height / 2 + size.height / 2 * math.sin(angle),
      );
      if (i == 0) {
        path.moveTo(point.dx, point.dy);
      } else {
        path.lineTo(point.dx, point.dy);
      }
    }
    path.close();
    return path;
  }

  @override
  bool shouldReclip(covariant CustomClipper<Path> oldClipper) => false;
}
