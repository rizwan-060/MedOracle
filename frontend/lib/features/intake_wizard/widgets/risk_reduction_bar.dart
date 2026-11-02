import 'package:flutter/material.dart';
import 'package:medoracle/core/theme/app_colors.dart';
import 'package:medoracle/core/theme/app_text_styles.dart';

/// Two tone bar showing how much of the risk stays and how much is removed.
class RiskReductionBar extends StatelessWidget {
  const RiskReductionBar({
    super.key,
    required this.affectedFraction,
    required this.improvementFraction,
    this.compact = false,
  });

  /// Share of the bar that stays affected.
  final double affectedFraction;

  /// Share of the bar that drops below the "no change" projection.
  final double improvementFraction;

  /// Renders a thinner bar for the side by side cards.
  final bool compact;

  @override
  Widget build(BuildContext context) {
    const int precision = 1000;
    final int affected = (affectedFraction * precision).round();
    final int improvement = (improvementFraction * precision).round();
    final int remaining = (precision - affected - improvement).clamp(0, precision);

    return ClipRRect(
      borderRadius: BorderRadius.circular(999),
      child: Container(
        height: compact ? 10 : 14,
        color: AppColors.dustyTaupe.withValues(alpha: 0.35),
        child: Row(
          children: <Widget>[
            if (affected > 0)
              Expanded(
                flex: affected,
                child: const ColoredBox(color: AppColors.primaryMaroon),
              ),
            if (improvement > 0)
              Expanded(
                flex: improvement,
                child: const ColoredBox(color: AppColors.mutedGreen),
              ),
            if (remaining > 0)
              Expanded(flex: remaining, child: const SizedBox.shrink()),
          ],
        ),
      ),
    );
  }
}

/// Legend entry for [RiskReductionBar].
class RiskReductionLegend extends StatelessWidget {
  const RiskReductionLegend({
    super.key,
    required this.affectedLabel,
    required this.improvementLabel,
  });

  /// Description of the maroon segment.
  final String affectedLabel;

  /// Description of the green segment.
  final String improvementLabel;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      alignment: WrapAlignment.center,
      spacing: 16,
      runSpacing: 8,
      children: <Widget>[
        _LegendEntry(color: AppColors.primaryMaroon, label: affectedLabel),
        _LegendEntry(color: AppColors.mutedGreen, label: improvementLabel),
      ],
    );
  }
}

class _LegendEntry extends StatelessWidget {
  const _LegendEntry({required this.color, required this.label});

  final Color color;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 6),
        Flexible(
          child: Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: AppTextStyles.finePrint,
          ),
        ),
      ],
    );
  }
}
