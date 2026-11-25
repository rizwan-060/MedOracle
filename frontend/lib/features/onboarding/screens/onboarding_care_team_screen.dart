import 'dart:math' as math;

import 'package:material_ui/material_ui.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../navigation/onboarding_navigation.dart';
import '../widgets/onboarding_shell.dart';
import '../widgets/onboarding_type.dart';

const Duration _motionDuration = Duration(milliseconds: 250);
const int _coreTarget = 5;

/// Onboarding 2 — Your AI Care Team.
///
/// Five agents fly in one after another around a Consensus Engine core. The
/// core activates after five seconds and the detail card reflects the current
/// selection.
class OnboardingCareTeamScreen extends StatefulWidget {
  const OnboardingCareTeamScreen({super.key, this.settled = false});

  static const String routePath = RouteNames.onboardingCareTeam;

  /// Skips the intro and renders the settled, fully arrived composition.
  final bool settled;

  @override
  State<OnboardingCareTeamScreen> createState() =>
      _OnboardingCareTeamScreenState();
}

class _OnboardingCareTeamScreenState extends State<OnboardingCareTeamScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  final Stopwatch _stopwatch = Stopwatch()..start();
  int? _selectedTarget;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 60),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _select(int target) {
    setState(() {
      _selectedTarget = _selectedTarget == target ? null : target;
    });
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
        RouteNames.onboardingBloodType,
      ),
      child: Padding(
        // OnboardingShell supplies 20px; this brings the stage to 24px.
        padding: const EdgeInsets.fromLTRB(4, 6, 4, 0),
        child: AnimatedBuilder(
          animation: _controller,
          builder: (BuildContext context, Widget? child) {
            final double elapsedMs = widget.settled
                ? 5000
                : _stopwatch.elapsedMilliseconds.toDouble();

            final List<double> opacities = <double>[];
            final List<double> offsets = <double>[];
            final List<double> arrivals = <double>[];
            final List<double> bobs = <double>[];

            for (int i = 0; i < _agents.length; i++) {
              if (widget.settled) {
                opacities.add(1);
                offsets.add(0);
                arrivals.add(1);
                bobs.add(math.sin(elapsedMs / 650 + i * 1.3) * 3);
                continue;
              }

              final double start = 400.0 + 750.0 * i;
              final double opacityProgress =
                  ((elapsedMs - start) / 350).clamp(0.0, 1.0).toDouble();
              final double travelProgress =
                  ((elapsedMs - start) / 900).clamp(0.0, 1.0).toDouble();
              final double easedTravel =
                  Curves.easeOutBack.transform(travelProgress);

              opacities.add(Curves.ease.transform(opacityProgress));
              offsets.add(400 * (1 - easedTravel));
              arrivals.add(travelProgress);
              bobs.add(elapsedMs >= start + 900
                  ? math.sin(elapsedMs / 650 + i * 1.3) * 3
                  : 0);
            }

            final bool coreActive = widget.settled || elapsedMs >= 5000;

            return Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                _CareTeamStage(
                  elapsedMs: elapsedMs,
                  coreActive: coreActive,
                  opacities: opacities,
                  offsets: offsets,
                  arrivals: arrivals,
                  bobs: bobs,
                  selected: _selectedTarget,
                  onSelect: _select,
                ),
                const SizedBox(height: 10),
                _InfoCard(selected: _selectedTarget),
              ],
            );
          },
        ),
      ),
    );
  }
}

enum _AgentShape { circle, roundedSquare, hexagon, egg, blob }

class _AgentSpec {
  const _AgentSpec({
    required this.label,
    required this.description,
    required this.fill,
    required this.border,
    required this.shape,
  });

  final String label;
  final String description;
  final Color fill;
  final Color border;
  final _AgentShape shape;
}

