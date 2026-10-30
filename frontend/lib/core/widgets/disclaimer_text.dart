import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

/// Standard footnotes shown beneath clinical results and data-entry steps.
class DisclaimerText extends StatelessWidget {
  const DisclaimerText({super.key, this.message});

  /// Overrides the default decision-support wording.
  final String? message;

  /// Default non-diagnostic statement required on clinical surfaces.
  static const String defaultMessage =
      'These are estimates, not predictions. MedOracle decision support '
      'only; does not provide diagnosis.';

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 16),
      child: Text(
        message ?? defaultMessage,
        style: AppTextStyles.helperText.copyWith(color: AppColors.textMuted),
      ),
    );
  }
}
