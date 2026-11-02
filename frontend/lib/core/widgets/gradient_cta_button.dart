import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

/// Primary call-to-action button adhering strictly to AGENTS.md
/// (Fixed height 56.0, radius 12.0, primary accent #E04E26).
class GradientCtaButton extends StatelessWidget {
  const GradientCtaButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.height = 56.0,
  });

  final String label;
  final VoidCallback? onPressed;

  /// Fixed height of 56.0 per AGENTS.md standards.
  final double height;

  @override
  Widget build(BuildContext context) {
    final bool enabled = onPressed != null;

    return Semantics(
      button: true,
      enabled: enabled,
      label: label,
      child: SizedBox(
        width: double.infinity,
        height: height,
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onPressed,
            borderRadius: BorderRadius.circular(12.0),
            child: Ink(
              height: height,
              decoration: BoxDecoration(
                color: enabled ? AppColors.cta : AppColors.dustyTaupe,
                border: Border.all(color: AppColors.ctaBorder),
                borderRadius: BorderRadius.circular(12.0),
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
                children: <Widget>[
                  Center(
                    child: Text(
                      label,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: AppTextStyles.lexend(
                        fontSize: 16.0,
                        fontWeight: FontWeight.w700,
                        color: Colors.white,
                        letterSpacing: 0.2,
                      ),
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
