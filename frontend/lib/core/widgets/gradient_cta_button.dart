import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

/// Primary call-to-action pill (`Next: Clinical Status`, `Submit Assessment`).
///
/// Reproduces the design reference's maroon gradient, 1px light border,
/// glossy top highlight and layered drop shadows.
class GradientCtaButton extends StatelessWidget {
  const GradientCtaButton({
    super.key,
    required this.label,
    required this.onPressed,
  });

  final String label;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    final bool enabled = onPressed != null;

    return Semantics(
      button: true,
      enabled: enabled,
      label: label,
      child: SizedBox(
        width: double.infinity,
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onPressed,
            borderRadius: BorderRadius.circular(999),
            child: Ink(
              height: 48,
              decoration: BoxDecoration(
                gradient: enabled ? AppColors.ctaGradient : null,
                color: enabled ? null : AppColors.dustyTaupe,
                border: Border.all(color: AppColors.ctaBorder),
                borderRadius: BorderRadius.circular(999),
                boxShadow: const <BoxShadow>[
                  BoxShadow(
                    color: AppColors.controlShadowStrong,
                    offset: Offset(0, 12),
                    blurRadius: 24,
                    spreadRadius: -8,
                  ),
                  BoxShadow(
                    color: AppColors.controlShadowSoft,
                    offset: Offset(0, 1),
                    blurRadius: 3,
                  ),
                ],
              ),
              child: Stack(
                fit: StackFit.expand,
                children: <Widget>[
                  // Glossy highlight sweeping across the top half.
                  const Align(
                    alignment: Alignment.topCenter,
                    child: _CtaGloss(),
                  ),
                  Center(
                    child: Text(
                      label,
                      style: AppTextStyles.primaryAction,
                      textAlign: TextAlign.center,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _CtaGloss extends StatelessWidget {
  const _CtaGloss();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 1, left: 5, right: 5),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(999),
        child: Container(
          height: 22,
          decoration: const BoxDecoration(gradient: AppColors.ctaGlossGradient),
        ),
      ),
    );
  }
}
