import 'package:material_ui/material_ui.dart';

import '../../../core/theme/app_colors.dart';
import 'onboarding_type.dart';

/// Full-width terracotta call-to-action used by every onboarding step.
class OnboardingPrimaryButton extends StatefulWidget {
  const OnboardingPrimaryButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.enabled = true,
    this.hardShadow = false,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool enabled;

  /// OB5 override: a solid 3D bottom shadow with a pressed-down state.
  final bool hardShadow;

  @override
  State<OnboardingPrimaryButton> createState() =>
      _OnboardingPrimaryButtonState();
}

class _OnboardingPrimaryButtonState extends State<OnboardingPrimaryButton> {
  bool _hovered = false;
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final bool canPress = widget.enabled && widget.onPressed != null;
    final bool lifted = widget.hardShadow && (canPress && (_hovered || _pressed));
    final Color surface = lifted
        ? Color.lerp(AppColors.terraCotta, AppColors.cardSurface, 0.07)!
        : AppColors.terraCotta;

    final List<BoxShadow> shadows = widget.hardShadow
        ? <BoxShadow>[
            BoxShadow(
              color: AppColors.onboardingCtaHardShadow,
              offset: Offset(0, _pressed && canPress ? 1 : 5),
            ),
          ]
        : const <BoxShadow>[
            BoxShadow(
              color: AppColors.authCtaShadow,
              offset: Offset(0, 12),
              blurRadius: 22,
              spreadRadius: -10,
            ),
          ];

    final Widget button = Semantics(
      button: true,
      enabled: canPress,
      label: widget.label,
      child: SizedBox(
        width: double.infinity,
        height: 56,
        child: MouseRegion(
          onEnter: widget.hardShadow
              ? (_) => setState(() => _hovered = true)
              : null,
          onExit: widget.hardShadow
              ? (_) => setState(() => _hovered = false)
              : null,
          child: GestureDetector(
            onTapDown: canPress
                ? (_) => setState(() => _pressed = true)
                : null,
            onTapUp: canPress
                ? (_) => setState(() => _pressed = false)
                : null,
            onTapCancel: canPress
                ? () => setState(() => _pressed = false)
                : null,
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: canPress ? widget.onPressed : null,
                borderRadius: BorderRadius.circular(28),
                child: AnimatedOpacity(
                  duration: const Duration(milliseconds: 180),
                  opacity: canPress ? 1 : 0.45,
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 100),
                    transform: Matrix4.translationValues(
                      0,
                      widget.hardShadow && _pressed && canPress ? 4 : 0,
                      0,
                    ),
                    decoration: BoxDecoration(
                      color: surface,
                      borderRadius: BorderRadius.circular(28),
                      boxShadow: shadows,
                    ),
                    child: Center(
                      child: Text(
                        widget.label,
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
        ),
      ),
    );

    return IgnorePointer(ignoring: !canPress, child: button);
  }
}
