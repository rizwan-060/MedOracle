import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:medoracle/core/theme/app_colors.dart';
import 'package:medoracle/core/theme/app_text_styles.dart';

/// Gauge showing where the risk sits today and where it is heading.
class RiskTrajectoryDial extends StatelessWidget {
  const RiskTrajectoryDial({
    super.key,
    required this.levelLabel,
    required this.levelCaption,
    this.todayLabel = 'Today',
    this.projectionLabel = 'In 1 year',
    this.lowerLabel = 'Lower',
    this.higherLabel = 'Higher',
    this.todayAngle = 288,
    this.projectionAngle = 310.5,
  });

  /// Current risk level, e.g. `High`.
  final String levelLabel;

  /// Caption below the level, e.g. `your risk level today`.
  final String levelCaption;

  /// Label of the current position marker.
  final String todayLabel;

  /// Label of the projected position marker.
  final String projectionLabel;

  /// Label of the low end of the gauge.
  final String lowerLabel;

  /// Label of the high end of the gauge.
  final String higherLabel;

  /// Angle (degrees) of the current position.
  final double todayAngle;

  /// Angle (degrees) of the projected position.
  final double projectionAngle;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (BuildContext context, BoxConstraints constraints) {
        final double scale = constraints.maxWidth / 350;
        return SizedBox(
          width: constraints.maxWidth,
          height: 222 * scale,
          child: CustomPaint(
            painter: RiskTrajectoryDialPainter(
              scale: scale,
              levelLabel: levelLabel,
              levelCaption: levelCaption,
              todayLabel: todayLabel,
              projectionLabel: projectionLabel,
              lowerLabel: lowerLabel,
              higherLabel: higherLabel,
              todayAngle: todayAngle,
              projectionAngle: projectionAngle,
              levelStyle: AppTextStyles.resultsHeadline.copyWith(
                fontSize: 46,
                height: 1.05,
                letterSpacing: -1,
              ),
              captionStyle: AppTextStyles.metricLabel,
              markerStyle: AppTextStyles.chipLabel.copyWith(
                fontWeight: FontWeight.w800,
              ),
              axisStyle: AppTextStyles.statLabel,
            ),
          ),
        );
      },
    );
  }
}

/// Paints the risk gauge: four risk bands, the trajectory arc and the two
/// position markers.
class RiskTrajectoryDialPainter extends CustomPainter {
  const RiskTrajectoryDialPainter({
    required this.scale,
    required this.levelLabel,
    required this.levelCaption,
    required this.todayLabel,
    required this.projectionLabel,
    required this.lowerLabel,
    required this.higherLabel,
    required this.todayAngle,
    required this.projectionAngle,
    required this.levelStyle,
    required this.captionStyle,
    required this.markerStyle,
    required this.axisStyle,
  });

  /// Scale factor between the design canvas (350 x 222) and the widget.
  final double scale;

  /// Current risk level.
  final String levelLabel;

  /// Caption below the level.
  final String levelCaption;

  /// Label of the current position marker.
  final String todayLabel;

  /// Label of the projected position marker.
  final String projectionLabel;

  /// Label of the low end of the gauge.
  final String lowerLabel;

  /// Label of the high end of the gauge.
  final String higherLabel;

  /// Angle (degrees) of the current position.
  final double todayAngle;

  /// Angle (degrees) of the projected position.
  final double projectionAngle;

  /// Style of the big level label.
  final TextStyle levelStyle;

  /// Style of the level caption.
  final TextStyle captionStyle;

  /// Style of the marker labels.
  final TextStyle markerStyle;

  /// Style of the axis labels.
  final TextStyle axisStyle;

  /// Risk bands, ordered from low to high risk.
  static const List<_RiskBand> _bands = <_RiskBand>[
    _RiskBand(start: 180, end: 225, color: AppColors.mutedGreen),
    _RiskBand(start: 225, end: 270, color: AppColors.amberWarning),
    _RiskBand(start: 270, end: 315, color: AppColors.primaryMaroon),
    _RiskBand(start: 315, end: 360, color: AppColors.maroonDark),
  ];

