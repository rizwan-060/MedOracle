import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// White rounded card used for each section of an intake step.
///
/// When [isActive] the card gets the elevated "focused" treatment from the
/// design: a 2px maroon ring, a soft maroon glow behind it, and a slightly
/// translucent surface.
///
/// When [onToggle] is provided the header becomes tappable and shows a
/// rotating chevron; the body is hidden while [isExpanded] is false.
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
    final Widget card = Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isActive
            ? AppColors.cardSurface.withValues(alpha: 0.58)
            : AppColors.cardSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isActive ? AppColors.primaryMaroon : AppColors.borderSubtle,
          width: isActive ? 2 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.textPrimary.withValues(alpha: isActive ? 0.18 : 0.06),
            blurRadius: isActive ? 30 : 8,
            offset: Offset(0, isActive ? 12 : 2),
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
                    style: const TextStyle(
                      fontSize: 17,
                      height: 24 / 17,
                      fontWeight: FontWeight.w800,
                      color: AppColors.textPrimary,
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
                      size: 18,
                      color: AppColors.textPrimary,
                    ),
                  ),
                ],
              ],
            ),
          ),
          if (isExpanded) ...[
            const SizedBox(height: 12),
            child,
          ],
        ],
      ),
    );

    if (!isActive) return card;

    // Soft radial halo bleeding out behind the active card.
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(34),
        gradient: RadialGradient(
          center: const Alignment(-0.85, -0.6),
          radius: 1.1,
          colors: [
            AppColors.dustyTaupe.withValues(alpha: 0.55),
            AppColors.dustyTaupe.withValues(alpha: 0),
          ],
          stops: const [0, 0.55],
        ),
      ),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(34),
          gradient: RadialGradient(
            center: const Alignment(0.9, 0.85),
            radius: 1.1,
            colors: [
              AppColors.borderSubtle.withValues(alpha: 0.8),
              AppColors.borderSubtle.withValues(alpha: 0),
            ],
            stops: const [0, 0.55],
          ),
        ),
        child: card,
      ),
    );
  }
}
