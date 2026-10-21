import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Primary maroon gradient CTA used to advance the intake wizard,
/// e.g. "Next: Medications & Family".
class GradientNextButton extends StatelessWidget {
  const GradientNextButton({super.key, required this.label, this.onTap});

  final String label;

  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 48,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              AppColors.primaryMaroon,
              AppColors.primaryMaroon,
              AppColors.maroonDark,
            ],
            stops: [0, 0.55, 1],
          ),
          borderRadius: BorderRadius.circular(999),
          border: Border.all(
            color: AppColors.cardSurface.withValues(alpha: 0.22),
          ),
          boxShadow: [
            BoxShadow(
              color: AppColors.maroonDark.withValues(alpha: 0.7),
              blurRadius: 24,
              spreadRadius: -8,
              offset: const Offset(0, 12),
            ),
            BoxShadow(
              color: AppColors.textPrimary.withValues(alpha: 0.3),
              blurRadius: 3,
              offset: const Offset(0, 1),
            ),
          ],
        ),
        child: Text(
          label,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: AppColors.cardSurface,
          ),
        ),
      ),
    );
  }
}

/// Text-style "Back" button that sits under the primary CTA.
class BackTextButton extends StatelessWidget {
  const BackTextButton({super.key, this.onTap});

  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 44,
        margin: const EdgeInsets.only(top: 4),
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: AppColors.cardSurface.withValues(alpha: 0.55),
          borderRadius: BorderRadius.circular(999),
          border: Border.all(
            color: AppColors.cardSurface.withValues(alpha: 0.9),
          ),
        ),
        child: const Text(
          'Back',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w700,
            color: AppColors.primaryMaroon,
          ),
        ),
      ),
    );
  }
}
