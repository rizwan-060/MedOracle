import 'package:material_ui/material_ui.dart';

import '../../../core/theme/app_colors.dart';

/// Six-segment progress rail in the onboarding header.
class OnboardingProgress extends StatelessWidget {
  const OnboardingProgress({super.key, required this.step});

  /// 1-based onboarding step.
  final int step;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Onboarding step $step of 6',
      child: SizedBox(
        width: 150,
        child: Row(
          children: List<Widget>.generate(6, (int index) {
            final bool active = index < step;
            return Expanded(
              child: Container(
                height: 4,
                margin: EdgeInsets.only(right: index == 5 ? 0 : 6),
                decoration: BoxDecoration(
                  color: active
                      ? AppColors.cardSurface
                      : AppColors.cardSurface.withValues(alpha: 0.35),
                  borderRadius: BorderRadius.circular(999),
                ),
              ),
            );
          }),
        ),
      ),
    );
  }
}

/// Three small position dots used inside the Welcome screen cards.
class OnboardingDots extends StatelessWidget {
  const OnboardingDots({
    super.key,
    required this.index,
    required this.onTap,
  });

  final int index;
  final ValueChanged<int> onTap;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List<Widget>.generate(3, (int i) {
        final bool active = i == index;
        return Semantics(
          button: true,
          label: 'Feature card ${i + 1}',
          child: GestureDetector(
            onTap: () => onTap(i),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              width: active ? 24 : 8,
              height: 8,
              margin: const EdgeInsets.symmetric(horizontal: 4),
              decoration: BoxDecoration(
                color: active
                    ? AppColors.headerText
                    : AppColors.headerText.withValues(alpha: 0.25),
                borderRadius: BorderRadius.circular(999),
              ),
            ),
          ),
        );
      }),
    );
  }
}
