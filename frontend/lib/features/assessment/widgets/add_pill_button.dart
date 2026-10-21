import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/app_button.dart';

/// Rounded pill button used in card headers (e.g. "+ Add Surgery", "+ Add Allergy").
/// Delegates directly to the generic [AppButton] core widget.
class AddPillButton extends StatelessWidget {
  const AddPillButton({super.key, required this.label, this.onTap});

  final String label;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return AppButton(
      label: label,
      onTap: onTap,
      variant: AppButtonVariant.pill,
      height: 36,
      borderRadius: 999,
      borderColor: AppColors.dustyTaupe,
      textColor: AppColors.primaryMaroon,
      fontSize: 13,
      backgroundColor: AppColors.cardSurface.withValues(alpha: 0.55),
    );
  }
}
