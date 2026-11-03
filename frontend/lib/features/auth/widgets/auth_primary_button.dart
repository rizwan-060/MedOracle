import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// Ember pill call-to-action from the authentication references.
///
/// Fixed 56px height, fully rounded, with the reference ember drop shadow.
class AuthPrimaryButton extends StatelessWidget {
  const AuthPrimaryButton({
    super.key,
    required this.label,
    required this.onPressed,
  });

  final String label;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: label,
      child: SizedBox(
        width: double.infinity,
        height: 56,
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onPressed,
            borderRadius: BorderRadius.circular(28),
            child: Ink(
              decoration: BoxDecoration(
                color: AppColors.authCta,
                borderRadius: BorderRadius.circular(28),
                boxShadow: const <BoxShadow>[
                  BoxShadow(
                    color: AppColors.authCtaShadow,
                    offset: Offset(0, 12),
                    blurRadius: 22,
                    spreadRadius: -10,
                  ),
                ],
              ),
              child: Center(
                child: Text(
                  label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: AppTextStyles.authCta(),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
