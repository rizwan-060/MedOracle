import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import 'autosave_badge.dart';
import 'brand_logo.dart';
import 'glass_pill_button.dart';

/// Maroon intake header: autosave status, MedOracle wordmark, `Save & exit`
/// pill and the 5-segment step progress rail.
class StepHeader extends StatelessWidget {
  const StepHeader({
    super.key,
    required this.stepNumber,
    required this.totalSteps,
    required this.isSaving,
    this.onSaveExit,
  });

  /// 1-based index of the current step.
  final int stepNumber;

  /// Total number of steps in the intake flow.
  final int totalSteps;

  /// Whether a save is currently in flight.
  final bool isSaving;

  final VoidCallback? onSaveExit;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: const BoxDecoration(
        color: AppColors.refPlum,
        borderRadius: BorderRadius.vertical(bottom: Radius.circular(28)),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: Color(0xCC321926),
            offset: Offset(0, 18),
            blurRadius: 32,
            spreadRadius: -20,
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: const BorderRadius.vertical(bottom: Radius.circular(28)),
        child: Stack(
          children: <Widget>[
            const Positioned.fill(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: AppColors.headerSheenGradient,
                ),
              ),
            ),
            const Positioned.fill(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: AppColors.headerGlowGradient,
                ),
              ),
            ),
            const Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: ColoredBox(color: Color(0x24FFFFFF), child: SizedBox(height: 1)),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 16),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: <Widget>[
                  SizedBox(
                    height: 56,
                    child: Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: <Widget>[
                          AutosaveBadge(isSaving: isSaving),
                          const Expanded(child: Center(child: BrandLogo())),
                          GlassPillButton.header(
                            label: 'Save & exit',
                            onTap: onSaveExit,
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Semantics(
                    image: true,
                    label: 'Step $stepNumber of $totalSteps',
                    child: Row(
                      children: <Widget>[
                        for (int i = 1; i <= totalSteps; i++) ...<Widget>[
                          if (i > 1) const SizedBox(width: 4),
                          Expanded(child: _ProgressRail(active: i <= stepNumber)),
                        ],
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ProgressRail extends StatelessWidget {
  const _ProgressRail({required this.active});

  final bool active;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 4,
      decoration: BoxDecoration(
        gradient: active ? AppColors.progressActiveGradient : null,
        color: active ? null : AppColors.refProgressIdle,
        borderRadius: BorderRadius.circular(2),
      ),
    );
  }
}
