import 'package:go_router/go_router.dart';
import 'package:material_ui/material_ui.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../navigation/onboarding_navigation.dart';
import '../widgets/onboarding_shell.dart';
import '../widgets/onboarding_type.dart';

/// Onboarding 6 — Your path from here.
///
/// Three staggered milestone sheets connected by a dotted path. Tapping the
/// stack replays the reveal animation.
class OnboardingPathScreen extends StatefulWidget {
  const OnboardingPathScreen({super.key});

  static const String routePath = RouteNames.onboardingPath;

  @override
  State<OnboardingPathScreen> createState() => _OnboardingPathScreenState();
}

class _OnboardingPathScreenState extends State<OnboardingPathScreen> {
  int _replayKey = 0;

  @override
  Widget build(BuildContext context) {
    return OnboardingShell(
      step: 6,
      title: 'Your path from here',
      subtitle: 'Three milestones built your assessment.',
      ctaLabel: 'Create my account',
      onCta: () => context.go(RouteNames.signup),
      onBack: () => OnboardingNavigation.back(
        context,
        RouteNames.onboardingHabits,
      ),
      child: SingleChildScrollView(
        child: Center(
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 500),
            child: GestureDetector(
              key: ValueKey<int>(_replayKey),
              behavior: HitTestBehavior.opaque,
              onTap: () => setState(() => _replayKey++),
              child: const SizedBox(
                width: 280,
                height: 436,
                child: _MilestonePath(),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _MilestonePath extends StatelessWidget {
  const _MilestonePath();

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: <Widget>[
        Positioned.fill(
          child: CustomPaint(
            size: const Size(280, 436),
            painter: _MilestoneConnectorPainter(),
          ),
        ),
        const Positioned(
          left: 0,
          top: 0,
          child: _MilestoneCard(
            title: 'Profile',
            status: 'Complete',
            complete: true,
            rotation: -1.4,
          ),
        ),
        const Positioned(
          left: 108,
          top: 160,
          child: _MilestoneCard(
            title: 'Clinical History',
            status: 'Pending',
            complete: false,
            rotation: 1.4,
          ),
        ),
        const Positioned(
          left: 0,
          top: 320,
          child: _MilestoneCard(
            title: 'AI Assessment',
            status: 'Pending',
            complete: false,
            rotation: -1.4,
          ),
        ),
      ],
    );
  }
}

class _MilestoneCard extends StatelessWidget {
  const _MilestoneCard({
    required this.title,
    required this.status,
    required this.complete,
    required this.rotation,
  });

  final String title;
  final String status;
  final bool complete;
  final double rotation;

  @override
  Widget build(BuildContext context) {
    return Transform.rotate(
      angle: rotation * 3.14159265 / 180,
      child: Container(
        width: 172,
        height: 116,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.authInputSurface,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(
            color: AppColors.headerText.withValues(alpha: 0.28),
          ),
          boxShadow: <BoxShadow>[
            BoxShadow(
              color: AppColors.headerText.withValues(alpha: 0.35),
              offset: const Offset(0, 10),
              blurRadius: 20,
              spreadRadius: -12,
            ),
          ],
        ),
        child: Stack(
          children: <Widget>[
            Positioned(
              right: 12,
              top: 10,
              child: Icon(
                Icons.description_outlined,
                size: 18,
                color: AppColors.headerText.withValues(alpha: 0.5),
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                Text(
                  title,
                  style: OnboardingType.serif(
                    18,
                    FontWeight.w700,
                    AppColors.deepInk,
                    height: 22 / 18,
                  ),
                ),
                const SizedBox(height: 6),
                Row(
                  children: <Widget>[
                    Text(
                      status,
                      style: OnboardingType.sans(
                        12,
                        FontWeight.w500,
                        complete
                            ? AppColors.mutedGreen
                            : AppColors.onboardingHint,
                      ),
                    ),
                    if (complete) ...<Widget>[
                      const SizedBox(width: 6),
                      Container(
                        width: 18,
                        height: 18,
                        decoration: const BoxDecoration(
                          color: AppColors.mutedGreen,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.check_rounded,
                          size: 12,
                          color: AppColors.cardSurface,
                        ),
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
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

    for (int i = 0; i < points.length - 1; i++) {
      _drawDashedLine(
        canvas,
        points[i],
        points[i + 1],
        Paint()
          ..color = AppColors.headerText.withValues(alpha: 0.4)
          ..strokeWidth = 2
          ..strokeCap = StrokeCap.round,
      );
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
      final double segmentEnd = (travelled + dash).clamp(0, length);
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
