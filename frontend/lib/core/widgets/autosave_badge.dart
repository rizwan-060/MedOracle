import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

/// "Autosaved" (or "Saving...") micro status shown at the top-left of the
/// intake header.
class AutosaveBadge extends StatelessWidget {
  const AutosaveBadge({super.key, required this.isSaving, this.width = 100});

  /// Whether a save is currently in flight.
  final bool isSaving;

  /// Fixed width so the brand logo stays optically centred in the header.
  final double width;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      child: Row(
        children: <Widget>[
          const _AutosaveCheck(size: 14),
          const SizedBox(width: 5),
          Flexible(
            child: Text(
              isSaving ? 'Saving...' : 'Autosaved',
              style: AppTextStyles.autosave,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}

class _AutosaveCheck extends StatelessWidget {
  const _AutosaveCheck({required this.size});

  final double size;

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      size: Size.square(size),
      painter: const _CheckPainter(),
    );
  }
}

class _CheckPainter extends CustomPainter {
  const _CheckPainter();

  @override
  void paint(Canvas canvas, Size size) {
    canvas.scale(size.width / 14, size.height / 14);

    canvas.drawCircle(
      const Offset(7, 7),
      6,
      Paint()..color = AppColors.refAutosaveCircle,
    );

    final Path tick = Path()
      ..moveTo(4, 7.2)
      ..lineTo(6.2, 9.3)
      ..lineTo(10, 5);
    canvas.drawPath(
      tick,
      Paint()
        ..color = AppColors.refAutosaveTick
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.6
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round,
    );
  }

  @override
  bool shouldRepaint(_CheckPainter oldDelegate) => false;
}
