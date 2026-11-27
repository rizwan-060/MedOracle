import 'package:material_ui/material_ui.dart';

import '../../../core/theme/app_colors.dart';
import 'onboarding_primary_button.dart';
import 'onboarding_progress.dart';
import 'onboarding_type.dart';

/// Shared native chrome for the six onboarding screens.
///
/// Provides the slate curved header, six-step progress rail, cream canvas and
/// the fixed terracotta footer CTA. Individual steps only supply their body.
class OnboardingShell extends StatelessWidget {
  const OnboardingShell({
    super.key,
    required this.step,
    required this.title,
    required this.subtitle,
    required this.ctaLabel,
    required this.onCta,
    required this.child,
    this.onBack,
    this.ctaEnabled = true,
    this.backgroundColor = AppColors.canvasBackground,
    this.contentHorizontalPadding = 20,
    this.hardCtaShadow = false,
  });

  final int step;
  final String title;
  final String subtitle;
  final String ctaLabel;
  final VoidCallback? onCta;
  final Widget child;

  /// A null callback renders a dimmed, non-interactive back button.
  final VoidCallback? onBack;
  final bool ctaEnabled;

  /// Optional per-step visual overrides. Defaults match the shared chrome.
  final Color backgroundColor;
  final double contentHorizontalPadding;
  final bool hardCtaShadow;

  @override
  Widget build(BuildContext context) {
    final double bottomInset = MediaQuery.paddingOf(context).bottom;

    return Scaffold(
      backgroundColor: backgroundColor,
      resizeToAvoidBottomInset: false,
      body: SafeArea(
        bottom: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            Container(
              height: 207,
              padding: const EdgeInsets.fromLTRB(20, 28, 20, 28),
              decoration: BoxDecoration(
                color: AppColors.headerText,
                borderRadius: const BorderRadius.vertical(
                  bottom: Radius.circular(40),
                ),
                boxShadow: <BoxShadow>[
                  BoxShadow(
                    color: AppColors.deepInk.withValues(alpha: 0.18),
                    blurRadius: 26,
                    offset: const Offset(0, 10),
                    spreadRadius: -12,
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: <Widget>[
                  Row(
                    children: <Widget>[
                      _BackCircle(onTap: onBack),
                      Expanded(
                        child: Center(child: OnboardingProgress(step: step)),
                      ),
                      const SizedBox(width: 44),
                    ],
                  ),
                  const SizedBox(height: 24),
                  Text(
                    title,
                    style: OnboardingType.serif(
                      24,
                      FontWeight.w700,
                      AppColors.cardSurface,
                      height: 28 / 24,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    subtitle,
                    style: OnboardingType.sans(
                      14,
                      FontWeight.w400,
                      AppColors.cardSurface.withValues(alpha: 0.9),
                      height: 20 / 14,
                    ),
                  ),
                ],
              ),
            ),
            Expanded(
              child: Padding(
                padding: EdgeInsets.symmetric(
                  horizontal: contentHorizontalPadding,
                ),
                child: child,
              ),
            ),
            Padding(
              padding: EdgeInsets.fromLTRB(20, 12, 20, 32 + bottomInset),
              child: OnboardingPrimaryButton(
                label: ctaLabel,
                onPressed: onCta,
                enabled: ctaEnabled,
                hardShadow: hardCtaShadow,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _BackCircle extends StatelessWidget {
  const _BackCircle({this.onTap});

  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      enabled: onTap != null,
      label: 'Back',
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(22),
          child: AnimatedOpacity(
            duration: const Duration(milliseconds: 160),
            opacity: onTap == null ? 0.4 : 1,
            child: Ink(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: Colors.transparent,
                borderRadius: BorderRadius.circular(22),
                border: Border.all(
                  color: AppColors.cardSurface.withValues(alpha: 0.9),
                  width: 1.5,
                ),
              ),
              child: Icon(
                Icons.arrow_back_ios_new_rounded,
                size: 18,
                color: AppColors.cardSurface,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
