import 'package:flutter/material.dart';

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

  @override
  Widget build(BuildContext context) {
    return StepScaffold(
      stepNumber: stepNumber,
      totalSteps: 5,
      ctaLabel: ctaLabel,
      onCta: null,
      onBack: () => Navigator.of(context).maybePop(),
      child: Container(
        margin: const EdgeInsets.only(top: 12),
        padding: const EdgeInsets.all(16),
        decoration: const BoxDecoration(
          color: Colors.white,
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
              onTap: () => Navigator.of(context).maybePop(),
            ),
          ],
        ),
      ),
    );
  }
}
