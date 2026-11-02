import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

/// MedOracle shield mark, painted from the vector path in the design
/// reference (26 x 28 viewBox: shield outline + medical cross).
class BrandShield extends StatelessWidget {
  const BrandShield({
    super.key,
    this.width = 22,
    this.height = 24,
    this.fill = const Color(0x24FFFFFF),
    this.stroke = AppColors.onPlum,
    this.strokeWidth = 2,
  });

  final double width;
  final double height;
  final Color fill;
  final Color stroke;
  final double strokeWidth;

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      size: Size(width, height),
      painter: _ShieldPainter(
        fill: fill,
        stroke: stroke,
        strokeWidth: strokeWidth,
      ),
    );
  }
}

/// Shield mark + "MedOracle" wordmark, as shown in the intake header.
class BrandLogo extends StatelessWidget {
  const BrandLogo({
    super.key,
    this.fill = const Color(0x24FFFFFF),
    this.stroke = AppColors.onPlum,
    this.textColor = AppColors.onPlum,
  });

  final Color fill;
  final Color stroke;
  final Color textColor;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        BrandShield(fill: fill, stroke: stroke),
        const SizedBox(width: 6),
        // Flexible so a cramped header ellipsises the wordmark instead of
        // overflowing (the reference assumes a 390px canvas).
        Flexible(
          child: Text(
            'MedOracle',
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: AppTextStyles.brand.copyWith(color: textColor),
          ),
        ),
      ],
    );
  }
}

class _ShieldPainter extends CustomPainter {
  const _ShieldPainter({
    required this.fill,
    required this.stroke,
    required this.strokeWidth,
  });

  final Color fill;
  final Color stroke;
  final double strokeWidth;

  @override
  void paint(Canvas canvas, Size size) {
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
        ..color = fill
        ..style = PaintingStyle.fill,
    );
    canvas.drawPath(
      shield,
      Paint()
        ..color = stroke
        ..style = PaintingStyle.stroke
        ..strokeWidth = strokeWidth
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
        ..color = stroke
        ..style = PaintingStyle.stroke
        ..strokeWidth = strokeWidth
        ..strokeCap = StrokeCap.round,
    );
  }

  @override
  bool shouldRepaint(_ShieldPainter oldDelegate) =>
      oldDelegate.fill != fill ||
      oldDelegate.stroke != stroke ||
      oldDelegate.strokeWidth != strokeWidth;
}