const List<_AgentSpec> _agents = <_AgentSpec>[
  _AgentSpec(
    label: 'Vitals & Biometrics',
    description: 'Heart rate, sleep, day-to-day body health',
    fill: AppColors.onboardingVitalsFill,
    border: AppColors.onboardingVitalsBorder,
    shape: _AgentShape.circle,
  ),
  _AgentSpec(
    label: 'Medical History',
    description: 'Past records, illnesses, family history',
    fill: AppColors.onboardingHistoryFill,
    border: AppColors.onboardingHistoryBorder,
    shape: _AgentShape.roundedSquare,
  ),
  _AgentSpec(
    label: 'Lifestyle & Habits',
    description: 'Movement, diet, stress, small changes',
    fill: AppColors.onboardingLifestyleFill,
    border: AppColors.onboardingLifestyleBorder,
    shape: _AgentShape.hexagon,
  ),
  _AgentSpec(
    label: 'Risk & Diagnostic',
    description: 'Future health risk prediction',
    fill: AppColors.onboardingRiskFill,
    border: AppColors.onboardingRiskBorder,
    shape: _AgentShape.egg,
  ),
  _AgentSpec(
    label: 'Counterfactual Simulator',
    description: '"What if" scenario testing',
    fill: AppColors.onboardingCounterfactualFill,
    border: AppColors.onboardingCounterfactualBorder,
    shape: _AgentShape.blob,
  ),
];

class _CareTeamStage extends StatelessWidget {
  const _CareTeamStage({
    required this.elapsedMs,
    required this.coreActive,
    required this.opacities,
    required this.offsets,
    required this.arrivals,
    required this.bobs,
    required this.selected,
    required this.onSelect,
  });

  final double elapsedMs;
  final bool coreActive;
  final List<double> opacities;
  final List<double> offsets;
  final List<double> arrivals;
  final List<double> bobs;
  final int? selected;
  final ValueChanged<int> onSelect;

  static const double _centre = 165;
  static const double _agentRadius = 122;
  static const double _dotRadius = 156;

  List<Offset> get _agentCentres => List<Offset>.generate(_agents.length, (int i) {
        final double radians = (-90 + i * 72) * math.pi / 180;
        return Offset(
          _centre + _agentRadius * math.cos(radians),
          _centre + _agentRadius * math.sin(radians),
        );
      });

  @override
  Widget build(BuildContext context) {
    final double elapsedSeconds = elapsedMs / 1000;
    final List<Offset> centres = _agentCentres;
    final int arrivedCount =
        arrivals.where((double value) => value >= 1).length;

    return SizedBox(
      width: 330,
      height: 330,
      child: ClipRect(
        child: Stack(
          children: <Widget>[
            _Glow(
              coreActive: coreActive,
              arrivedCount: arrivedCount,
              elapsedMs: elapsedMs,
            ),
            _ring(
              left: 9,
              top: 9,
              size: 312,
              angle: elapsedSeconds * (6 * math.pi / 180),
              painter: _CircularDashPainter(
                color: AppColors.headerText.withValues(alpha: 0.38),
                strokeWidth: 1.5,
                dash: 6,
                gap: 4,
              ),
            ),
            _ring(
              left: 89,
              top: 89,
              size: 152,
              angle: -elapsedSeconds * (8 * math.pi / 180),
              painter: _CircularDashPainter(
                color: AppColors.headerText.withValues(alpha: 0.35),
                strokeWidth: 2,
                dash: 0.5,
                gap: 5,
              ),
            ),
            _ring(
              left: 99,
              top: 99,
              size: 132,
              angle: elapsedSeconds * (12 * math.pi / 180),
              opacity: coreActive ? 0.9 : 0,
              painter: _CircularDashPainter(
                color: AppColors.onboardingAmber,
                strokeWidth: 1.5,
                dash: 7,
                gap: 5,
              ),
            ),
            for (int i = 0; i < 3; i++)
              _PulseRing(
                index: i,
                elapsedMs: elapsedMs,
                active: coreActive,
              ),
            for (int i = 0; i < _agents.length; i++)
              _SmallDot(
                left: _centre +
                        _dotRadius * math.cos((-90 + i * 72) * math.pi / 180) -
                    4,
                top: _centre +
                        _dotRadius * math.sin((-90 + i * 72) * math.pi / 180) -
                    4,
                color: _agents[i].border,
                opacity: arrivals[i] >= 1 ? 1 : 0.25,
              ),
            IgnorePointer(
              child: CustomPaint(
                size: const Size.square(330),
                painter: _ConnectorPainter(
                  centres: centres,
                  arrivals: arrivals,
                  selected: selected,
                ),
              ),
            ),
            for (int i = 0; i < _agents.length; i++)
              _AgentNode(
                spec: _agents[i],
                centre: centres[i],
                dx: offsets[i],
                opacity: opacities[i],
                bobDy: bobs[i],
                selected: selected == i,
                onTap: () => onSelect(i),
              ),
            _CoreButton(
              selected: selected == _coreTarget,
              onTap: () => onSelect(_coreTarget),
            ),
          ],
        ),
      ),
    );
  }

