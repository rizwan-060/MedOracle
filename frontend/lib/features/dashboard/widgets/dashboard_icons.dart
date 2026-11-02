import 'package:flutter/material.dart';

/// Vector glyphs used across the Home Dashboard.
///
/// Every glyph is traced from the MedOracle v3.1 design reference on a 24x24
/// view box and scaled to the requested size, so no raster assets are needed.
enum DashboardIconType {
  /// Filled home glyph of the bottom navigation bar.
  home,

  /// Clock glyph of the bottom navigation bar.
  history,

  /// Stethoscope glyph of the bottom navigation bar.
  doctors,

  /// Person glyph used by the avatar and the profile tab.
  profile,

  /// Notification bell of the header bar.
  bell,

  /// Clipboard glyph of the "Start New Assessment" card.
  assessment,

  /// Sliders glyph of the "Simulate Lifestyle" card.
  lifestyle,

  /// Map pin glyph of the "Find Specialists" card.
  specialist,

  /// Tick of the "Completed" status badge.
  check,

  /// Chevron pointing right, used by the action cards.
  chevronRight,

  /// Arrow pointing right, used by the hero call to action.
  arrowRight,
}

/// Renders a [DashboardIconType] glyph as a stroked vector path.
class DashboardIcon extends StatelessWidget {
  const DashboardIcon(
    this.type, {
    super.key,
    this.size = 24,
    this.color,
    this.strokeWidth = 1.8,
    this.filled = false,
  });

  /// Which glyph to draw.
  final DashboardIconType type;

  /// Rendered edge length of the glyph.
  final double size;

  /// Stroke (and fill) colour; defaults to the theme's primary colour.
  final Color? color;

  /// Stroke width in view-box units.
  final double strokeWidth;

  /// Whether the glyph also gets a translucent fill.
  final bool filled;

  @override
  Widget build(BuildContext context) {
    return SizedBox.square(
      dimension: size,
      child: CustomPaint(
        painter: _DashboardIconPainter(
          type: type,
          color: color ?? Theme.of(context).colorScheme.primary,
          strokeWidth: strokeWidth,
          filled: filled,
        ),
      ),
    );
  }
}

/// Paints a [DashboardIconType] glyph onto the canvas.
class _DashboardIconPainter extends CustomPainter {
  const _DashboardIconPainter({
    required this.type,
    required this.color,
    required this.strokeWidth,
    required this.filled,
  });

  final DashboardIconType type;
  final Color color;
  final double strokeWidth;
  final bool filled;

  @override
  void paint(Canvas canvas, Size size) {
    final double scale = size.width / 24;
    canvas.save();
    canvas.scale(scale);

    final Paint stroke = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final Path path = _glyphPath();
    if (filled) {
      canvas.drawPath(
        path,
        Paint()
          ..color = color.withValues(alpha: 0.14)
          ..style = PaintingStyle.fill,
      );
    }
    canvas.drawPath(path, stroke);
    canvas.restore();
  }

