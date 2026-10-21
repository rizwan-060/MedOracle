import 'package:flutter/material.dart';
import 'package:medoracle/core/theme/app_colors.dart';
import 'package:medoracle/core/theme/app_text_styles.dart';
import 'package:medoracle/features/intake_wizard/models/assessment_data.dart';

/// Visual reasoning map: patient details flow into the specialist models and
/// converge on the final conclusion.
class ReasoningMapChart extends StatelessWidget {
  const ReasoningMapChart({
    super.key,
    required this.facts,
    required this.models,
    required this.resultTitle,
    required this.resultConfidence,
  });

  /// Patient details that were taken into account.
  final List<ReasoningFact> facts;

  /// Specialist models that reviewed the details.
  final List<ReasoningModel> models;

  /// Name of the conclusion.
  final String resultTitle;

  /// Confidence of the conclusion.
  final String resultConfidence;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (BuildContext context, BoxConstraints constraints) {
        final double width = constraints.maxWidth;
        const double gap = 8;
        final int columns = facts.length > models.length ? facts.length : models.length;
        final double columnWidth = (width - (gap * (columns - 1))) / columns;
        final List<double> centers = <double>[
          for (int index = 0; index < columns; index++)
            (index * (columnWidth + gap)) + (columnWidth / 2),
        ];

        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            IntrinsicHeight(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: <Widget>[
                  for (int index = 0; index < facts.length; index++)
                    Expanded(
                      child: Padding(
                        padding: EdgeInsets.only(
                          right: index == facts.length - 1 ? 0 : gap,
                        ),
                        child: _FactChip(label: facts[index].label),
                      ),
                    ),
                ],
              ),
            ),
            SizedBox(
              height: 28,
              child: CustomPaint(
                painter: _DropArrowsPainter(centers),
              ),
            ),
            IntrinsicHeight(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: <Widget>[
                  for (int index = 0; index < models.length; index++)
                    Expanded(
                      child: Padding(
                        padding: EdgeInsets.only(
                          right: index == models.length - 1 ? 0 : gap,
                        ),
                        child: _ModelChip(model: models[index]),
                      ),
                    ),
                ],
              ),
            ),
            SizedBox(
              height: 34,
              child: CustomPaint(
                painter: _ConvergeArrowsPainter(centers),
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              decoration: BoxDecoration(
                gradient: AppColors.ctaGradient,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Column(
                children: <Widget>[
                  Text(
                    resultTitle,
                    textAlign: TextAlign.center,
                    style: AppTextStyles.resultBarTitle,
                  ),
                  const SizedBox(height: 2),
                  Text(
                    resultConfidence,
                    textAlign: TextAlign.center,
                    style: AppTextStyles.resultBarConfidence,
                  ),
                ],
              ),
            ),
          ],
        );
      },
    );
  }
}

/// One patient detail inside the top row of the map.
class _FactChip extends StatelessWidget {
  const _FactChip({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: const BoxConstraints(minHeight: 60),
      alignment: Alignment.center,
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.canvasBackground,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.refGlowB),
      ),
      child: Text(
        label,
        textAlign: TextAlign.center,
        style: AppTextStyles.fieldLabel,
      ),
    );
  }
}

/// One specialist model inside the middle row of the map.
class _ModelChip extends StatelessWidget {
  const _ModelChip({required this.model});

  final ReasoningModel model;

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: const BoxConstraints(minHeight: 56),
      alignment: Alignment.center,
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.refCardRing, width: 1.5),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Text(
            model.name,
            textAlign: TextAlign.center,
            style: AppTextStyles.chipLabel.copyWith(
              fontWeight: FontWeight.w800,
            ),
          ),
          if (model.confidence != null)
            Text(
              '${model.confidence}%',
              textAlign: TextAlign.center,
              style: AppTextStyles.chipLabel.copyWith(
                color: AppColors.refSubtitle,
              ),
            ),
        ],
      ),
    );
  }
}

/// Straight arrows dropping from the facts into the models.
class _DropArrowsPainter extends CustomPainter {
  const _DropArrowsPainter(this.centers);

  final List<double> centers;

  @override
  void paint(Canvas canvas, Size size) {
    final Paint paint = Paint()
      ..color = AppColors.dustyTaupe
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.6
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    for (final double center in centers) {
      canvas.drawLine(Offset(center, 2), Offset(center, 23), paint);
      canvas.drawPath(
        Path()
          ..moveTo(center - 3.5, 19)
          ..lineTo(center, 25)
          ..lineTo(center + 3.5, 19),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _DropArrowsPainter oldDelegate) =>
      oldDelegate.centers != centers;
}

/// Arrows converging from the models onto the conclusion.
class _ConvergeArrowsPainter extends CustomPainter {
  const _ConvergeArrowsPainter(this.centers);

  final List<double> centers;

  @override
  void paint(Canvas canvas, Size size) {
    final Paint paint = Paint()
      ..color = AppColors.dustyTaupe
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.6
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final double middle = size.width / 2;
    const double spread = 54;

    for (int index = 0; index < centers.length; index++) {
      final double startX = centers[index];
      final double endX = middle + ((index - 1) * spread);
      canvas.drawLine(Offset(startX, 2), Offset(endX, 29), paint);

      if (index == 1) {
        canvas.drawPath(
          Path()
            ..moveTo(endX - 3.5, 23)
            ..lineTo(endX, 30)
            ..lineTo(endX + 3.5, 23),
          paint,
        );
      } else if (index == 0) {
        canvas.drawPath(
          Path()
            ..moveTo(endX - 7.8, 29.7)
            ..lineTo(endX, 30)
            ..lineTo(endX - 4.5, 23.6),
          paint,
        );
      } else {
        canvas.drawPath(
          Path()
            ..moveTo(endX + 7.8, 29.7)
            ..lineTo(endX, 30)
            ..lineTo(endX + 4.5, 23.6),
          paint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant _ConvergeArrowsPainter oldDelegate) =>
      oldDelegate.centers != centers;
}
