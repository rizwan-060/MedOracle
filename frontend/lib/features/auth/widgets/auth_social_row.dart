import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// "or continue with" divider and Google / Apple provider buttons.
class AuthSocialRow extends StatelessWidget {
  const AuthSocialRow({
    super.key,
    required this.onGoogle,
    required this.onApple,
  });

  final VoidCallback onGoogle;
  final VoidCallback onApple;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        Row(
          children: <Widget>[
            const Expanded(
              child: Divider(
                height: 1,
                thickness: 1,
                color: AppColors.authSlateDivider,
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Text(
                'or continue with',
                style: AppTextStyles.authDivider(),
              ),
            ),
            const Expanded(
              child: Divider(
                height: 1,
                thickness: 1,
                color: AppColors.authSlateDivider,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: <Widget>[
            Expanded(
              child: _SocialButton(
                badge: 'G',
                label: 'Google',
                onTap: onGoogle,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _SocialButton(badge: 'A', label: 'Apple', onTap: onApple),
            ),
          ],
        ),
      ],
    );
  }
}

class _SocialButton extends StatelessWidget {
  const _SocialButton({
    required this.badge,
    required this.label,
    required this.onTap,
  });

  final String badge;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: 'Continue with $label',
      child: SizedBox(
        height: 48,
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onTap,
            borderRadius: BorderRadius.circular(24),
            child: Ink(
              decoration: BoxDecoration(
                color: AppColors.authInputSurface,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: AppColors.authSlateRing),
                boxShadow: const <BoxShadow>[
                  BoxShadow(
                    color: AppColors.authFieldShadow,
                    offset: Offset(0, 8),
                    blurRadius: 18,
                    spreadRadius: -12,
                  ),
                  BoxShadow(
                    color: AppColors.authFieldShadowSoft,
                    offset: Offset(0, 1),
                    blurRadius: 3,
                  ),
                ],
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: <Widget>[
                  Container(
                    width: 24,
                    height: 24,
                    alignment: Alignment.center,
                    decoration: const BoxDecoration(
                      color: AppColors.authSlateTint,
                      shape: BoxShape.circle,
                    ),
                    child: Text(badge, style: AppTextStyles.authSocialBadge()),
                  ),
                  const SizedBox(width: 10),
                  Flexible(
                    child: Text(
                      label,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: AppTextStyles.authSocial(),
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
