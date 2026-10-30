import 'dart:async';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// Animated splash screen for MedOracle.
///
/// Displays the pulsing MedOracle logo and clinical intelligence tagline,
/// then smoothly transitions to the onboarding flow.
class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _pulseController;
  late final Animation<double> _scaleAnimation;
  late final Animation<double> _fadeAnimation;
  Timer? _navigationTimer;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    )..repeat(reverse: true);

    _scaleAnimation = Tween<double>(begin: 0.94, end: 1.06).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOutCubic),
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _pulseController,
        curve: const Interval(0.0, 0.6, curve: Curves.easeIn),
      ),
    );

    // Navigate to onboarding after 2.2 seconds
    _navigationTimer = Timer(const Duration(milliseconds: 2200), () {
      if (mounted) {
        context.go(RouteNames.onboarding);
      }
    });
  }

  @override
  void dispose() {
    _navigationTimer?.cancel();
    _pulseController.dispose();
    super.dispose();
  }

  void _skipSplash() {
    _navigationTimer?.cancel();
    if (mounted) {
      context.go(RouteNames.onboarding);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.canvasBackground,
      body: GestureDetector(
        onTap: _skipSplash,
        behavior: HitTestBehavior.opaque,
        child: Stack(
          children: [
            // Ambient corner glow (top-left)
            Positioned(
              top: -100,
              left: -100,
              child: Container(
                width: 300,
                height: 300,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      AppColors.onboardingAuraTopLeft,
                      Colors.transparent,
                    ],
                  ),
                ),
              ),
            ),

            // Ambient corner glow (bottom-right)
            Positioned(
              bottom: -100,
              right: -100,
              child: Container(
                width: 320,
                height: 320,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      AppColors.onboardingAuraBottomRight,
                      Colors.transparent,
                    ],
                  ),
                ),
              ),
            ),

            // Center branded pulse logo & title
            Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  ScaleTransition(
                    scale: _scaleAnimation,
                    child: Container(
                      width: 88,
                      height: 88,
                      decoration: BoxDecoration(
                        color: AppColors.onboardingMaroon,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: AppColors.onboardingMaroon.withValues(alpha: 0.35),
                            blurRadius: 28,
                            spreadRadius: 4,
                            offset: const Offset(0, 8),
                          ),
                        ],
                      ),
                      child: Center(
                        child: CustomPaint(
                          size: const Size(42, 24),
                          painter: _SplashEcgPainter(
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 28),
                  Text(
                    'MedOracle',
                    style: AppTextStyles.lexend(
                      fontSize: 32,
                      fontWeight: FontWeight.w700,
                      color: AppColors.onboardingTitle,
                      letterSpacing: -0.5,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Multi-Agent Disease Forecasting',
                    style: AppTextStyles.lexend(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: AppColors.onboardingBody,
                      letterSpacing: 0.2,
                    ),
                  ),
                ],
              ),
            ),

            // Bottom loading indicator
            Positioned(
              bottom: 48,
              left: 0,
              right: 0,
              child: Center(
                child: FadeTransition(
                  opacity: _fadeAnimation,
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        width: 6,
                        height: 6,
                        decoration: const BoxDecoration(
                          shape: BoxShape.circle,
                          color: AppColors.onboardingMaroon,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Initializing clinical engine...',
                        style: AppTextStyles.lexend(
                          fontSize: 12,
                          fontWeight: FontWeight.w400,
                          color: AppColors.onboardingBody,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Precise ECG pulse icon painter matching the MedOracle logo
class _SplashEcgPainter extends CustomPainter {
  final Color color;

  const _SplashEcgPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 2.4
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final path = Path();
    final h = size.height;
    final w = size.width;

    // Baseline start
    path.moveTo(0, h * 0.55);
    path.lineTo(w * 0.22, h * 0.55);

    // P wave
    path.lineTo(w * 0.28, h * 0.42);
    path.lineTo(w * 0.34, h * 0.55);

    // QRS complex
    path.lineTo(w * 0.40, h * 0.65);
    path.lineTo(w * 0.52, h * 0.05);
    path.lineTo(w * 0.64, h * 0.95);
    path.lineTo(w * 0.72, h * 0.55);

    // T wave
    path.lineTo(w * 0.82, h * 0.40);
    path.lineTo(w * 0.88, h * 0.55);

    // Baseline end
    path.lineTo(w, h * 0.55);

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant _SplashEcgPainter oldDelegate) =>
      oldDelegate.color != color;
}
