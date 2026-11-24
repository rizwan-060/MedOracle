import 'dart:math' as math;

import 'package:material_ui/material_ui.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../navigation/onboarding_navigation.dart';
import '../widgets/onboarding_illustrations.dart';
import '../widgets/onboarding_shell.dart';
import '../widgets/onboarding_type.dart';

/// Onboarding 2 — Your AI Care Team.
///
/// Five specialist agents orbit a Consensus Engine. Tapping any node updates
/// the detail card below the wheel.
class OnboardingCareTeamScreen extends StatefulWidget {
  const OnboardingCareTeamScreen({super.key});

  static const String routePath = RouteNames.onboardingCareTeam;

  @override
  State<OnboardingCareTeamScreen> createState() =>
      _OnboardingCareTeamScreenState();
}

class _OnboardingCareTeamScreenState extends State<OnboardingCareTeamScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  int _selected = -1;

  static const List<_Agent> _agents = <_Agent>[
    _Agent(
      name: 'Vitals & Biometrics',
      description: 'Heart rate, sleep, day-to-day body health',
    ),
    _Agent(
      name: 'Medical History',
      description: 'Past records, illnesses, family history',
    ),
    _Agent(
      name: 'Lifestyle & Habits',
      description: 'Movement, diet, stress, small changes',
    ),
    _Agent(
      name: 'Risk & Diagnostic',
      description: 'Future health risk prediction',
    ),
    _Agent(
      name: 'Counterfactual Simulator',
      description: '"What if" scenario testing',
    ),
  ];

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 14),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  String get _detailTitle {
    if (_selected >= 0 && _selected < _agents.length) {
      return _agents[_selected].name;
    }
    if (_selected == 5) return 'Consensus Engine';
    return 'Meet your care team';
  }

  String get _detailBody {
    if (_selected >= 0 && _selected < _agents.length) {
      return _agents[_selected].description;
    }
    if (_selected == 5) {
      return "Weighs every agent's view and combines them into one clear, "
          'balanced health picture.';
    }
    return 'Tap an agent or the core to see how your care team works together.';
  }

  void _select(int index) {
    setState(() => _selected = index);
  }

  @override
  Widget build(BuildContext context) {
    return OnboardingShell(
      step: 2,
      title: 'Your AI Care Team',
      subtitle: '5 specialized agents working for your health.',
      ctaLabel: 'Tell us about you',
      onBack: () => OnboardingNavigation.back(
        context,
        RouteNames.onboardingWelcome,
      ),
      onCta: () => OnboardingNavigation.next(
        context,
        RouteNames.onboardingProfile,
      ),
      child: SingleChildScrollView(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              AnimatedBuilder(
                animation: _controller,
                builder: (BuildContext context, Widget? child) {
                  return _AgentWheel(
                    angle: _controller.value * math.pi * 2,
                    selected: _selected,
                    onSelect: _select,
                  );
                },
              ),
              const SizedBox(height: 10),
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 350),
                child: _AgentDetailCard(
                  key: ValueKey<int>(_selected),
                  title: _detailTitle,
                  body: _detailBody,
                  selected: _selected,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Agent {
  const _Agent({required this.name, required this.description});

  final String name;
  final String description;
}

class _AgentWheel extends StatelessWidget {
  const _AgentWheel({
    required this.angle,
    required this.selected,
    required this.onSelect,
  });

  final double angle;
  final int selected;
  final ValueChanged<int> onSelect;

  @override
  Widget build(BuildContext context) {
    const double center = 165;
    const double radius = 122;

    return SizedBox(
      width: 330,
      height: 330,
      child: Stack(
        children: <Widget>[
          Positioned.fill(
            child: Transform.rotate(
              angle: angle,
              child: CustomPaint(
                size: const Size.square(330),
                painter: _RingPainter(
                  radius: 156,
                  color: AppColors.headerText.withValues(alpha: 0.38),
                  dashed: true,
                ),
              ),
            ),
          ),
          Positioned.fill(
            child: Transform.rotate(
              angle: -angle * 1.35,
              child: CustomPaint(
                size: const Size.square(330),
                painter: _RingPainter(
                  radius: 76,
                  color: AppColors.headerText.withValues(alpha: 0.35),
                  dashed: true,
                ),
              ),
            ),
          ),
          Positioned.fill(
            child: CustomPaint(
              size: const Size.square(330),
              painter: _AgentLinesPainter(selected: selected),
            ),
          ),
          for (int i = 0; i < 5; i++)
            _agentNode(i, center, radius),
          Positioned(
            left: 113,
            top: 113,
            child: Semantics(
              button: true,
              label: 'Consensus Engine',
              child: GestureDetector(
                onTap: () => onSelect(5),
                child: ClipPath(
                  clipper: const _HexagonClipper(),
                  child: Container(
                    width: 104,
                    height: 104,
                    color: selected == 5
                        ? AppColors.onboardingSlateDeep
                        : AppColors.onboardingSlateSoft,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: <Widget>[
                        Icon(
                          Icons.psychology_outlined,
                          size: 24,
                          color: AppColors.cardSurface,
                        ),
                        const SizedBox(height: 4),
                        SizedBox(
                          width: 72,
                          child: Text(
                            'Consensus Engine',
                            textAlign: TextAlign.center,
                            style: OnboardingType.sans(
                              9,
                              FontWeight.w600,
                              AppColors.cardSurface,
                              height: 11 / 9,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _agentNode(int index, double center, double radius) {
    final double radians = (-90 + index * 72) * math.pi / 180;
    final double x = center + radius * math.cos(radians) - 44;
    final double y = center + radius * math.sin(radians) - 32;
    final String label =
        const <String>['Vitals', 'History', 'Lifestyle', 'Risk', 'What-if'][index];

    return Positioned(
      left: x,
      top: y,
      child: Semantics(
        button: true,
        label: label,
        child: GestureDetector(
          onTap: () => onSelect(index),
          child: SizedBox(
            width: 88,
            child: Column(
              children: <Widget>[
                AgentGlyph(index: index, selected: selected == index),
                const SizedBox(height: 5),
                Text(
                  label,
                  textAlign: TextAlign.center,
                  style: OnboardingType.sans(
                    10,
                    FontWeight.w700,
                    AppColors.onboardingMutedInk,
                    height: 12 / 10,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _AgentDetailCard extends StatelessWidget {
  const _AgentDetailCard({
    super.key,
    required this.title,
    required this.body,
    required this.selected,
  });

  final String title;
  final String body;
  final int selected;

  @override
  Widget build(BuildContext context) {
    final Color chip = selected == 5
        ? AppColors.onboardingSlateSoft
        : selected >= 0
            ? AppColors.alertMedium
            : AppColors.onboardingAmber;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      width: double.infinity,
      constraints: const BoxConstraints(minHeight: 112),
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
      decoration: BoxDecoration(
        color: AppColors.authInputSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.headerText.withValues(alpha: 0.14)),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.headerText.withValues(alpha: 0.45),
            offset: const Offset(0, 14),
            blurRadius: 28,
            spreadRadius: -18,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Row(
            children: <Widget>[
              Container(
                width: 14,
                height: 14,
                decoration: BoxDecoration(
                  color: chip,
                  shape: BoxShape.circle,
                  border: Border.all(color: chip, width: 2),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  title,
                  style: OnboardingType.serif(
                    19,
                    FontWeight.w700,
                    AppColors.deepInk,
                    height: 24 / 19,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            body,
            style: OnboardingType.sans(
              14,
              FontWeight.w400,
              AppColors.onboardingMutedInk,
              height: 21 / 14,
            ),
          ),
        ],
      ),
    );
  }
}

class _RingPainter extends CustomPainter {
  const _RingPainter({
    required this.radius,
    required this.color,
    required this.dashed,
  });

  final double radius;
  final Color color;
  final bool dashed;

  @override
  void paint(Canvas canvas, Size size) {
    final Offset center = Offset(size.width / 2, size.height / 2);
    final Paint paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;

    if (!dashed) {
      canvas.drawCircle(center, radius, paint);
      return;
    }

    const int segments = 48;
    for (int i = 0; i < segments; i += 2) {
      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        (i / segments) * math.pi * 2,
        (1 / segments) * math.pi * 2,
        false,
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _RingPainter oldDelegate) =>
      oldDelegate.radius != radius ||
      oldDelegate.color != color ||
      oldDelegate.dashed != dashed;
}

class _AgentLinesPainter extends CustomPainter {
  const _AgentLinesPainter({required this.selected});

  final int selected;

  @override
  void paint(Canvas canvas, Size size) {
    final Offset center = Offset(size.width / 2, size.height / 2);
    for (int i = 0; i < 5; i++) {
      final double radians = (-90 + i * 72) * math.pi / 180;
      final Offset end = center + Offset(122 * math.cos(radians), 122 * math.sin(radians));
      final bool on = selected == i;
      canvas.drawLine(
        center,
        end,
        Paint()
          ..color = on
              ? AppColors.alertMedium
              : AppColors.headerText.withValues(alpha: 0.22)
          ..strokeWidth = on ? 2.5 : 1.2
          ..strokeCap = StrokeCap.round,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _AgentLinesPainter oldDelegate) =>
      oldDelegate.selected != selected;
}

class _HexagonClipper extends CustomClipper<Path> {
  const _HexagonClipper();

  @override
  Path getClip(Size size) {
    final Path path = Path();
    for (int i = 0; i < 6; i++) {
      final double a = (math.pi / 3) * i - math.pi / 2;
      final Offset point = Offset(
        size.width / 2 + size.width / 2 * math.cos(a),
        size.height / 2 + size.height / 2 * math.sin(a),
      );
      if (i == 0) {
        path.moveTo(point.dx, point.dy);
      } else {
        path.lineTo(point.dx, point.dy);
      }
    }
    path.close();
    return path;
  }

  @override
  bool shouldReclip(covariant CustomClipper<Path> oldClipper) => false;
}
