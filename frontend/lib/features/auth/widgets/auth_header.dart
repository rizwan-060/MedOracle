import 'package:flutter/material.dart';
import 'package:medoracle/core/theme/app_colors.dart';
import 'package:medoracle/core/theme/app_text_styles.dart'; // Adjust path if needed

/// Top Main Header displaying the Maroon curved bar with Logo, 
/// followed by the Auth title text
class AuthHeader extends StatelessWidget {
  final bool isLogin;

  const AuthHeader({super.key, required this.isLogin});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 1. The Maroon Curved Header (Same sizing/color as AssessmentHeader, but only logo)
        Container(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 16),
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: <Color>[AppColors.headerBg, AppColors.headerBg],
            ),
            borderRadius: BorderRadius.vertical(bottom: Radius.circular(28)),
          ),
          child: const SafeArea(
            bottom: false,
            child: SizedBox(
              height: 48,
              child: Center(
                child: _MedOracleLogo(),
              ),
            ),
          ),
        ),

        const SizedBox(height: 24.0),

        // 2. The dynamic Auth Text (Welcome back / Create account)
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Main Header with Instrument Serif
              Text(
                isLogin ? 'Welcome back' : 'Create your account',
                style: AppTextStyles.instrumentSerif(
                  fontSize: 28.0,
                  fontWeight: FontWeight.w600,
                  color: AppColors.headerText, // Soft Slate Blue applied
                  letterSpacing: -0.4,
                ),
              ),

              const SizedBox(height: 8.0),

              // Subtitle in Lexend
              Text(
                isLogin
                    ? 'Log in to see your results and next steps.'
                    : 'Start your first health check in a few minutes.',
                style: AppTextStyles.lexend(
                  fontSize: 14.0,
                  fontWeight: FontWeight.w400,
                  color: AppColors.textPrimary, // Updated to your AGENTS.md token
                  height: 1.4,
                ),
              ),
              
              // 32px of spacing at the bottom so the form card isn't squished
              const SizedBox(height: 32.0),
            ],
          ),
        ),
      ],
    );
  }
}

/// The white MedOracle logo centered in the maroon header
class _MedOracleLogo extends StatelessWidget {
  const _MedOracleLogo();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        const CustomPaint(
          size: Size(22, 24),
          painter: _ShieldPainter(),
        ),
        const SizedBox(width: 6),
        const Text(
          'MedOracle',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w800,
            color: AppColors.cardSurface, // White text to contrast with maroon
          ),
        ),
      ],
    );
  }
}

/// Shield + cross wordmark glyph (from AssessmentHeader)
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