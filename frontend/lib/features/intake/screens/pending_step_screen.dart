import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/widgets/glass_pill_button.dart';
import '../../../core/widgets/step_scaffold.dart';

/// Placeholder used by intake steps whose UI is scheduled for a later session.
///
/// Keeps the flow navigable (next/back) without shipping half-built screens.
class PendingStepScreen extends StatelessWidget {
  const PendingStepScreen({
    super.key,
    required this.stepNumber,
    required this.stepTitle,
    required this.ctaLabel,
    this.nextRoute,
  });

  final int stepNumber;
  final String stepTitle;
  final String ctaLabel;

  /// Route pushed when the user taps the CTA, or `null` on the last step.
  final String? nextRoute;

  /// Returns to the previous screen, falling back to Step 1 when the wizard
  /// was opened directly (deep link).
  void _goBack(BuildContext context) {
    if (context.canPop()) {
      context.pop();
      return;
    }
    context.go(RouteNames.step1Profile);
  }

  @override
  Widget build(BuildContext context) {
    return StepScaffold(
      stepNumber: stepNumber,
      totalSteps: 5,
      ctaLabel: ctaLabel,
      // The CTA advances the wizard; the last step hands over to the results
      // flow through `nextRoute`.
      onCta: nextRoute == null ? null : () => context.push(nextRoute!),
      onBack: () => _goBack(context),
      child: Container(
        margin: const EdgeInsets.only(top: 12),
        padding: const EdgeInsets.all(16),
        decoration: const BoxDecoration(
          color: AppColors.cardSurface,
          borderRadius: BorderRadius.all(Radius.circular(16)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Text('$stepNumber. $stepTitle',
                style: AppTextStyles.sectionTitle),
            const SizedBox(height: 6),
            Text(
              'This step is scheduled for an upcoming session.',
              style: AppTextStyles.helperText,
            ),
            const SizedBox(height: 12),
            GlassPillButton.footer(
              label: 'Back to Profile',
              onTap: () => _goBack(context),
            ),
          ],
        ),
      ),
    );
  }
}
