import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/widgets/brand_logo.dart';

/// Slate hero header from the authentication references.
///
/// Shows the MedOracle wordmark, a large serif greeting and an optional glass
/// "Back to login" pill for the sign-up flow.
class AuthHeroHeader extends StatelessWidget {
  const AuthHeroHeader({
    super.key,
    required this.title,
    required this.subtitle,
    this.onBack,
    this.backLabel = 'Back to login',
  });

  final String title;
  final String subtitle;
  final VoidCallback? onBack;
  final String backLabel;

  @override
  Widget build(BuildContext context) {
    final double topInset = MediaQuery.paddingOf(context).top;

    return Container(
      decoration: const BoxDecoration(
        color: AppColors.headerText,
        borderRadius: BorderRadius.vertical(bottom: Radius.circular(28)),
      ),
      padding: EdgeInsets.fromLTRB(20, topInset + 16, 20, 80),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          const Center(
            child: BrandLogo(
              shieldWidth: 20,
              shieldHeight: 20,
              textStyle: TextStyle(
                fontFamily: AppTextStyles.fontFamily,
                fontSize: 16,
                height: 20 / 16,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          const SizedBox(height: 36),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Text(
                      title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: AppTextStyles.authHero(),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: AppTextStyles.authHeroSubtitle(),
                    ),
                  ],
                ),
              ),
              if (onBack != null)
                Padding(
                  padding: const EdgeInsets.only(left: 12, top: 6),
                  child: _BackToLoginPill(label: backLabel, onTap: onBack!),
                ),
            ],
          ),
        ],
      ),
    );
  }
}

class _BackToLoginPill extends StatelessWidget {
  const _BackToLoginPill({required this.label, required this.onTap});

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: label,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(18),
          child: Ink(
            height: 36,
            decoration: BoxDecoration(
              color: AppColors.authGlassFill,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: AppColors.authGlassBorder),
            ),
            padding: const EdgeInsets.only(left: 10, right: 12),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: <Widget>[
                const Icon(
                  Icons.arrow_back_rounded,
                  size: 16,
                  color: AppColors.authOnSlate,
                ),
                const SizedBox(width: 4),
                Text(label, style: AppTextStyles.authBackPill()),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
