import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Maroon rounded-bottom header shared by the assessment output screens.
///
/// Shows the "Completed" indicator, the MedOracle shield + wordmark and a
/// glass "Close" pill (design: v8 Step 6A header band).
class AssessmentHeader extends StatelessWidget {
  const AssessmentHeader({
    super.key,
    this.onClose,
  });

  /// Dismisses the results flow (wired to Step 5 by the router).
  final VoidCallback? onClose;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 16),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: <Color>[AppColors.primaryMaroon, AppColors.maroonDark],
        ),
        borderRadius: BorderRadius.vertical(bottom: Radius.circular(28)),
      ),
      child: SafeArea(
        bottom: false,
        child: SizedBox(
          height: 48,
          child: Row(
            children: <Widget>[
              const SizedBox(width: 100, child: _CompletedIndicator()),
              const Expanded(child: _MedOracleLogo()),
              SizedBox(
                width: 100,
                child: Align(
                  alignment: Alignment.centerRight,
                  child: _ClosePill(onTap: onClose),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CompletedIndicator extends StatelessWidget {
  const _CompletedIndicator();

  @override
  Widget build(BuildContext context) {
    // Balances the 100px Close pill; scales down instead of overflowing
    // when the test font doubles the label width.
    return FittedBox(
      fit: BoxFit.scaleDown,
      alignment: Alignment.centerLeft,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Container(
            width: 14,
            height: 14,
            decoration: const BoxDecoration(
              color: AppColors.mutedGreen,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.check,
              size: 10,
              color: AppColors.cardSurface,
            ),
          ),
          const SizedBox(width: 5),
          const Text(
            'Completed',
            maxLines: 1,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w700,
              color: AppColors.greenSurface,
            ),
          ),
        ],
      ),
    );
  }
}

class _MedOracleLogo extends StatelessWidget {
  const _MedOracleLogo();

  @override
  Widget build(BuildContext context) {
    // The flanking indicator and pill each claim 100px, so the lockup scales
    // down instead of overflowing the leftover slot on narrow phones.
    return Align(
      alignment: Alignment.center,
      child: FittedBox(
        fit: BoxFit.scaleDown,
        child: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            CustomPaint(
              size: const Size(22, 24),
              painter: const _ShieldPainter(),
            ),
            const SizedBox(width: 6),
            const Text(
              'MedOracle',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w800,
                color: AppColors.cardSurface,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ClosePill extends StatelessWidget {
  const _ClosePill({this.onTap});

  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: onTap,
      child: Container(
        height: 44,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: AppColors.cardSurface.withValues(alpha: 0.14),
          borderRadius: BorderRadius.circular(999),
          border: Border.all(
            color: AppColors.cardSurface.withValues(alpha: 0.30),
          ),
        ),
        child: const Text(
          'Close',
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

/// Shield + cross wordmark glyph, white on the maroon band.
class _ShieldPainter extends CustomPainter {
  const _ShieldPainter();

  @override
  void paint(Canvas canvas, Size size) {
    canvas.save();
    canvas.scale(size.width / 26, size.height / 28);

    final Path shield = Path()
      ..moveTo(13, 2)
      ..lineTo(23, 5.5)
      ..lineTo(23, 13.5)
      ..cubicTo(23, 19.5, 18.5, 24, 13, 26)
      ..cubicTo(7.5, 24, 3, 19.5, 3, 13.5)
      ..lineTo(3, 5.5)
      ..close();

    canvas.drawPath(
      shield,
      Paint()
        ..color = AppColors.cardSurface.withValues(alpha: 0.14)
        ..style = PaintingStyle.fill,
    );
    canvas.drawPath(
      shield,
      Paint()
        ..color = AppColors.cardSurface
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2
        ..strokeJoin = StrokeJoin.round,
    );

    final Path cross = Path()
      ..moveTo(13, 9)
      ..lineTo(13, 18)
      ..moveTo(8.5, 13.5)
      ..lineTo(17.5, 13.5);
    canvas.drawPath(
      cross,
      Paint()
        ..color = AppColors.cardSurface
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2
        ..strokeCap = StrokeCap.round,
    );

    canvas.restore();
  }

  @override
  bool shouldRepaint(_ShieldPainter oldDelegate) => false;
}
