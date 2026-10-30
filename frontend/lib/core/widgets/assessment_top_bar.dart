import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';
import 'brand_logo.dart';

/// Light header shared by every results / assessment screen.
///
/// Mirrors the design reference: the completion status on the left, the
/// MedOracle lockup in the middle and the close affordance on the right.
class AssessmentTopBar extends StatelessWidget {
  const AssessmentTopBar({super.key, this.onClose});

  /// Invoked when the user taps `Close`.
  final VoidCallback? onClose;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 56,
      child: Row(
        children: <Widget>[
          const Flexible(
            child: Align(
              alignment: Alignment.centerLeft,
              child: _CompletionBadge(),
            ),
          ),
          const Flexible(
            child: Center(
              child: BrandLogo(
                fill: AppColors.cardSurface,
                stroke: AppColors.headerText,
                textColor: AppColors.textPrimary,
              ),
            ),
          ),
          Flexible(
            child: Align(
              alignment: Alignment.centerRight,
              child: _CloseButton(onPressed: onClose),
            ),
          ),
        ],
      ),
    );
  }
}

/// Green `Completed` status chip with a check mark.
class _CompletionBadge extends StatelessWidget {
  const _CompletionBadge();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        Container(
          width: 14,
          height: 14,
          decoration: const BoxDecoration(
            color: AppColors.mutedGreen,
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.check_rounded,
            size: 10,
            color: AppColors.cardSurface,
          ),
        ),
        const SizedBox(width: 6),
        const Flexible(
          child: Text(
            'Completed',
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: AppTextStyles.statusBadge,
          ),
        ),
      ],
    );
  }
}

/// Pill shaped close button.
class _CloseButton extends StatelessWidget {
  const _CloseButton({this.onPressed});

  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 100,
      height: 44,
      child: Material(
        type: MaterialType.transparency,
        child: InkWell(
          onTap: onPressed,
          borderRadius: BorderRadius.circular(999),
          child: Container(
            padding: const EdgeInsets.only(right: 18),
            alignment: Alignment.centerRight,
            decoration: BoxDecoration(
              gradient: AppColors.pillGradient,
              borderRadius: BorderRadius.circular(999),
              border: Border.all(color: AppColors.cardSurface, width: 1.5),
              boxShadow: <BoxShadow>[
                BoxShadow(
                  color: AppColors.refPlum.withValues(alpha: 0.20),
                  blurRadius: 16,
                  offset: const Offset(0, 6),
                ),
              ],
            ),
            child: const Text('Close', style: AppTextStyles.secondaryAction),
          ),
        ),
      ),
    );
  }
}
