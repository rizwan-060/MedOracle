import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// White rounded card used for each section of an intake step,
/// adhering strictly to AGENTS.md standards (radius 12.0, AppColors.borderSubtle).
class SectionCard extends StatelessWidget {
  const SectionCard({
    super.key,
    required this.title,
    required this.child,
    this.trailing,
    this.isActive = false,
    this.isExpanded = true,
    this.onToggle,
  });

  final String title;

  /// Optional widget pinned to the right of the title (e.g. an add pill).
  final Widget? trailing;

  final Widget child;

  /// Whether this card is the currently focused/expanded one.
  final bool isActive;

  /// Accordion state. Only meaningful when [onToggle] is non-null.
  final bool isExpanded;

  /// When non-null, the card header acts as an accordion toggle.
  final VoidCallback? onToggle;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(
          color: isActive ? AppColors.cta : AppColors.borderSubtle,
          width: isActive ? 1.5 : 1.0,
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.textPrimary.withValues(alpha: isActive ? 0.08 : 0.04),
            blurRadius: isActive ? 16 : 6,
            offset: Offset(0, isActive ? 4 : 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: onToggle,
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    title,
                    style: AppTextStyles.instrumentSerif(
                      fontSize: 24.0,
                      fontWeight: FontWeight.w600,
                      color: AppColors.headerText,
                    ),
                  ),
                ),
                if (trailing != null) ...[
                  const SizedBox(width: 8),
                  trailing!,
                ],
                if (onToggle != null) ...[
                  const SizedBox(width: 10),
                  Transform.rotate(
                    angle: isExpanded ? 0 : math.pi,
                    child: const Icon(
                      Icons.keyboard_arrow_down,
                      size: 20,
                      color: AppColors.headerText,
                    ),
                  ),
                ],
              ],
            ),
          ),
          if (isExpanded) ...[
            const SizedBox(height: 16.0),
            child,
          ],
        ],
      ),
    );
  }
}
