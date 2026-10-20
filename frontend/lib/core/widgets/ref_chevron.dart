import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// The chevron used by expandable section headers and select-style fields.
///
/// Drawn with a [CustomPainter] so the stroke weight matches the design
/// reference exactly (`M3 6.5 L9 12 L15 6.5`, 2px round stroke).
class RefChevron extends StatelessWidget {
  const RefChevron({
    super.key,
    this.size = 18,
    this.strokeWidth = 2,
    this.color = AppColors.refInk,
    this.rotated = false,
  });

  /// Edge length of the square the chevron is painted into.
  final double size;

  /// Stroke width in logical pixels.
  final double strokeWidth;

  /// Stroke colour.
  final Color color;

  /// Rotates the chevron 180 degrees (pointing up), used while expanded.
  final bool rotated;

  @override
  Widget build(BuildContext context) {
    return Transform.rotate(
      angle: rotated ? 3.141592653589793 : 0,
      child: CustomPaint(
        size: Size.square(size),
        painter: _ChevronPainter(strokeWidth: strokeWidth, color: color),
      ),
    );
  }
}

class _ChevronPainter extends CustomPainter {
  const _ChevronPainter({required this.strokeWidth, required this.color});

  final double strokeWidth;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    // Normalised path from the design reference (18x18 viewBox).
    final Path path = Path()
      ..moveTo(size.width * (3 / 18), size.height * (6.5 / 18))
      ..lineTo(size.width * (9 / 18), size.height * (12 / 18))
      ..lineTo(size.width * (15 / 18), size.height * (6.5 / 18));

    final Paint paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(_ChevronPainter oldDelegate) =>
      oldDelegate.color != color || oldDelegate.strokeWidth != strokeWidth;
}