  /// Builds the 24x24 outline of the requested glyph.
  Path _glyphPath() {
    return switch (type) {
      DashboardIconType.home => Path()
        ..moveTo(4, 11)
        ..lineTo(12, 4)
        ..lineTo(20, 11)
        ..lineTo(20, 19.5)
        ..arcToPoint(
          const Offset(19.5, 20),
          radius: const Radius.circular(0.5),
          clockwise: true,
        )
        ..lineTo(15, 20)
        ..lineTo(15, 14)
        ..lineTo(9, 14)
        ..lineTo(9, 20)
        ..lineTo(4.5, 20)
        ..arcToPoint(
          const Offset(4, 19.5),
          radius: const Radius.circular(0.5),
          clockwise: true,
        )
        ..close(),
      DashboardIconType.history => Path()
        ..addOval(Rect.fromCircle(center: const Offset(12, 12), radius: 8.2))
        ..moveTo(12, 7.5)
        ..lineTo(12, 12)
        ..lineTo(15, 14),
      DashboardIconType.doctors => Path()
        ..moveTo(6, 3.5)
        ..lineTo(6, 8.7)
        ..arcToPoint(
          const Offset(14, 8.7),
          radius: const Radius.circular(4),
          clockwise: false,
        )
        ..lineTo(14, 3.5)
        ..moveTo(10, 12.7)
        ..lineTo(10, 14.3)
        ..arcToPoint(
          const Offset(19.2, 14.3),
          radius: const Radius.circular(4.6),
          clockwise: false,
        )
        ..lineTo(19.2, 12.9)
        ..addOval(Rect.fromCircle(center: const Offset(19.2, 10.8), radius: 2)),
      DashboardIconType.profile => Path()
        ..addOval(Rect.fromCircle(center: const Offset(12, 8.5), radius: 3.6))
        ..moveTo(5, 20)
        ..cubicTo(5.7, 16.4, 8.6, 14.5, 12, 14.5)
        ..cubicTo(15.4, 14.5, 18.3, 16.4, 19, 20),
      DashboardIconType.bell => Path()
        ..moveTo(6, 9.5)
        ..arcToPoint(
          const Offset(18, 9.5),
          radius: const Radius.circular(6),
          clockwise: true,
        )
        ..cubicTo(18, 14.3, 20, 15.5, 20, 15.5)
        ..lineTo(4, 15.5)
        ..cubicTo(4, 15.5, 6, 14.3, 6, 9.5)
        ..close()
        ..moveTo(10, 19)
        ..arcToPoint(
          const Offset(14, 19),
          radius: const Radius.circular(2),
          clockwise: false,
        ),
      DashboardIconType.assessment => Path()
        ..addRRect(
          RRect.fromRectAndRadius(
            const Rect.fromLTWH(5, 4, 14, 17),
            const Radius.circular(3),
          ),
        )
        ..moveTo(9, 4)
        ..lineTo(15, 4)
        ..lineTo(15, 6.6)
        ..lineTo(9, 6.6)
        ..close()
        ..moveTo(12, 10)
        ..lineTo(12, 16)
        ..moveTo(9, 13)
        ..lineTo(15, 13),
      DashboardIconType.lifestyle => Path()
        ..moveTo(4, 7)
        ..lineTo(13, 7)
        ..moveTo(19, 7)
        ..lineTo(20, 7)
        ..moveTo(4, 17)
        ..lineTo(5, 17)
        ..moveTo(11, 17)
        ..lineTo(20, 17)
        ..addOval(Rect.fromCircle(center: const Offset(16, 7), radius: 2.6))
        ..addOval(Rect.fromCircle(center: const Offset(8, 17), radius: 2.6)),
      DashboardIconType.specialist => Path()
        ..moveTo(12, 21)
        ..cubicTo(12, 21, 5.5, 15.4, 5.5, 10.5)
        ..arcToPoint(
          const Offset(18.5, 10.5),
          radius: const Radius.circular(6.5),
          clockwise: true,
        )
        ..cubicTo(18.5, 15.4, 12, 21, 12, 21)
        ..close()
        ..moveTo(12, 8.2)
        ..lineTo(12, 12.8)
        ..moveTo(9.7, 10.5)
        ..lineTo(14.3, 10.5),
      DashboardIconType.check => Path()
        ..moveTo(3, 7.4)
        ..lineTo(5.8, 10)
        ..lineTo(11, 4.4),
      DashboardIconType.chevronRight => Path()
        ..moveTo(9, 6)
        ..lineTo(15, 12)
        ..lineTo(9, 18),
      DashboardIconType.arrowRight => Path()
        ..moveTo(5, 12)
        ..lineTo(19, 12)
        ..moveTo(13, 6)
        ..lineTo(19, 12)
        ..lineTo(13, 18),
    };
  }

  @override
  bool shouldRepaint(covariant _DashboardIconPainter oldDelegate) {
    return oldDelegate.type != type ||
        oldDelegate.color != color ||
        oldDelegate.strokeWidth != strokeWidth ||
        oldDelegate.filled != filled;
  }
}