  Widget _ring({
    required double left,
    required double top,
    required double size,
    required double angle,
    required CustomPainter painter,
    double opacity = 1,
  }) {
    return Positioned(
      left: left,
      top: top,
      child: IgnorePointer(
        child: AnimatedOpacity(
          opacity: opacity,
          duration: const Duration(milliseconds: 250),
          child: Transform.rotate(
            angle: angle,
            child: CustomPaint(painter: painter, size: Size.square(size)),
          ),
        ),
      ),
    );
  }
}

class _Glow extends StatelessWidget {
  const _Glow({
    required this.coreActive,
    required this.arrivedCount,
    required this.elapsedMs,
  });

  final bool coreActive;
  final int arrivedCount;
  final double elapsedMs;

  @override
  Widget build(BuildContext context) {
    final Color color = coreActive
        ? AppColors.onboardingAmber
        : AppColors.onboardingSlateSoft;
    final double pulse = 0.5 + 0.5 * math.sin(elapsedMs / 2600 * math.pi * 2);
    final double alpha = coreActive
        ? 0.28 + 0.22 * pulse
        : (0.12 + arrivedCount * 0.02).clamp(0, 0.22);

    return Positioned(
      left: 73,
      top: 73,
      child: IgnorePointer(
        child: Container(
          width: 184,
          height: 184,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: RadialGradient(
              colors: <Color>[
                color.withValues(alpha: alpha),
                color.withValues(alpha: alpha * 0.45),
                Colors.transparent,
              ],
              stops: const <double>[0, 0.45, 0.68],
            ),
          ),
        ),
      ),
    );
  }
}

class _PulseRing extends StatelessWidget {
  const _PulseRing({
    required this.index,
    required this.elapsedMs,
    required this.active,
  });

  final int index;
  final double elapsedMs;
  final bool active;

