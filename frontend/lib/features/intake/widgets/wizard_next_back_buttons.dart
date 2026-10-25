import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// Primary call-to-action button used to advance the intake wizard,
/// adhering strictly to AGENTS.md (fixed height 56.0, radius 12.0).
class GradientNextButton extends StatelessWidget {
  const GradientNextButton({super.key, required this.label, this.onTap});

  final String label;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12.0),
        child: Container(
          height: 56.0,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: AppColors.cta,
            borderRadius: BorderRadius.circular(12.0),
            boxShadow: [
              BoxShadow(
                color: AppColors.cta.withValues(alpha: 0.35),
                blurRadius: 18,
                spreadRadius: -4,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: Text(
            label,
            style: AppTextStyles.lexend(
              fontSize: 16.0,
              fontWeight: FontWeight.w700,
              color: Colors.white,
              letterSpacing: 0.2,
            ),
          ),
        ),
      ),
    );
  }
}

/// Secondary "Back" button adhering strictly to AGENTS.md (fixed height 56.0, radius 12.0).
class BackTextButton extends StatelessWidget {
  const BackTextButton({super.key, this.onTap});

  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 16.0),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12.0),
          child: Container(
            height: 56.0,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: AppColors.cardSurface,
              borderRadius: BorderRadius.circular(12.0),
              border: Border.all(
                color: AppColors.borderSubtle,
                width: 1.5,
              ),
              boxShadow: [
                BoxShadow(
                  color: AppColors.textPrimary.withValues(alpha: 0.04),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Text(
              'Back',
              style: AppTextStyles.lexend(
                fontSize: 14.0,
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
