import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:medoracle/core/theme/app_colors.dart';
import 'package:medoracle/core/theme/app_text_styles.dart';

/// Amber callout that surfaces the doubt the models raised.
class DoubtRaisedCard extends StatelessWidget {
  const DoubtRaisedCard({
    super.key,
    required this.message,
    this.label = 'DOUBT RAISED',
  });

  /// The doubt, e.g. `Could this just be muscle strain?`.
  final String message;

  /// Uppercase label of the callout.
  final String label;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: <Widget>[
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          decoration: BoxDecoration(
            color: AppColors.amberSurface,
            borderRadius: BorderRadius.circular(14),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Row(
                children: <Widget>[
                  Container(
                    width: 20,
                    height: 20,
                    alignment: Alignment.center,
                    decoration: const BoxDecoration(
                      color: AppColors.amberWarning,
                      shape: BoxShape.circle,
                    ),
                    child: const Text(
                      '?',
                      style: TextStyle(
                        fontFamily: AppTextStyles.fontFamily,
                        fontSize: 12,
                        height: 1.2,
                        fontWeight: FontWeight.w800,
                        color: AppColors.cardSurface,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      label,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: AppTextStyles.eyebrow.copyWith(
                        color: AppColors.refInk,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(message, style: AppTextStyles.bodyEmphasis),
            ],
          ),
        ),
        Positioned.fill(
          child: IgnorePointer(
            child: CustomPaint(
              painter: const DashedBorderPainter(
                radius: 14,
                color: AppColors.amberWarning,
                strokeWidth: 1.5,
              ),
            ),
          ),
        ),
      ],
    );
  }
}

/// Green callout explaining why the doubt was ruled out.
class RuledOutCard extends StatelessWidget {
  const RuledOutCard({
    super.key,
    required this.message,
    this.highlights = const <String>[],
    this.label = 'WHY IT WAS RULED OUT',
  });

  /// Explanation of the ruling.
  final String message;

  /// Supporting evidence, e.g. `BP 146`.
  final List<String> highlights;

  /// Uppercase label of the callout.
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: AppColors.greenSurface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.mutedGreen, width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Row(
            children: <Widget>[
              Container(
                width: 20,
                height: 20,
                alignment: Alignment.center,
                decoration: const BoxDecoration(
                  color: AppColors.mutedGreen,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.check_rounded,
                  size: 13,
                  color: AppColors.cardSurface,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: AppTextStyles.eyebrow.copyWith(
                    color: AppColors.mutedGreen,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(message, style: AppTextStyles.bodyEmphasis),
          if (highlights.isNotEmpty) ...<Widget>[
            const SizedBox(height: 10),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: <Widget>[
                for (final String highlight in highlights)
                  _EvidenceChip(label: highlight),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

/// Small green outlined chip holding a piece of evidence.
class _EvidenceChip extends StatelessWidget {
  const _EvidenceChip({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.mutedGreen),
      ),
      child: Text(
        label,
        style: AppTextStyles.chipLabel.copyWith(
          color: AppColors.mutedGreen,
        ),
      ),
    );
  }
}

/// Arrow pointing from the doubt to the ruling.
class VerticalFlowArrow extends StatelessWidget {
  const VerticalFlowArrow({super.key});

  @override
  Widget build(BuildContext context) {
    return const SizedBox(
      height: 30,
      width: 20,
      child: CustomPaint(painter: _FlowArrowPainter()),
    );
  }
}

class _FlowArrowPainter extends CustomPainter {
  const _FlowArrowPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final Paint paint = Paint()
      ..color = AppColors.dustyTaupe
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.8
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final double centerX = size.width / 2;
    canvas.drawLine(Offset(centerX, 3), Offset(centerX, 24), paint);
    canvas.drawPath(
      Path()
        ..moveTo(centerX - 4.5, 19.5)
        ..lineTo(centerX, 25)
        ..lineTo(centerX + 4.5, 19.5),
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant _FlowArrowPainter oldDelegate) => false;
}

/// Paints a dashed rounded rectangle.
class DashedBorderPainter extends CustomPainter {
  const DashedBorderPainter({
    required this.radius,
    required this.color,
    required this.strokeWidth,
    this.dashLength = 6,
    this.gapLength = 4,
  });

  /// Corner radius of the dashed outline.
  final double radius;

  /// Colour of the dashes.
  final Color color;

  /// Width of the dashes.
  final double strokeWidth;

  /// Length of a single dash.
  final double dashLength;

  /// Gap between two dashes.
  final double gapLength;

  @override
  void paint(Canvas canvas, Size size) {
    final Rect rect = Offset.zero & size;
    final Path path = Path()
      ..addRRect(
        RRect.fromRectAndRadius(
          rect.deflate(strokeWidth / 2),
          Radius.circular(radius),
        ),
      );

    final Paint paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.butt;

    for (final metric in path.computeMetrics()) {
      double distance = 0;
      while (distance < metric.length) {
        final double end = math.min(distance + dashLength, metric.length);
        canvas.drawPath(metric.extractPath(distance, end), paint);
        distance = end + gapLength;
      }
    }
  }

  @override
  bool shouldRepaint(covariant DashedBorderPainter oldDelegate) =>
      oldDelegate.color != color ||
      oldDelegate.radius != radius ||
      oldDelegate.strokeWidth != strokeWidth;
}
