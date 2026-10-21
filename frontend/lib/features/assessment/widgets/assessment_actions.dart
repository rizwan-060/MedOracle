import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Primary maroon gradient action pill (design: v8 CTA button).
class AssessmentPrimaryAction extends StatelessWidget {
  const AssessmentPrimaryAction({
    super.key,
    required this.label,
    required this.onTap,
  });

  final String label;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Container(
          height: 48,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: <Color>[
                AppColors.primaryMaroon,
                AppColors.primaryMaroon,
                AppColors.maroonDark,
              ],
              stops: <double>[0.0, 0.55, 1.0],
            ),
            borderRadius: BorderRadius.circular(999),
            border: Border.all(
              color: AppColors.cardSurface.withValues(alpha: 0.22),
            ),
            boxShadow: <BoxShadow>[
              BoxShadow(
                color: AppColors.primaryMaroon.withValues(alpha: 0.45),
                blurRadius: 22,
                spreadRadius: -8,
                offset: const Offset(0, 10),
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
      ),
    );
  }
}

/// Secondary glass pill beneath the CTA (design: "Done").
class AssessmentDonePill extends StatelessWidget {
  const AssessmentDonePill({
    super.key,
    required this.label,
    required this.onTap,
  });

  final String label;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Container(
          height: 44,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: AppColors.cardSurface,
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: AppColors.borderSubtle),
            boxShadow: <BoxShadow>[
              BoxShadow(
                color: AppColors.textPrimary.withValues(alpha: 0.06),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Text(
            label,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              color: AppColors.primaryMaroon,
            ),
          ),
        ),
      ),
    );
  }
}
