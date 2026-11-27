import 'dart:math' as math;

import 'package:go_router/go_router.dart';
import 'package:material_ui/material_ui.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../navigation/onboarding_navigation.dart';
import '../widgets/onboarding_shell.dart';
import '../widgets/onboarding_type.dart';

/// Onboarding 6 — Your path from here.
///
/// Three staggered notebook sheets flip in along a dotted path. Tapping the
/// stack replays the reveal animation.
class OnboardingPathScreen extends StatefulWidget {
  const OnboardingPathScreen({super.key});

  static const String routePath = RouteNames.onboardingPath;

  @override
  State<OnboardingPathScreen> createState() => _OnboardingPathScreenState();
}

class _OnboardingPathScreenState extends State<OnboardingPathScreen>
    with SingleTickerProviderStateMixin {
  static const Duration _sequenceDuration = Duration(milliseconds: 1700);
  static const double _total = 1700;
  static const Cubic _flipCurve = Cubic(0.22, 1.0, 0.36, 1.0);

  late final AnimationController _controller;
  late final CurvedAnimation _sheet1Flip;
  late final CurvedAnimation _sheet2Flip;
  late final CurvedAnimation _sheet3Flip;
  late final CurvedAnimation _sheet1Opacity;
  late final CurvedAnimation _sheet2Opacity;
  late final CurvedAnimation _sheet3Opacity;
  late final CurvedAnimation _badgePop;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: _sequenceDuration,
    );

    _sheet1Flip = CurvedAnimation(
      parent: _controller,
      curve: Interval(200 / _total, 900 / _total, curve: _flipCurve),
    );
    _sheet2Flip = CurvedAnimation(
      parent: _controller,
      curve: Interval(600 / _total, 1300 / _total, curve: _flipCurve),
    );
    _sheet3Flip = CurvedAnimation(
      parent: _controller,
      curve: Interval(1000 / _total, 1700 / _total, curve: _flipCurve),
    );

    _sheet1Opacity = CurvedAnimation(
      parent: _controller,
      curve: Interval(200 / _total, 900 / _total, curve: Curves.easeOut),
    );
    _sheet2Opacity = CurvedAnimation(
      parent: _controller,
      curve: Interval(600 / _total, 1300 / _total, curve: Curves.easeOut),
    );
    _sheet3Opacity = CurvedAnimation(
      parent: _controller,
      curve: Interval(1000 / _total, 1700 / _total, curve: Curves.easeOut),
    );

    _badgePop = CurvedAnimation(
      parent: _controller,
      curve: Interval(700 / _total, 1200 / _total, curve: Curves.easeOutBack),
    );

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      _controller.forward(from: 0);
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _replay() {
    _controller.forward(from: 0);
  }

  @override
  Widget build(BuildContext context) {
    return OnboardingShell(
      step: 6,
      title: 'Your path from here',
      subtitle: 'Three milestones built your assessment.',
      contentHorizontalPadding: 24,
      ctaLabel: 'Create my account',
      onCta: () => context.go(RouteNames.signup),
      onBack: () => OnboardingNavigation.back(
        context,
        RouteNames.onboardingHabits,
      ),
      child: SingleChildScrollView(
        // OnboardingShell supplies the horizontal half of the requested
        // EdgeInsets.all(24); this supplies the vertical half.
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 24),
          child: AnimatedBuilder(
            animation: _controller,
            builder: (BuildContext context, Widget? child) {
              return Center(
                child: GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: _replay,
                  child: SizedBox(
                    width: 280,
                    height: 436,
                    child: Stack(
                      children: <Widget>[
                        Positioned.fill(
                          child: CustomPaint(
                            size: const Size(280, 436),
                            painter: const _MilestoneConnectorPainter(),
                          ),
                        ),
                        _AnimatedSheet(
                          left: 0,
                          top: 0,
                          tiltDegrees: -1.4,
                          title: 'Profile',
                          status: 'Complete',
                          complete: true,
                          flip: _sheet1Flip,
                          opacity: _sheet1Opacity,
                          badgeProgress: _badgePop.value,
                        ),
                        _AnimatedSheet(
                          left: 108,
                          top: 160,
                          tiltDegrees: 1.4,
                          title: 'Clinical History',
                          status: 'Pending',
                          complete: false,
                          flip: _sheet2Flip,
                          opacity: _sheet2Opacity,
                          badgeProgress: 0,
                        ),
                        _AnimatedSheet(
                          left: 0,
                          top: 320,
                          tiltDegrees: -1.4,
                          title: 'AI Assessment',
                          status: 'Pending',
                          complete: false,
                          flip: _sheet3Flip,
                          opacity: _sheet3Opacity,
                          badgeProgress: 0,
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}

class _AnimatedSheet extends StatelessWidget {
  const _AnimatedSheet({
    required this.left,
    required this.top,
    required this.tiltDegrees,
    required this.title,
    required this.status,
    required this.complete,
    required this.flip,
    required this.opacity,
    required this.badgeProgress,
  });

  final double left;
  final double top;
  final double tiltDegrees;
  final String title;
  final String status;
  final bool complete;
  final Animation<double> flip;
  final Animation<double> opacity;
  final double badgeProgress;

  @override
  Widget build(BuildContext context) {
    final double progress = flip.value.clamp(0.0, 1.0).toDouble();
    final double rotateX = -math.pi / 2 * (1 - progress);
    final double rotateZ = tiltDegrees * math.pi / 180;
    final Matrix4 transform = Matrix4.identity()
      ..setEntry(3, 2, 0.0011)
      ..rotateX(rotateX)
      ..rotateZ(rotateZ);

    return Positioned(
      left: left,
      top: top,
      child: Opacity(
        opacity: opacity.value.clamp(0.0, 1.0).toDouble(),
        child: Transform(
          alignment: Alignment.topCenter,
          transform: transform,
          child: _PaperSheet(
            title: title,
            status: status,
            complete: complete,
            badgeProgress: badgeProgress,
          ),
        ),
      ),
    );
  }
}

class _PaperSheet extends StatelessWidget {
  const _PaperSheet({
    required this.title,
    required this.status,
    required this.complete,
    required this.badgeProgress,
  });

  static const BorderRadius paperRadius = BorderRadius.only(
    topLeft: Radius.circular(3),
    topRight: Radius.circular(2),
    bottomLeft: Radius.circular(3),
    bottomRight: Radius.circular(4),
  );

  final String title;
  final String status;
  final bool complete;
  final double badgeProgress;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 172,
      height: 116,
      child: Stack(
        children: <Widget>[
          Container(
            decoration: BoxDecoration(
              color: AppColors.authInputSurface,
              borderRadius: paperRadius,
              border: Border.all(
                color: AppColors.headerText.withValues(alpha: 0.14),
                width: 1,
              ),
              boxShadow: <BoxShadow>[
                BoxShadow(
                  color: AppColors.headerText.withValues(alpha: 0.4),
                  offset: const Offset(0, 12),
                  blurRadius: 22,
                  spreadRadius: -16,
                ),
                BoxShadow(
                  color: AppColors.onboardingPaperShadowInk.withValues(
                    alpha: 0.14,
                  ),
                  offset: const Offset(0, 3),
                  blurRadius: 8,
                  spreadRadius: -3,
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: paperRadius,
              child: Stack(
                children: <Widget>[
                  Positioned.fill(
                    child: CustomPaint(
                      size: Size.infinite,
                      painter: const _PaperTexturePainter(),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.fromLTRB(40, 16, 28, 16),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Text(
                          title,
                          style: OnboardingType.serif(
                            16,
                            FontWeight.w700,
                            AppColors.onboardingPaperInk,
                            height: 1.25,
                          ).copyWith(letterSpacing: -0.01 * 16),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          status,
                          style: OnboardingType.sans(
                            11,
                            FontWeight.w600,
                            AppColors.onboardingPaperStatus,
                            spacing: 0.06 * 11,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (complete)
            Positioned(
              top: -8,
              right: -8,
              child: _TickBadge(progress: badgeProgress),
            ),
        ],
      ),
    );
  }
}

class _TickBadge extends StatelessWidget {
  const _TickBadge({required this.progress});

  final double progress;

  @override
  Widget build(BuildContext context) {
    final double scale = progress.clamp(0.0, 1.5).toDouble();
    final double rotation = -20 * (1 - scale) * math.pi / 180;
    final Color top = Color.lerp(
          AppColors.onboardingTickGreen,
          AppColors.cardSurface,
          0.25,
        )!;

    return Transform.rotate(
      angle: rotation,
      child: Transform.scale(
        scale: scale,
        child: Container(
          width: 24,
          height: 24,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: <Color>[
                top,
                AppColors.onboardingTickGreen,
                AppColors.onboardingTickGreen,
              ],
            ),
            boxShadow: <BoxShadow>[
              BoxShadow(
                color: AppColors.onboardingTickGreen.withValues(alpha: 0.55),
                offset: const Offset(0, 4),
                blurRadius: 10,
                spreadRadius: -3,
              ),
            ],
          ),
          child: const Center(
            child: CustomPaint(
              painter: _CheckPainter(),
              size: Size(14, 14),
            ),
          ),
        ),
      ),
    );
  }
}

class _CheckPainter extends CustomPainter {
  const _CheckPainter();

  @override
  void paint(Canvas canvas, Size size) {
    canvas.save();
    canvas.scale(size.width / 24, size.height / 24);
    canvas.drawPath(
      Path()
        ..moveTo(20, 6)
        ..lineTo(9, 17)
        ..lineTo(4, 12),
      Paint()
        ..color = AppColors.cardSurface
        ..style = PaintingStyle.stroke
        ..strokeWidth = 3.2
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round,
    );
    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant _CheckPainter oldDelegate) => false;
}

class _PaperTexturePainter extends CustomPainter {
  const _PaperTexturePainter();

  @override
  void paint(Canvas canvas, Size size) {
    for (final double y in <double>[22, 45, 68, 91, 114]) {
      canvas.drawLine(
        Offset(0, y),
        Offset(size.width, y),
        Paint()
          ..color = AppColors.headerText.withValues(alpha: 0.06)
          ..strokeWidth = 1,
      );
    }

    canvas.drawLine(
      const Offset(20, 0),
      Offset(20, size.height),
      Paint()
        ..color = AppColors.onboardingRedMargin.withValues(alpha: 0.5)
        ..strokeWidth = 1.5,
    );
    canvas.drawLine(
      const Offset(25, 0),
      Offset(25, size.height),
      Paint()
        ..color = AppColors.onboardingRedMargin.withValues(alpha: 0.2)
        ..strokeWidth = 1,
    );

    canvas.drawRect(
      Rect.fromLTWH(0, 0, size.width, 3),
      Paint()
        ..shader = LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: <Color>[
            AppColors.headerText.withValues(alpha: 0.12),
            AppColors.headerText.withValues(alpha: 0),
          ],
        ).createShader(Rect.fromLTWH(0, 0, size.width, 3)),
    );

    _drawFold(canvas, size);
    _drawSpeckle(canvas, const Offset(38, 37), 2.4);
    _drawSpeckle(canvas, const Offset(151, 83), 1.8);
  }

  void _drawFold(Canvas canvas, Size size) {
    final double right = size.width;
    final double bottom = size.height;
    const double fold = 18;

    final Path outer = Path()
      ..moveTo(right - fold, bottom)
      ..lineTo(right, bottom - fold)
      ..lineTo(right, bottom - 3)
      ..quadraticBezierTo(right, bottom, right - 3, bottom)
      ..close();
    canvas.drawPath(
      outer,
      Paint()..color = AppColors.onboardingParchmentLight,
    );

    final Path inner = Path()
      ..moveTo(right - fold, bottom)
      ..lineTo(right - 4, bottom - 14)
      ..lineTo(right - 4, bottom)
      ..close();
    canvas.drawPath(
      inner,
      Paint()..color = AppColors.onboardingParchment,
    );

    canvas.drawLine(
      Offset(right - fold, bottom),
      Offset(right, bottom - fold),
      Paint()
        ..color = AppColors.onboardingFoldCrease.withValues(alpha: 0.18)
        ..strokeWidth = 1,
    );
  }

  void _drawSpeckle(Canvas canvas, Offset center, double radius) {
    final Rect bounds = Rect.fromCircle(center: center, radius: radius);
    canvas.drawCircle(
      center,
      radius,
      Paint()
        ..shader = RadialGradient(
          colors: <Color>[
            AppColors.headerText.withValues(alpha: 0.5),
            AppColors.headerText.withValues(alpha: 0),
          ],
        ).createShader(bounds),
    );
  }

  @override
  bool shouldRepaint(covariant _PaperTexturePainter oldDelegate) => false;
}

class _MilestoneConnectorPainter extends CustomPainter {
  const _MilestoneConnectorPainter();

  @override
  void paint(Canvas canvas, Size size) {
    const List<Offset> points = <Offset>[
      Offset(166, 58),
      Offset(114, 218),
      Offset(166, 378),
    ];
    final Paint paint = Paint()
      ..color = AppColors.headerText.withValues(alpha: 0.4)
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    for (int i = 0; i < points.length - 1; i++) {
      _drawDashedLine(canvas, points[i], points[i + 1], paint);
    }
  }

  void _drawDashedLine(
    Canvas canvas,
    Offset start,
    Offset end,
    Paint paint,
  ) {
    const double dash = 2;
    const double gap = 6;
    final double length = (end - start).distance;
    final Offset direction = (end - start) / length;

    double travelled = 0;
    while (travelled < length) {
      final double segmentEnd = (travelled + dash).clamp(0.0, length);
      canvas.drawLine(
        start + direction * travelled,
        start + direction * segmentEnd,
        paint,
      );
      travelled += dash + gap;
    }
  }

  @override
  bool shouldRepaint(covariant _MilestoneConnectorPainter oldDelegate) => false;
}
