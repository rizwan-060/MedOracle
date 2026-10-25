import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Rounded "glass" pill button used in card headers
/// (e.g. "+ Add Surgery", "+ Add Allergy").
class AddPillButton extends StatelessWidget {
  const AddPillButton({super.key, required this.label, this.onTap});

  final String label;

  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 36,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: AppColors.cardSurface.withValues(alpha: 0.55),
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: AppColors.dustyTaupe, width: 1.5),
          boxShadow: const [
            BoxShadow(
              color: AppColors.borderSubtle,
              blurRadius: 14,
              offset: Offset(0, 5),
            ),
          ],
        ),
        child: Text(
          label,
          maxLines: 1,
          style: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w800,
            color: AppColors.primaryMaroon,
          ),
        ),
      ),
    );
  }
}
