import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import 'gradient_cta_button.dart';
import 'glass_pill_button.dart';
import 'step_header.dart';

/// Shared page chrome for every intake step: maroon header, scrollable
/// content on the canvas gradient, primary CTA and `Back` pill.
class StepScaffold extends StatelessWidget {
  const StepScaffold({
    super.key,
    required this.stepNumber,
    required this.totalSteps,
    required this.ctaLabel,
    required this.child,
    this.isSaving = false,
    this.onCta,
    this.onBack,
    this.onSaveExit,
  });

  /// 1-based index of the current step.
  final int stepNumber;

  /// Total number of steps in the intake flow.
  final int totalSteps;

  /// Label of the primary pill button pinned to the bottom.
  final String ctaLabel;

  /// Step content, rendered inside the scroll area between header and CTA.
  final Widget child;

  /// Whether a save is currently in flight (shown in the header).
  final bool isSaving;

  final VoidCallback? onCta;
  final VoidCallback? onBack;
  final VoidCallback? onSaveExit;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(gradient: AppColors.canvasGradient),
      child: SafeArea(
        bottom: false,
        child: Column(
          children: <Widget>[
            StepHeader(
              stepNumber: stepNumber,
              totalSteps: totalSteps,
              isSaving: isSaving,
              onSaveExit: onSaveExit,
            ),
            const SizedBox(height: 4),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: <Widget>[
                    child,
                    const SizedBox(height: 24),
                    GradientCtaButton(label: ctaLabel, onPressed: onCta),
                    const SizedBox(height: 4),
                    GlassPillButton.footer(label: 'Back', onTap: onBack),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
