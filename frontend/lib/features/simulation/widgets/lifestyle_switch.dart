import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// On/off switch of the lifestyle simulation.
///
/// Reproduces the design reference's switch: a 51x31 pill that fills with the
/// slate accent and a 27px white knob that slides across
/// (design: v8 Step 6C switch control).
class LifestyleSwitch extends StatelessWidget {
  const LifestyleSwitch({
    super.key,
    required this.value,
    required this.onChanged,
    required this.semanticLabel,
  });

  /// Whether the switch is on.
  final bool value;

  /// Called with the new value when the switch is tapped.
  final ValueChanged<bool> onChanged;

  /// Accessible name of the switch, e.g. `Quit smoking`.
  final String semanticLabel;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      container: true,
      toggled: value,
      label: semanticLabel,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () => onChanged(!value),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          curve: Curves.ease,
          width: 51,
          height: 31,
          decoration: BoxDecoration(
            color: value
                ? AppColors.refControlAccent
                : AppColors.refControlTrackIdle,
            borderRadius: BorderRadius.circular(999),
          ),
          child: AnimatedAlign(
            duration: const Duration(milliseconds: 200),
            curve: Curves.ease,
            alignment: value
                ? Alignment.centerRight
                : Alignment.centerLeft,
            child: Container(
              margin: const EdgeInsets.all(2),
              width: 27,
              height: 27,
              decoration: BoxDecoration(
                color: AppColors.cardSurface,
                shape: BoxShape.circle,
                boxShadow: <BoxShadow>[
                  BoxShadow(
                    color: AppColors.textPrimary.withValues(alpha: 0.30),
                    offset: const Offset(0, 2),
                    blurRadius: 5,
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