  @override
  Widget build(BuildContext context) {
    final double phase = ((elapsedMs / 2600) + index / 3) % 1;
    final double scale = 1 + 0.95 * phase;
    final double opacity = active ? (1 - phase) * 0.55 : 0;

    return Positioned(
      left: 113,
      top: 113,
      child: IgnorePointer(
        child: Opacity(
          opacity: opacity,
          child: Transform.scale(
            scale: scale,
            child: Container(
              width: 104,
              height: 104,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: AppColors.onboardingAmber.withValues(alpha: 0.7),
                  width: 2,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _SmallDot extends StatelessWidget {
  const _SmallDot({
    required this.left,
    required this.top,
    required this.color,
    required this.opacity,
  });

  final double left;
  final double top;
  final Color color;
  final double opacity;

  @override
  Widget build(BuildContext context) {
    return Positioned(
      left: left,
      top: top,
      child: IgnorePointer(
        child: AnimatedOpacity(
          opacity: opacity,
          duration: const Duration(milliseconds: 300),
          child: Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
        ),
      ),
    );
  }
}

class _CoreButton extends StatelessWidget {
  const _CoreButton({required this.selected, required this.onTap});

  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Positioned(
      left: 113,
      top: 113,
      child: Semantics(
        button: true,
        label: 'Consensus Engine',
        child: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTap: onTap,
          child: AnimatedScale(
            scale: selected ? 1.06 : 1,
            duration: _motionDuration,
            curve: Curves.easeOutBack,
            child: SizedBox(
              width: 104,
              height: 104,
              child: Stack(
                children: <Widget>[
                  const CustomPaint(
                    painter: _CoreHexagonPainter(),
                    size: Size(104, 104),
                  ),
                  Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: <Widget>[
                        const CustomPaint(
                          painter: _LayersGlyphPainter(),
                          size: Size(26, 26),
                        ),
                        const SizedBox(height: 4),
                        SizedBox(
                          width: 70,
                          child: Text(
                            'Consensus Engine',
                            textAlign: TextAlign.center,
                            style: OnboardingType.sans(
                              10,
                              FontWeight.w600,
                              AppColors.authOnSlate,
                              height: 1.1,
                              spacing: 0.2,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _AgentNode extends StatelessWidget {
  const _AgentNode({
    required this.spec,
    required this.centre,
    required this.dx,
    required this.opacity,
    required this.bobDy,
    required this.selected,
    required this.onTap,
  });

  final _AgentSpec spec;
  final Offset centre;
  final double dx;
  final double opacity;
  final double bobDy;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Positioned(
      left: centre.dx - 44 + dx,
      top: centre.dy - 32 + bobDy,
      child: IgnorePointer(
        ignoring: opacity < 0.99,
        child: Opacity(
          opacity: opacity,
          child: Semantics(
            button: true,
            label: spec.label,
            child: GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: onTap,
              child: SizedBox(
                width: 88,
                child: Column(
                  children: <Widget>[
                    AnimatedScale(
                      scale: selected ? 1.08 : 1,
                      duration: _motionDuration,
                      curve: Curves.easeOutBack,
                      child: CustomPaint(
                        painter: _AgentShapePainter(
                          shape: spec.shape,
                          fill: spec.fill,
                          border: spec.border,
                          selected: selected,
                        ),
                        size: const Size(64, 64),
                      ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      spec.label,
                      textAlign: TextAlign.center,
                      style: OnboardingType.sans(
                        10.5,
                        FontWeight.w700,
                        AppColors.onboardingLabelInk,
                        height: 12 / 10.5,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({required this.selected});

  final int? selected;

  @override
  Widget build(BuildContext context) {
    final Color fill;
    final Color border;
    final String heading;
    final String body;

    if (selected == null) {
      fill = AppColors.onboardingPeachBorder;
      border = AppColors.onboardingAmber;
      heading = 'Meet your care team.';
      body =
          'Tap an agent or the core to see how your care team works together.';
    } else if (selected == _coreTarget) {
      fill = AppColors.onboardingSlateSoft;
      border = AppColors.onboardingCoreBorder;
      heading = 'Consensus Engine';
      body = "Weighs every agent's view and combines them into one clear, "
          'balanced health picture.';
    } else {
      final _AgentSpec spec = _agents[selected!];
      fill = spec.fill;
      border = spec.border;
      heading = spec.label;
      body = spec.description;
    }

    return Container(
      width: double.infinity,
      constraints: const BoxConstraints(minHeight: 112),
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
      decoration: BoxDecoration(
        color: AppColors.authInputSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppColors.headerText.withValues(alpha: 0.14),
          width: 1,
        ),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.headerText.withValues(alpha: 0.45),
            offset: const Offset(0, 14),
            blurRadius: 28,
            spreadRadius: -18,
          ),
          BoxShadow(
            color: AppColors.headerText.withValues(alpha: 0.08),
            offset: const Offset(0, 1),
            blurRadius: 3,
          ),
        ],
      ),
      child: AnimatedSwitcher(
        duration: const Duration(milliseconds: 400),
        transitionBuilder: (Widget child, Animation<double> animation) {
          final CurvedAnimation curved =
              CurvedAnimation(parent: animation, curve: Curves.easeOut);
          return FadeTransition(
            opacity: curved,
            child: AnimatedBuilder(
              animation: curved,
              child: child,
              builder: (BuildContext context, Widget? child) {
                return Transform.translate(
                  offset: Offset(0, 8 * (1 - curved.value)),
                  child: child,
                );
              },
            ),
          );
        },
        child: _InfoCardContent(
          key: ValueKey<int?>(selected),
          fill: fill,
          border: border,
          heading: heading,
          body: body,
        ),
      ),
    );
  }
}

class _InfoCardContent extends StatelessWidget {
  const _InfoCardContent({
    super.key,
    required this.fill,
    required this.border,
    required this.heading,
    required this.body,
  });

  final Color fill;
  final Color border;
  final String heading;
  final String body;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        Row(
          children: <Widget>[
            Container(
              width: 14,
              height: 14,
              decoration: BoxDecoration(
                color: fill,
                shape: BoxShape.circle,
                border: Border.all(color: border, width: 2),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                heading,
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
            AppColors.onboardingInfoBody,
            height: 21 / 14,
          ),
        ),
      ],
    );
  }
}

class _CircularDashPainter extends CustomPainter {
  const _CircularDashPainter({
    required this.color,
    required this.strokeWidth,
    required this.dash,
    required this.gap,
  });

  final Color color;
  final double strokeWidth;
  final double dash;
  final double gap;

  @override
  void paint(Canvas canvas, Size size) {
    final Rect rect = Rect.fromLTWH(
      strokeWidth / 2,
      strokeWidth / 2,
      size.width - strokeWidth,
      size.height - strokeWidth,
    );
    final Path circle = Path()..addOval(rect);
    final metric = circle.computeMetrics().first;
    final Paint paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    double distance = 0;
    while (distance < metric.length) {
      final double end = math.min(distance + dash, metric.length);
      canvas.drawPath(metric.extractPath(distance, end), paint);
      distance += dash + gap;
    }
  }

  @override
  bool shouldRepaint(covariant _CircularDashPainter oldDelegate) =>
      oldDelegate.color != color ||
      oldDelegate.strokeWidth != strokeWidth ||
      oldDelegate.dash != dash ||
      oldDelegate.gap != gap;
}

class _ConnectorPainter extends CustomPainter {
  const _ConnectorPainter({
    required this.centres,
    required this.arrivals,
    required this.selected,
  });

  final List<Offset> centres;
  final List<double> arrivals;
  final int? selected;

  @override
  void paint(Canvas canvas, Size size) {
    const Offset centre = Offset(165, 165);
    for (int i = 0; i < centres.length; i++) {
      final double progress = arrivals[i];
      if (progress <= 0) continue;

      final bool isSelected = selected == i;
      final Color color = isSelected ? _agents[i].border : AppColors.headerText;
      final double alpha = (isSelected ? 0.95 : 0.22) * progress;

      canvas.drawLine(
        centre,
        centres[i],
        Paint()
          ..color = color.withValues(alpha: alpha)
          ..strokeWidth = isSelected ? 2.5 : 1.2
          ..strokeCap = StrokeCap.round,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _ConnectorPainter oldDelegate) =>
      selected != oldDelegate.selected ||
      !_sameDoubles(arrivals, oldDelegate.arrivals);
}

class _CoreHexagonPainter extends CustomPainter {
  const _CoreHexagonPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final Rect rect = Offset.zero & size;
    final RadialGradient gradient = RadialGradient(
      center: const Alignment(0, -0.24),
      radius: 0.82,
      colors: <Color>[
        AppColors.onboardingSlateLight,
        AppColors.onboardingSlateSoft,
        AppColors.onboardingSlateDeep,
      ],
      stops: const <double>[0, 0.55, 1],
    );

    canvas.drawPath(
      _shapePath(_AgentShape.hexagon, rect),
      Paint()..shader = gradient.createShader(rect),
    );
  }

  @override
  bool shouldRepaint(covariant _CoreHexagonPainter oldDelegate) => false;
}

class _LayersGlyphPainter extends CustomPainter {
  const _LayersGlyphPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final Paint paint = Paint()
      ..color = AppColors.authOnSlate
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.8
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    for (int i = 2; i >= 0; i--) {
      final double dy = i * 4;
      canvas.drawPath(
        Path()
          ..moveTo(13, 5 + dy)
          ..lineTo(21, 9 + dy)
          ..lineTo(13, 13 + dy)
          ..lineTo(5, 9 + dy)
          ..close(),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _LayersGlyphPainter oldDelegate) => false;
}

class _AgentShapePainter extends CustomPainter {
  const _AgentShapePainter({
    required this.shape,
    required this.fill,
    required this.border,
    required this.selected,
  });

  final _AgentShape shape;
  final Color fill;
  final Color border;
  final bool selected;

  @override
  void paint(Canvas canvas, Size size) {
    final Rect outer = Offset.zero & size;
    final Path outerPath = _shapePath(shape, outer);

    if (selected) {
      canvas.drawPath(
        outerPath,
        Paint()
          ..color = border.withValues(alpha: 0.65)
          ..maskFilter = MaskFilter.blur(BlurStyle.normal, 6),
      );
    }

    canvas.save();
    canvas.translate(0, 4);
    canvas.drawPath(
      outerPath,
      Paint()
        ..color = AppColors.deepInk.withValues(alpha: 0.18)
        ..maskFilter = MaskFilter.blur(BlurStyle.normal, 5),
    );
    canvas.restore();

    canvas.drawPath(outerPath, Paint()..color = border);

    final Rect inner = Rect.fromLTWH(3, 3, size.width - 6, size.height - 6);
    canvas.drawPath(
      _shapePath(shape, inner),
      Paint()..color = fill,
    );
  }

  @override
  bool shouldRepaint(covariant _AgentShapePainter oldDelegate) =>
      shape != oldDelegate.shape ||
      fill != oldDelegate.fill ||
      border != oldDelegate.border ||
      selected != oldDelegate.selected;
}

const List<Offset> _hexagonPoints = <Offset>[
  Offset(0.25, 0.03),
  Offset(0.75, 0.03),
  Offset(1, 0.5),
  Offset(0.75, 0.97),
  Offset(0.25, 0.97),
  Offset(0, 0.5),
];

const List<Offset> _blobPoints = <Offset>[
  Offset(0.5, 0),
  Offset(0.8, 0.09),
  Offset(1, 0.38),
  Offset(0.93, 0.76),
  Offset(0.66, 1),
  Offset(0.3, 0.96),
  Offset(0.05, 0.7),
  Offset(0, 0.34),
  Offset(0.2, 0.07),
];

Path _shapePath(_AgentShape shape, Rect rect) {
  switch (shape) {
    case _AgentShape.circle:
      return Path()..addOval(rect);
    case _AgentShape.roundedSquare:
      final double radius = rect.left > 0 ? 17 : 20;
      return Path()
        ..addRRect(RRect.fromRectAndRadius(rect, Radius.circular(radius)));
    case _AgentShape.hexagon:
      return _polygonPath(rect, _hexagonPoints);
    case _AgentShape.egg:
      return _eggPath(rect);
    case _AgentShape.blob:
      return _polygonPath(rect, _blobPoints);
  }
}

Path _polygonPath(Rect rect, List<Offset> points) {
  final Path path = Path();
  for (int i = 0; i < points.length; i++) {
    final Offset point = points[i];
    final Offset position = Offset(
      rect.left + rect.width * point.dx,
      rect.top + rect.height * point.dy,
    );
    if (i == 0) {
      path.moveTo(position.dx, position.dy);
    } else {
      path.lineTo(position.dx, position.dy);
    }
  }
  path.close();
  return path;
}

Path _eggPath(Rect rect) {
  final double x = rect.left;
  final double y = rect.top;
  final double w = rect.width;
  final double h = rect.height;
  final Path path = Path()
    ..moveTo(x + w * 0.5, y)
    ..cubicTo(x + w * 0.92, y, x + w, y + h * 0.42, x + w, y + h * 0.58)
    ..cubicTo(x + w, y + h * 0.86, x + w * 0.76, y + h, x + w * 0.5, y + h)
    ..cubicTo(x + w * 0.24, y + h, x, y + h * 0.86, x, y + h * 0.58)
    ..cubicTo(x, y + h * 0.42, x + w * 0.08, y, x + w * 0.5, y)
    ..close();
  return path;
}

bool _sameDoubles(List<double> a, List<double> b) {
  if (a.length != b.length) return false;
  for (int i = 0; i < a.length; i++) {
    if (a[i] != b[i]) return false;
  }
  return true;
}
