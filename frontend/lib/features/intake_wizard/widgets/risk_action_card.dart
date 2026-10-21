import 'package:flutter/material.dart';
import 'package:medoracle/core/theme/app_colors.dart';
import 'package:medoracle/core/theme/app_text_styles.dart';
import 'package:medoracle/features/intake_wizard/models/assessment_data.dart';
import 'package:medoracle/features/intake_wizard/widgets/risk_reduction_bar.dart';

/// Card describing one behaviour change and the risk it removes.
class RiskActionCard extends StatelessWidget {
  const RiskActionCard({
    super.key,
    required this.action,
    this.compact = false,
  });

  /// The behaviour change and its projected impact.
  final RiskReductionAction action;

  /// Renders the tighter variant used by the side by side cards.
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(compact ? 12 : 16),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.refCardRing),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.refCardShadow,
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            action.title,
            style: AppTextStyles.chipLabel.copyWith(
              fontSize: compact ? 14 : 15,
              fontWeight: FontWeight.w700,
            ),
          ),
          SizedBox(height: compact ? 10 : 12),
          RiskReductionBar(
            affectedFraction: action.affectedFraction,
            improvementFraction: action.improvementFraction,
            compact: compact,
          ),
          SizedBox(height: compact ? 10 : 12),
          Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: <Widget>[
              Text(
                action.value,
                style: AppTextStyles.statValue.copyWith(
                  fontSize: 20,
                  height: 26 / 20,
                ),
              ),
              const SizedBox(width: 6),
              const Flexible(
                child: Text(
                  'out of 100',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: AppTextStyles.metricLabel,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
