import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Circular consensus-confidence gauge (design: 96x96 ring, 88.5% filled).
///
/// The ring draws its track first, then the maroon progress arc sweeping
/// clockwise from 12 o'clock, with the percentage centred inside.
class ConfidenceRing extends StatelessWidget {
  const ConfidenceRing({
    super.key,
    required this.percent,
    this.size = 96,
  });

  /// Confidence in percent (0-100).
  final double percent;

  final double size;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        fit: StackFit.expand,
        children: <Widget>[
          CustomPaint(
            painter: _RingPainter(fraction: percent / 100),
          ),
          Center(
            child: Text(
              '${percent.toStringAsFixed(1)}%',
              style: const TextStyle(
                fontSize: 19,
                fontWeight: FontWeight.w800,
                color: AppColors.textPrimary,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _RingPainter extends CustomPainter {
  const _RingPainter({required this.fraction});

  final double fraction;

  @override
  void paint(Canvas canvas, Size size) {
    final Offset center = Offset(size.width / 2, size.height / 2);
    final double radius = (size.width - 10) / 2;
    final Rect ring = Rect.fromCircle(center: center, radius: radius);

    final Paint track = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 10
      ..color = AppColors.borderSubtle;
    canvas.drawCircle(center, radius, track);

    final Paint progress = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 10
      ..strokeCap = StrokeCap.round
      ..color = AppColors.primaryMaroon;
    canvas.drawArc(ring, -1.5708, fraction * 6.2832, false, progress);
  }

  @override
  bool shouldRepaint(_RingPainter oldDelegate) =>
      oldDelegate.fraction != fraction;
}
