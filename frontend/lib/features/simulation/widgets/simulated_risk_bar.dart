import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/widgets/gradient_cta_button.dart';

/// Bottom result and action card of the lifestyle simulation.
///
/// It displays the simulated risk next to the delta pill and the
/// "Save Action Plan" call to action.
class SimulatedRiskBar extends StatelessWidget {
  const SimulatedRiskBar({
    super.key,
    required this.simulatedRisk,
    required this.deltaLabel,
    required this.hasDelta,
    required this.onSave,
  });

  /// The projected risk, out of 100.
  final int simulatedRisk;

  /// Label of the delta pill, e.g. `11 points lower`.
  final String deltaLabel;

  /// Whether the changes moved the risk.
  final bool hasDelta;

  /// Saves the action plan (wired by the screen).
  final VoidCallback onSave;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 20),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(
          color: AppColors.borderSubtle,
          width: 1.5,
        ),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.textPrimary.withValues(alpha: 0.05),
            offset: const Offset(0, 2),
            blurRadius: 8,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          ConstrainedBox(
            constraints: const BoxConstraints(minHeight: 56),
            child: Row(
              children: <Widget>[
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      Text(
                        'Simulated Risk',
                        style: AppTextStyles.simulationBarLabel,
                      ),
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.baseline,
                        textBaseline: TextBaseline.alphabetic,
                        children: <Widget>[
                          Text(
                            '$simulatedRisk',
                            style: AppTextStyles.simulationBarValue,
                          ),
                          const SizedBox(width: 6),
                          Text(
                            'out of 100',
                            style: AppTextStyles.simulationBarUnit,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                _DeltaPill(label: deltaLabel, hasDelta: hasDelta),
              ],
            ),
          ),
          const SizedBox(height: 12),
          GradientCtaButton(
            label: 'Save Action Plan',
            onPressed: onSave,
            height: 56,
          ),
        ],
      ),
    );
  }
}

/// Pill showing how many points the changes removed.
class _DeltaPill extends StatelessWidget {
  const _DeltaPill({required this.label, required this.hasDelta});

  final String label;

  /// Whether the pill shows the positive state.
  final bool hasDelta;

  @override
  Widget build(BuildContext context) {
    final TextStyle labelStyle = hasDelta
        ? AppTextStyles.simulationDeltaLabel
        : AppTextStyles.simulationDeltaLabel.copyWith(
            color: AppColors.textMuted,
          );

    return Container(
      height: 34,
      padding: const EdgeInsets.symmetric(horizontal: 14),
      decoration: BoxDecoration(
        color: hasDelta
            ? AppColors.refDeltaSurface
            : AppColors.refPillSurfaceIdle,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(
          color: hasDelta
              ? AppColors.refAutosaveCircle
              : AppColors.refPillBorderIdle,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          if (hasDelta) ...<Widget>[
            const CustomPaint(
              size: Size(14, 14),
              painter: _TrendArrowPainter(),
            ),
            const SizedBox(width: 6),
          ],
          Text(label, style: labelStyle),
        ],
      ),
    );
  }
}

/// Downward trend arrow of the delta pill.
class _TrendArrowPainter extends CustomPainter {
  const _TrendArrowPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final Paint paint = Paint()
      ..color = AppColors.refAutosaveTick
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final Path shaft = Path()
      ..moveTo(7, 2)
      ..lineTo(7, 11.5);

    final Path head = Path()
      ..moveTo(3, 7.8)
      ..lineTo(7, 11.8)
      ..lineTo(11, 7.8);

    canvas.drawPath(shaft, paint);
    canvas.drawPath(head, paint);
  }

  @override
  bool shouldRepaint(_TrendArrowPainter oldDelegate) => false;
}
