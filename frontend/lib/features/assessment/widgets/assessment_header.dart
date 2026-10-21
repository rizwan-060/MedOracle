import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Shared maroon clinical header used across patient assessment sections.
///
/// Shows the "Autosaved" indicator, shield logo + wordmark, a
/// "Save & exit" glass pill, and the segmented progress bar.
class AssessmentHeader extends StatelessWidget {
  const AssessmentHeader({
    super.key,
    required this.currentStep,
    required this.totalSteps,
    this.onSaveExit,
  });

  /// 1-based index of the active step (Step 2 -> 2).
  final int currentStep;

  final int totalSteps;

  final VoidCallback? onSaveExit;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 16),
      decoration: BoxDecoration(
        color: AppColors.primaryMaroon,
        borderRadius: const BorderRadius.vertical(bottom: Radius.circular(28)),
        boxShadow: [
          BoxShadow(
            color: AppColors.textPrimary.withValues(alpha: 0.8),
            blurRadius: 32,
            offset: const Offset(0, 18),
          ),
        ],
      ),
      child: SafeArea(
        bottom: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            SizedBox(
              height: 48,
              child: Row(
                children: [
                  const _AutosavedIndicator(),
                  const Expanded(child: _MedOracleLogo()),
                  _SaveExitButton(onTap: onSaveExit),
                ],
              ),
            ),
            const SizedBox(height: 4),
            _StepProgress(currentStep: currentStep, totalSteps: totalSteps),
          ],
        ),
      ),
    );
  }
}

class _AutosavedIndicator extends StatelessWidget {
  const _AutosavedIndicator();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 14,
          height: 14,
          decoration: const BoxDecoration(
            color: AppColors.mutedGreen,
            shape: BoxShape.circle,
          ),
          child: const Icon(Icons.check, size: 10, color: AppColors.cardSurface),
        ),
        const SizedBox(width: 5),
        const Text(
          'Autosaved',
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w700,
            color: AppColors.greenSurface,
          ),
        ),
      ],
    );
  }
}

class _MedOracleLogo extends StatelessWidget {
  const _MedOracleLogo();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        CustomPaint(
          size: const Size(22, 24),
          painter: _ShieldCrossPainter(
            shieldFill: AppColors.cardSurface,
            crossColor: AppColors.primaryMaroon,
          ),
        ),
        const SizedBox(width: 6),
        const Text(
          'MedOracle',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w800,
            color: AppColors.cardSurface,
          ),
        ),
      ],
    );
  }
}

class _ShieldCrossPainter extends CustomPainter {
  const _ShieldCrossPainter({
    required this.shieldFill,
    required this.crossColor,
  });

  final Color shieldFill;
  final Color crossColor;

  @override
  void paint(Canvas canvas, Size size) {
    final double w = size.width;
    final double h = size.height;
    final Path shield = Path()
      ..moveTo(w * 0.5, 0)
      ..lineTo(w * 0.92, h * 0.2)
      ..lineTo(w * 0.92, h * 0.5)
      ..cubicTo(w * 0.92, h * 0.78, w * 0.72, h * 0.95, w * 0.5, h)
      ..cubicTo(w * 0.28, h * 0.95, w * 0.08, h * 0.78, w * 0.08, h * 0.5)
      ..lineTo(w * 0.08, h * 0.2)
      ..close();

    canvas.drawPath(
      shield,
      Paint()
        ..color = shieldFill
        ..style = PaintingStyle.fill,
    );
    canvas.drawPath(
      shield,
      Paint()
        ..color = crossColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2
        ..strokeJoin = StrokeJoin.round,
    );

    final Paint cross = Paint()
      ..color = crossColor
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(Offset(w * 0.5, h * 0.33), Offset(w * 0.5, h * 0.68), cross);
    canvas.drawLine(Offset(w * 0.32, h * 0.5), Offset(w * 0.68, h * 0.5), cross);
  }

  @override
  bool shouldRepaint(_ShieldCrossPainter oldDelegate) =>
      oldDelegate.shieldFill != shieldFill || oldDelegate.crossColor != crossColor;
}

class _SaveExitButton extends StatelessWidget {
  const _SaveExitButton({this.onTap});

  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 44,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: AppColors.cardSurface.withValues(alpha: 0.14),
          borderRadius: BorderRadius.circular(999),
          border: Border.all(
            color: AppColors.cardSurface.withValues(alpha: 0.3),
          ),
        ),
        child: const Text(
          'Save & exit',
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w800,
            color: AppColors.cardSurface,
          ),
        ),
      ),
    );
  }
}

class _StepProgress extends StatelessWidget {
  const _StepProgress({required this.currentStep, required this.totalSteps});

  final int currentStep;
  final int totalSteps;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: List.generate(totalSteps, (int index) {
        final bool filled = index < currentStep;
        return Expanded(
          child: Container(
            height: 4,
            margin: index == 0 ? null : const EdgeInsets.only(left: 4),
            decoration: BoxDecoration(
              color: filled
                  ? AppColors.cardSurface
                  : AppColors.cardSurface.withValues(alpha: 0.22),
              borderRadius: BorderRadius.circular(2),
            ),
          ),
        );
      }),
    );
  }
}

/// Backward compatibility typedef alias.
typedef WizardHeader = AssessmentHeader;
