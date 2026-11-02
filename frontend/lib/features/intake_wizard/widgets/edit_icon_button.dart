import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// 44px pencil edit affordance shown in the top-right of review cards.
/// Tapping it jumps back to the wizard step that owns the section.
class EditIconButton extends StatelessWidget {
  const EditIconButton({super.key, required this.onTap, this.tooltip});

  final VoidCallback onTap;
  final String? tooltip;

  @override
  Widget build(BuildContext context) {
    final Widget icon = CustomPaint(
      size: const Size(18, 18),
      painter: _PencilPainter(color: AppColors.primaryMaroon),
    );

    return GestureDetector(
      onTap: onTap,
      child: SizedBox(
        width: 44,
        height: 44,
        child: Center(
          child: tooltip == null
              ? icon
              : Tooltip(message: tooltip!, child: icon),
        ),
      ),
    );
  }
}

class _PencilPainter extends CustomPainter {
  const _PencilPainter({required this.color});

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final double w = size.width;
    final double h = size.height;
    final Path pencil = Path()
      ..moveTo(w * 0.14, h * 0.86) // tip at bottom-left
      ..lineTo(w * 0.18, h * 0.67)
      ..lineTo(w * 0.70, h * 0.15)
      ..cubicTo(w * 0.74, h * 0.11, w * 0.80, h * 0.11, w * 0.84, h * 0.15)
      ..lineTo(w * 0.87, h * 0.18)
      ..cubicTo(w * 0.91, h * 0.22, w * 0.91, h * 0.28, w * 0.87, h * 0.32)
      ..lineTo(w * 0.34, h * 0.84)
      ..close();

    canvas.drawPath(
      pencil,
      Paint()
        ..color = color
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.8
        ..strokeJoin = StrokeJoin.round,
    );
  }

  @override
  bool shouldRepaint(_PencilPainter oldDelegate) => oldDelegate.color != color;
}
