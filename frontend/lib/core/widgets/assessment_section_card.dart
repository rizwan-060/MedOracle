import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

/// White card used for the numbered sections of the results screens,
/// adhering strictly to AGENTS.md standards (radius 12.0, AppColors.borderSubtle).
///
/// [emphasized] reproduces the highlighted variant of the design reference:
/// a heavier outline plus two soft radial accents.
class AssessmentSectionCard extends StatelessWidget {
  const AssessmentSectionCard({
    super.key,
    required this.stepNumber,
    required this.title,
    required this.subtitle,
    required this.child,
    this.trailing,
    this.emphasized = false,
  });

  /// Number rendered inside the badge, e.g. `1`.
  final String stepNumber;

  /// Section title, e.g. `Visual reasoning map`.
  final String title;

  /// Section subtitle, e.g. `How your details became the result`.
  final String subtitle;

  /// Optional widget rendered on the right of the section header.
  final Widget? trailing;

  /// Section body.
  final Widget child;

  /// Uses the highlighted outline and radial accents.
  final bool emphasized;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(
          color: emphasized ? AppColors.cta : AppColors.borderSubtle,
          width: emphasized ? 1.5 : 1.0,
        ),
        boxShadow: const <BoxShadow>[
          BoxShadow(
            color: AppColors.refCardShadow,
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Container(
                width: 28,
                height: 28,
                alignment: Alignment.center,
                decoration: const BoxDecoration(
                  color: AppColors.headerBg,
                  shape: BoxShape.circle,
                ),
                child: Text(
                  stepNumber,
                  style: const TextStyle(
                    fontFamily: AppTextStyles.fontFamily,
                    fontSize: 14,
                    height: 1.2,
                    fontWeight: FontWeight.w800,
                    color: AppColors.onPlum,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Text(
                      title,
                      style: AppTextStyles.instrumentSerif(
                        fontSize: 24.0,
                        fontWeight: FontWeight.w600,
                        color: AppColors.headerText,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(subtitle, style: AppTextStyles.sectionSubtitle),
                  ],
                ),
              ),
              if (trailing != null) ...<Widget>[
                const SizedBox(width: 12),
                trailing!,
              ],
            ],
          ),
          const SizedBox(height: 16),
          emphasized
              ? _RadialAccentBackground(child: child)
              : child,
        ],
      ),
    );
  }
}

/// Soft radial highlights behind the emphasized section.
class _RadialAccentBackground extends StatelessWidget {
  const _RadialAccentBackground({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(12.0),
      child: Stack(
        children: <Widget>[
          Positioned.fill(
            child: DecoratedBox(
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  center: const Alignment(-0.76, -0.40),
                  radius: 1.10,
                  colors: <Color>[
                    AppColors.refGlowA.withValues(alpha: 0.38),
                    AppColors.refGlowA.withValues(alpha: 0.00),
                  ],
                ),
              ),
            ),
          ),
          Positioned.fill(
            child: DecoratedBox(
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  center: const Alignment(0.84, 0.76),
                  radius: 0.90,
                  colors: <Color>[
                    AppColors.refGlowB.withValues(alpha: 0.33),
                    AppColors.refGlowB.withValues(alpha: 0.00),
                  ],
                ),
              ),
            ),
          ),
          child,
        ],
      ),
    );
  }
}
