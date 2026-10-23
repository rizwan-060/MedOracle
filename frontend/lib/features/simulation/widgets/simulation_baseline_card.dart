import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// White card holding the user's current 1-year risk.
///
/// It is the anchor of the simulation: every slider below is read against
/// this baseline
/// (design: v8 Step 6C "Current 1-Year Risk" card).
class SimulationBaselineCard extends StatelessWidget {
  const SimulationBaselineCard({
    super.key,
    required this.label,
    required this.value,
    required this.unit,
  });

  /// Caption above the number, e.g. `Current 1-Year Risk`.
  final String label;

  /// The baseline risk, e.g. `29`.
  final String value;

  /// Unit next to the number, e.g. `out of 100`.
  final String unit;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 22),
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 20),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(
          color: AppColors.dustyTaupe.withValues(alpha: 0.45),
        ),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.primaryMaroon.withValues(alpha: 0.40),
            offset: const Offset(0, 14),
            blurRadius: 30,
            spreadRadius: -12,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Text(label, style: AppTextStyles.simulationBaselineLabel),
          const SizedBox(height: 4),
          Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: <Widget>[
              Text(value, style: AppTextStyles.simulationBaselineValue),
              const SizedBox(width: 8),
              Text(unit, style: AppTextStyles.simulationBaselineUnit),
            ],
          ),
        ],
      ),
    );
  }
}
