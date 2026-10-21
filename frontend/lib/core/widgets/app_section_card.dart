import 'dart:math' as math;
import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// Highly customizable, generic section card widget.
///
/// Supports:
/// - Title and optional subtitle
/// - Trailing actions (e.g. edit buttons, add pill, badges)
/// - Accordion collapsible behavior via [onToggle] and [isExpanded]
/// - Active focus halo treatment via [isActive]
/// - Style overrides ([backgroundColor], [borderColor], [titleColor], [padding])
class AppSectionCard extends StatelessWidget {
  const AppSectionCard({
    super.key,
    required this.title,
    required this.child,
    this.subtitle,
    this.trailing,
    this.isActive = false,
    this.isExpanded = true,
    this.onToggle,
    this.backgroundColor,
    this.borderColor,
    this.titleColor,
    this.padding,
    this.borderRadius,
  });

  final String title;
  final String? subtitle;
  final Widget? trailing;
  final Widget child;
  final bool isActive;
  final bool isExpanded;
  final VoidCallback? onToggle;
  final Color? backgroundColor;
  final Color? borderColor;
  final Color? titleColor;
  final EdgeInsetsGeometry? padding;
  final double? borderRadius;

  @override
  Widget build(BuildContext context) {
    final double r = borderRadius ?? 16.0;
    final EdgeInsetsGeometry pad = padding ?? const EdgeInsets.all(16);

    final Color effectiveBg = backgroundColor ??
        (isActive
            ? AppColors.cardSurface.withValues(alpha: 0.58)
            : AppColors.cardSurface);
    final Color effectiveBorder = borderColor ??
        (isActive ? AppColors.primaryMaroon : AppColors.borderSubtle);
    final Color effectiveTitle = titleColor ?? AppColors.textPrimary;

    final Widget card = Container(
      width: double.infinity,
      padding: pad,
      decoration: BoxDecoration(
        color: effectiveBg,
        borderRadius: BorderRadius.circular(r),
        border: Border.all(
          color: effectiveBorder,
          width: isActive ? 2 : 1,
        ),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.textPrimary.withValues(alpha: isActive ? 0.18 : 0.06),
            blurRadius: isActive ? 30 : 8,
            offset: Offset(0, isActive ? 12 : 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: onToggle,
            child: Row(
              children: <Widget>[
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Text(
                        title,
                        style: TextStyle(
                          fontSize: 17,
                          height: 24 / 17,
                          fontWeight: FontWeight.w800,
                          color: effectiveTitle,
                        ),
                      ),
                      if (subtitle != null) ...[
                        const SizedBox(height: 2),
                        Text(
                          subtitle!,
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                            color: AppColors.textMuted,
                          ),
                        ),
                      ],
                    ],
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

    // Halo background treatment when active
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(34),
        gradient: RadialGradient(
          center: const Alignment(-0.85, -0.6),
          radius: 1.1,
          colors: <Color>[
            AppColors.dustyTaupe.withValues(alpha: 0.55),
            AppColors.dustyTaupe.withValues(alpha: 0),
          ],
          stops: const <double>[0, 0.55],
        ),
      ),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(34),
          gradient: RadialGradient(
            center: const Alignment(0.9, 0.85),
            radius: 1.1,
            colors: <Color>[
              AppColors.borderSubtle.withValues(alpha: 0.8),
              AppColors.borderSubtle.withValues(alpha: 0),
            ],
            stops: const <double>[0, 0.55],
          ),
        ),
        child: card,
      ),
    );
  }
}
