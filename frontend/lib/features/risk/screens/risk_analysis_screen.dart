import 'package:flutter/material.dart';
import 'package:medoracle/core/theme/app_colors.dart';
import 'package:medoracle/core/theme/app_text_styles.dart';
import 'package:medoracle/core/widgets/assessment_section_card.dart';
import 'package:medoracle/core/widgets/assessment_top_bar.dart';
import 'package:medoracle/core/widgets/disclaimer_text.dart';
import 'package:medoracle/core/widgets/glass_pill_button.dart';
import 'package:medoracle/core/widgets/gradient_cta_button.dart';

/// Results overview - the landing screen of the results flow.
///
/// Shows the headline risk and the two doors into the rest of the assessment:
/// the reasoning behind the number and the trajectory it is heading towards.
///
/// The screen is intentionally light on content: the design frame for this
/// step (Step 6A of the intake flow) is still to be translated, so the cards
/// reuse the shared assessment chrome.
class RiskAnalysisScreen extends StatelessWidget {
  const RiskAnalysisScreen({
    super.key,
    this.onReasoningAction,
    this.onTrajectoryAction,
    this.onClose,
    this.levelLabel = 'High',
    this.todayValue = '24',
  });

  /// Opens the "how our AI reached this result" screen.
  final VoidCallback? onReasoningAction;

  /// Opens the risk trajectory screen.
  final VoidCallback? onTrajectoryAction;

  /// Leaves the results flow (usually back to the intake review step).
  final VoidCallback? onClose;

  /// Current risk level.
  final String levelLabel;

  /// Risk per 100 people today.
  final String todayValue;

  void _placeholder(BuildContext context, String destination) {
    debugPrint(
      '[MedOracle] TODO: route to "$destination" from RiskAnalysisScreen.',
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
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(20, 0, 20, 28),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                AssessmentTopBar(
                  onClose: onClose ?? () => _placeholder(context, 'close'),
                ),
                const SizedBox(height: 18),
                const Text('YOUR RESULT', style: AppTextStyles.eyebrow),
                const SizedBox(height: 8),
                const Text(
                  'Your heart risk is high',
                  style: AppTextStyles.resultsHeadline,
                ),
                const SizedBox(height: 10),
                Text(
                  '$todayValue out of 100 people like you have a heart attack '
                  'or stroke within the next 10 years.',
                  style: AppTextStyles.resultsBody,
                ),
                const SizedBox(height: 22),
                AssessmentSectionCard(
                  stepNumber: '1',
                  title: 'Your 10 year risk',
                  subtitle: 'Where you stand today',
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: <Widget>[
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.baseline,
                        textBaseline: TextBaseline.alphabetic,
                        children: <Widget>[
                          Text(todayValue, style: AppTextStyles.metricValue),
                          const SizedBox(width: 6),
                          const Text(
                            'out of 100',
                            style: AppTextStyles.metricLabel,
                          ),
                          const Spacer(),
                          _LevelBadge(label: levelLabel),
                        ],
                      ),
                      const SizedBox(height: 14),
                      const Text(
                        'People like you who have a heart attack or stroke '
                        'within 10 years',
                        style: AppTextStyles.helperText,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                const DisclaimerText(),
                const SizedBox(height: 16),
                GradientCtaButton(
                  label: 'How we reached this result',
                  onPressed: onReasoningAction ??
                      () => _placeholder(context, 'reasoning'),
                ),
                const SizedBox(height: 10),
                GlassPillButton.footer(
                  label: 'View risk trajectory',
                  onTap: onTrajectoryAction ??
                      () => _placeholder(context, 'risk trajectory'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Pill showing the risk level of the result.
class _LevelBadge extends StatelessWidget {
  const _LevelBadge({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.amberSurface,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.amberWarning, width: 1.5),
      ),
      child: Text(
        label,
        style: AppTextStyles.chipLabel.copyWith(
          color: AppColors.amberWarning,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}
