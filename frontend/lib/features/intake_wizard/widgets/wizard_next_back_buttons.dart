import 'package:flutter/material.dart';

import '../../../core/widgets/app_button.dart';

/// Primary maroon gradient CTA used to advance the intake wizard.
/// Delegates directly to the generic [AppButton] core widget.
class GradientNextButton extends StatelessWidget {
  const GradientNextButton({super.key, required this.label, this.onTap});

  final String label;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return AppButton(
      label: label,
      onTap: onTap,
      variant: AppButtonVariant.gradient,
    );
  }
}

/// Text-style "Back" button that sits under the primary CTA.
/// Delegates directly to the generic [AppButton] core widget.
class BackTextButton extends StatelessWidget {
  const BackTextButton({super.key, this.onTap});

  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return AppButton(
      label: 'Back',
      onTap: onTap,
      variant: AppButtonVariant.text,
    );
  }
}
