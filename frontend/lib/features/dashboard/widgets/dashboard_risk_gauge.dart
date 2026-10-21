import 'dart:math' show pi;

import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// Semicircular risk gauge of the dashboard hero metric card.
///
/// The gauge renders the score as a filled arc over a muted track, with the
/// value centred inside the arc and the 0 - 100 scale underneath.
class DashboardRiskGauge extends StatelessWidget {
  const DashboardRiskGauge({super.key, required this.score});

  /// Risk score between 0 and 100.
  final int score;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 280,
      height: 164,
      child: Stack(
        children: <Widget>[
          Positioned.fill(
            child: CustomPaint(painter: _RiskArcPainter(score: score)),
          ),
          Positioned(
            left: 0,
            right: 0,
            top: 73,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: <Widget>[
                Text(
                  '$score',
                  textAlign: TextAlign.center,
                  style: AppTextStyles.dashboardGaugeValue,
                ),
                Text(
                  'out of 100',
                  textAlign: TextAlign.center,
                  style: AppTextStyles.dashboardGaugeCaption.copyWith(
                    color: AppColors.onPlum.withValues(alpha: 0.82),
                  ),
                ),
              ],
            ),
          ),
          Positioned(
            left: 20,
            right: 10,
            bottom: 0,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                SizedBox(
                  width: 20,
                  child: Text(
                    '0',
                    textAlign: TextAlign.center,
                    style: AppTextStyles.dashboardGaugeScale.copyWith(
                      color: AppColors.onPlum.withValues(alpha: 0.82),
                    ),
                  ),
                ),
                SizedBox(
                  width: 40,
                  child: Text(
                    '100',
                    textAlign: TextAlign.center,
                    style: AppTextStyles.dashboardGaugeScale.copyWith(
                      color: AppColors.onPlum.withValues(alpha: 0.82),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// Paints the track and the value arc of the risk gauge.
class _RiskArcPainter extends CustomPainter {
  const _RiskArcPainter({required this.score});

  /// Risk score between 0 and 100.
  final int score;

  @override
  void paint(Canvas canvas, Size size) {
    final Offset centre = Offset(size.width / 2, 140);
    final Rect arc = Rect.fromCircle(center: centre, radius: 110);

    final Paint track = Paint()
      ..color = AppColors.onPlum.withValues(alpha: 0.16)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 16
      ..strokeCap = StrokeCap.round;
    canvas.drawArc(arc, pi, pi, false, track);

    final double sweep = pi * (score.clamp(0, 100) / 100);
    final Paint value = Paint()
      ..color = AppColors.amberSurface
      ..style = PaintingStyle.stroke
      ..strokeWidth = 16
      ..strokeCap = StrokeCap.round;
    canvas.drawArc(arc, pi, sweep, false, value);
  }

  @override
  bool shouldRepaint(covariant _RiskArcPainter oldDelegate) {
    return oldDelegate.score != score;
  }
}
