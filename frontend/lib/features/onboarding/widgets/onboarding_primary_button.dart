import 'package:material_ui/material_ui.dart';

import '../../../core/theme/app_colors.dart';
import 'onboarding_type.dart';

/// Full-width terracotta call-to-action used by every onboarding step.
class OnboardingPrimaryButton extends StatelessWidget {
  const OnboardingPrimaryButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.enabled = true,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    final bool canPress = enabled && onPressed != null;

    return Semantics(
      button: true,
      enabled: canPress,
      label: label,
      child: SizedBox(
        width: double.infinity,
        height: 56,
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: canPress ? onPressed : null,
            borderRadius: BorderRadius.circular(28),
            child: AnimatedOpacity(
              duration: const Duration(milliseconds: 180),
              opacity: canPress ? 1 : 0.45,
              child: Ink(
                decoration: BoxDecoration(
                  color: AppColors.terraCotta,
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
                    style: OnboardingType.sans(
                      16,
                      FontWeight.w700,
                      AppColors.cardSurface,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
