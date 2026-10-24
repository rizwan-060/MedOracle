import 'package:flutter/material.dart';
import 'package:medoracle/core/theme/app_colors.dart';
import 'package:medoracle/core/theme/app_text_styles.dart';
import 'package:medoracle/core/widgets/disclaimer_text.dart';
import 'package:medoracle/core/widgets/glass_pill_button.dart';
import 'package:medoracle/features/intake_wizard/models/assessment_data.dart';
import 'package:medoracle/features/intake_wizard/widgets/risk_action_card.dart';
import 'package:medoracle/features/intake_wizard/widgets/risk_reduction_bar.dart';
import 'package:medoracle/features/intake_wizard/widgets/risk_trajectory_dial.dart';

// Added import for the AssessmentHeader
import 'package:medoracle/features/assessment/widgets/assessment_header.dart';

/// Risk trajectory screen of the intake flow.
///
/// Shows where the risk sits today, where it is heading and which behaviour
/// changes move it back down.
class RiskTrajectoryScreen extends StatelessWidget {
  const RiskTrajectoryScreen({
    super.key,
    this.onPrimaryAction,
    this.onSecondaryAction,
    this.onClose,
    this.levelLabel = 'High',
    this.levelCaption = 'your risk level today',
    this.todayValue = '24',
    this.projectedValue = '29',
    this.actions = AssessmentDemoData.actions,
  });

  /// Optional action hook.
  final VoidCallback? onPrimaryAction;

  /// Wired to the return button - go back to the results
  /// (`RouteNames.resultsReports`).
  final VoidCallback? onSecondaryAction;

  /// Wired to the close button (`RouteNames.resultsReports`).
  final VoidCallback? onClose;

  /// Current risk level shown in the middle of the gauge.
  final String levelLabel;

  /// Caption below the current risk level.
  final String levelCaption;

  /// Risk per 100 people today.
  final String todayValue;

  /// Risk per 100 people in one year if nothing changes.
  final String projectedValue;

  /// Behaviour changes ordered by how much they help.
  final List<RiskReductionAction> actions;

  void _placeholder(BuildContext context, String destination) {
    debugPrint(
      '[MedOracle] TODO: route to "$destination" from RiskTrajectoryScreen.',
    );
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('TODO: route to $destination')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.refCanvasBottom,
      body: DecoratedBox(
        decoration: const BoxDecoration(gradient: AppColors.canvasGradient),
        child: SafeArea(
          bottom: false,
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(0, 0, 0, 28),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                AssessmentHeader(
                  onClose:
                      onClose ?? () => _placeholder(context, 'close'),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: <Widget>[
                      const SizedBox(height: 18),
                      const Text(
                        'NEXT 12 MONTHS',
                        style: AppTextStyles.eyebrow,
                      ),
                      const SizedBox(height: 6),
                      const Text(
                        'Your heart risk is rising',
                        style: AppTextStyles.resultsHeadline,
                      ),
                      const SizedBox(height: 16),
                      RiskTrajectoryDial(
                        levelLabel: levelLabel,
                        levelCaption: levelCaption,
                      ),
                      const SizedBox(height: 14),
                      const Text(
                        'People like you who have a heart attack or stroke within '
                        '10 years',
                        textAlign: TextAlign.center,
                        style: AppTextStyles.metricLabel,
                      ),
                      const SizedBox(height: 18),
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: <Widget>[
                          Expanded(
                            child: _RiskMetric(
                              value: todayValue,
                              label: 'out of 100',
                              caption: 'today',
                            ),
                          ),
                          Container(
                            width: 1,
                            height: 44,
                            color: AppColors.borderSubtle,
                          ),
                          Expanded(
                            child: _RiskMetric(
                              value: projectedValue,
                              label: 'out of 100',
                              caption: 'in 1 year, if nothing changes',
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 22),
                      const Text(
                        'WHAT HELPS MOST',
                        style: AppTextStyles.eyebrow,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Your $projectedValue out of 100 goes down when you '
                        'make these changes',
                        style: AppTextStyles.metricLabel,
                      ),
                      const SizedBox(height: 12),
                      if (actions.isNotEmpty)
                        RiskActionCard(action: actions.first),
                      if (actions.length > 1) ...<Widget>[
                        const SizedBox(height: 10),
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: <Widget>[
                            for (int index = 1; index < actions.length; index++)
                              Expanded(
                                child: Padding(
                                  padding: EdgeInsets.only(
                                    right: index == actions.length - 1
                                        ? 0
                                        : 10,
                                  ),
                                  child: RiskActionCard(
                                    action: actions[index],
                                    compact: true,
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ],
                      const SizedBox(height: 16),
                      const RiskReductionLegend(
                        affectedLabel: 'still affected',
                        improvementLabel: 'fewer than if nothing changes',
                      ),
                      const SizedBox(height: 14),
                      const DisclaimerText(),
                      const SizedBox(height: 20),
                      GlassPillButton.footer(
                        label: 'Back to results',
                        onTap: onSecondaryAction ??
                            () => _placeholder(context, 'results'),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// One of the two headline risk numbers.
class _RiskMetric extends StatelessWidget {
  const _RiskMetric({
    required this.value,
    required this.label,
    required this.caption,
  });

  final String value;
  final String label;
  final String caption;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Row(
          crossAxisAlignment: CrossAxisAlignment.baseline,
          textBaseline: TextBaseline.alphabetic,
          children: <Widget>[
            Text(value, style: AppTextStyles.metricValue),
            const SizedBox(width: 6),
            Flexible(
              child: Text(
                label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: AppTextStyles.metricLabel,
              ),
            ),
          ],
        ),
        Text(caption, style: AppTextStyles.metricLabel),
      ],
    );
  }
}