  @override
  void paint(Canvas canvas, Size size) {
    final double s = scale;
    final Offset center = Offset(175 * s, 190 * s);
    final double radius = 130 * s;
    final Rect arcRect = Rect.fromCircle(center: center, radius: radius);

    final Paint bandPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 26 * s
      ..strokeCap = StrokeCap.butt;

    for (final _RiskBand band in _bands) {
      bandPaint.color = band.color;
      canvas.drawArc(
        arcRect,
        band.start * math.pi / 180,
        (band.end - band.start) * math.pi / 180,
        false,
        bandPaint,
      );
    }

    // Dashed trajectory between the current and the projected position.
    final double todayRad = todayAngle * math.pi / 180;
    final double projectionRad = projectionAngle * math.pi / 180;
    final Path trajectory = Path()
      ..arcTo(
        arcRect,
        todayRad,
        projectionRad - todayRad,
        false,
      );
    _drawDashedPath(
      canvas,
      trajectory,
      Paint()
        ..color = AppColors.cardSurface
        ..style = PaintingStyle.stroke
        ..strokeWidth = 4 * s
        ..strokeCap = StrokeCap.round,
      dashLength: 0.1 * s,
      gapLength: 9 * s,
    );

    // Current position marker - white disc with a maroon ring so that it
    // stays readable on the maroon "high risk" band.
    final Offset todayPoint = _pointOnCircle(center, radius, todayRad);
    canvas.drawCircle(todayPoint, 12 * s, Paint()..color = AppColors.cardSurface);
    canvas.drawCircle(
      todayPoint,
      12 * s,
      Paint()
        ..color = AppColors.primaryMaroon
        ..style = PaintingStyle.stroke
        ..strokeWidth = 4 * s,
    );

    // Projected position marker - white disc with a dashed maroon ring.
    final Offset projectionPoint =
        _pointOnCircle(center, radius, projectionRad);
    canvas.drawCircle(projectionPoint, 11 * s, Paint()..color = AppColors.cardSurface);
    _drawDashedPath(
      canvas,
      Path()
        ..addOval(Rect.fromCircle(center: projectionPoint, radius: 11 * s)),
      Paint()
        ..color = AppColors.primaryMaroon
        ..style = PaintingStyle.stroke
        ..strokeWidth = 3 * s,
      dashLength: 4 * s,
      gapLength: 3 * s,
    );

    _drawText(canvas, todayLabel, 226 * s, 30 * s, markerStyle);
    _drawText(canvas, projectionLabel, 300 * s, 64 * s, markerStyle);
    _drawText(canvas, levelLabel, 175 * s, 166 * s, levelStyle);
    _drawText(canvas, levelCaption, 175 * s, 188 * s, captionStyle);
    _drawText(canvas, lowerLabel, 45 * s, 214 * s, axisStyle);
    _drawText(canvas, higherLabel, 305 * s, 214 * s, axisStyle);
  }

  Offset _pointOnCircle(Offset center, double radius, double angle) {
    return Offset(
      center.dx + (radius * math.cos(angle)),
      center.dy + (radius * math.sin(angle)),
    );
  }

  void _drawDashedPath(
    Canvas canvas,
    Path path,
    Paint paint, {
    required double dashLength,
    required double gapLength,
  }) {
    for (final metric in path.computeMetrics()) {
      double distance = 0;
      while (distance < metric.length) {
        final double end = math.min(distance + dashLength, metric.length);
        canvas.drawPath(metric.extractPath(distance, end), paint);
        distance = end + gapLength;
      }
    }
  }

  void _drawText(
    Canvas canvas,
    String text,
    double x,
    double y,
    TextStyle style,
  ) {
    final TextPainter painter = TextPainter(
      text: TextSpan(text: text, style: style),
      textDirection: TextDirection.ltr,
    )..layout();
    final List<LineMetrics> metrics = painter.computeLineMetrics();
    final double baseline = metrics.isEmpty ? painter.height : metrics.first.baseline;
    painter.paint(canvas, Offset(x - (painter.width / 2), y - baseline));
    painter.dispose();
  }

  @override
  bool shouldRepaint(covariant RiskTrajectoryDialPainter oldDelegate) =>
      oldDelegate.scale != scale ||
      oldDelegate.levelLabel != levelLabel ||
      oldDelegate.todayAngle != todayAngle ||
      oldDelegate.projectionAngle != projectionAngle;
}

/// One coloured band of the gauge.
class _RiskBand {
  const _RiskBand({
    required this.start,
    required this.end,
    required this.color,
  });

  /// Start angle in degrees.
  final double start;

  /// End angle in degrees.
  final double end;

  /// Band colour.
  final Color color;
}
