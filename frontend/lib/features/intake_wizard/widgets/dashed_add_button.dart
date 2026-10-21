import 'package:flutter/material.dart';

import '../../../core/widgets/app_button.dart';

/// Full-width dashed-outline button with a bold label (e.g. "+ Add Condition").
/// Delegates directly to the generic [AppButton] core widget.
class DashedAddButton extends StatelessWidget {
  const DashedAddButton({super.key, required this.label, this.onTap});

  final String label;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return AppButton(
      label: label,
      onTap: onTap,
      variant: AppButtonVariant.dashed,
    );
  }
}
