import 'dart:math' as math;

import 'package:material_ui/material_ui.dart';

import '../../../core/theme/app_colors.dart';
import 'onboarding_type.dart';

/// First card illustration: answers flowing into a single report.
class ReportIllustration extends StatelessWidget {
  const ReportIllustration({super.key});

  @override
  Widget build(BuildContext context) {
    return _IllustrationFrame(
      child: Row(
        children: <Widget>[
          Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const <Widget>[
                _CheckRow(label: 'About you'),
                SizedBox(height: 12),
                _CheckRow(label: 'Daily habits'),
                SizedBox(height: 12),
                _CheckRow(label: 'Health history'),
              ],
            ),
          ),
          Container(width: 1, height: 96, color: AppColors.headerText
              .withValues(alpha: 0.2)),
          const SizedBox(width: 12),
          Expanded(
            child: Container(
              height: 122,
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: AppColors.authInputSurface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.headerText, width: 2),
              ),
              child: Column(
                children: <Widget>[
                  Text(
                    'Your report',
                    style: OnboardingType.sans(
                      11,
                      FontWeight.w600,
                      AppColors.headerText,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Icon(
                    Icons.favorite_rounded,
                    size: 34,
                    color: AppColors.onboardingAmber,
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: <Widget>[
                      Icon(
                        Icons.show_chart_rounded,
                        size: 18,
                        color: AppColors.headerText,
                      ),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Container(
                          height: 6,
                          decoration: BoxDecoration(
                            color: AppColors.headerText.withValues(alpha: 0.25),
                            borderRadius: BorderRadius.circular(3),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Second card illustration: five agents reaching an agreed answer.
class ConsensusIllustration extends StatelessWidget {
  const ConsensusIllustration({super.key});

  @override
  Widget build(BuildContext context) {
    return _IllustrationFrame(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: List<Widget>.generate(5, (int i) {
              return CircleAvatar(
                radius: 17,
                backgroundColor: AppColors.authInputSurface,
                child: Icon(
                  Icons.person_outline_rounded,
                  size: 18,
                  color: AppColors.headerText,
                ),
              );
            }),
          ),
          const SizedBox(height: 12),
          Container(
            height: 2,
            color: AppColors.onboardingAmber.withValues(alpha: 0.7),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: AppColors.headerText,
              borderRadius: BorderRadius.circular(18),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: <Widget>[
                const Icon(Icons.check_rounded, size: 16, color: AppColors.cardSurface),
                const SizedBox(width: 6),
                Text(
                  'Agreed',
                  style: OnboardingType.sans(
                    12,
                    FontWeight.w600,
                    AppColors.cardSurface,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// Third card illustration: two ten-year trajectories.
class TrajectoryIllustration extends StatelessWidget {
  const TrajectoryIllustration({super.key});

  @override
  Widget build(BuildContext context) {
    return _IllustrationFrame(
      child: Stack(
        children: <Widget>[
          Positioned.fill(child: CustomPaint(painter: _TrajectoryPainter())),
          Positioned(
            left: 4,
            bottom: 4,
            child: Text(
              'Today',
              style: OnboardingType.sans(
                10,
                FontWeight.w400,
                AppColors.headerText.withValues(alpha: 0.75),
              ),
            ),
          ),
          Positioned(
            right: 4,
            bottom: 4,
            child: Text(
              'In 10 years',
              style: OnboardingType.sans(
                10,
                FontWeight.w400,
                AppColors.headerText.withValues(alpha: 0.75),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _TrajectoryPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final Paint axis = Paint()
      ..color = AppColors.headerText.withValues(alpha: 0.35)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;
    canvas.drawLine(
      Offset(10, size.height - 24),
      Offset(size.width - 10, size.height - 24),
      axis,
    );
    canvas.drawLine(
      Offset(10, 10),
      Offset(10, size.height - 24),
      axis,
    );

    final Path statusQuo = Path()
      ..moveTo(10, size.height - 48)
      ..lineTo(size.width - 12, size.height - 54);
    canvas.drawPath(
      statusQuo,
      Paint()
        ..color = AppColors.headerText
        ..strokeWidth = 5
        ..strokeCap = StrokeCap.round
        ..style = PaintingStyle.stroke,
    );

    final Path smallChanges = Path()
      ..moveTo(10, size.height - 48)
      ..cubicTo(
        size.width * 0.35,
        size.height - 70,
        size.width * 0.62,
        size.height - 100,
        size.width - 12,
        16,
      );
    canvas.drawPath(
      smallChanges,
      Paint()
        ..color = AppColors.onboardingAmber
        ..strokeWidth = 3.5
        ..strokeCap = StrokeCap.round
        ..style = PaintingStyle.stroke,
    );

    canvas.drawCircle(
      Offset(size.width - 12, 16),
      6,
      Paint()
        ..color = AppColors.onboardingPeachSurface
        ..style = PaintingStyle.fill,
    );
    canvas.drawCircle(
      Offset(size.width - 12, 16),
      6,
      Paint()
        ..color = AppColors.onboardingAmber
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.5,
    );
  }

  @override
  bool shouldRepaint(covariant _TrajectoryPainter oldDelegate) => false;
}

class _IllustrationFrame extends StatelessWidget {
  const _IllustrationFrame({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 158,
      width: double.infinity,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppColors.onboardingPeachSurface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.onboardingPeachBorder, width: 2),
        ),
        child: child,
      ),
    );
  }
}

class _CheckRow extends StatelessWidget {
  const _CheckRow({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: <Widget>[
        Icon(
          Icons.check_circle_rounded,
          size: 15,
          color: AppColors.headerText,
        ),
        const SizedBox(width: 6),
        Text(
          label,
          style: OnboardingType.sans(
            11,
            FontWeight.w500,
            AppColors.headerText,
          ),
        ),
      ],
    );
  }
}

/// One of the five selectable agent icons in the care-team wheel.
class AgentGlyph extends StatelessWidget {
  const AgentGlyph({super.key, required this.index, required this.selected});

  final int index;
  final bool selected;

  static const List<Color> _fills = <Color>[
    AppColors.pastelMist,
    AppColors.pastelSage,
    AppColors.pastelSand,
    AppColors.pastelBlush,
    AppColors.pastelButter,
  ];
  static const List<Color> _strokes = <Color>[
    AppColors.onboardingSlateSoft,
    AppColors.mutedGreen,
    AppColors.alertMedium,
    AppColors.terraCotta,
    AppColors.onboardingAmber,
  ];

  @override
  Widget build(BuildContext context) {
    final Color fill = _fills[index % _fills.length];
    final Color stroke = _strokes[index % _strokes.length];

    Widget shape = Container(
      width: 64,
      height: 64,
      decoration: BoxDecoration(
        color: fill,
        borderRadius: BorderRadius.circular(index == 1 ? 20 : 32),
        border: Border.all(color: stroke, width: 2),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.deepInk.withValues(alpha: 0.18),
            offset: const Offset(0, 4),
            blurRadius: 6,
          ),
        ],
      ),
      child: Icon(
        <IconData>[
          Icons.monitor_heart_outlined,
          Icons.history_edu_outlined,
          Icons.eco_outlined,
          Icons.trending_up_rounded,
          Icons.alt_route_rounded,
        ][index % 5],
        size: 26,
        color: stroke,
      ),
    );

    if (index == 2 || index == 4) {
      shape = ClipPath(
        clipper: index == 2 ? const _HexagonClipper() : const _OctagonClipper(),
        child: shape,
      );
    }

    return Transform.scale(scale: selected ? 1.08 : 1, child: shape);
  }
}

class _HexagonClipper extends CustomClipper<Path> {
  const _HexagonClipper();

  @override
  Path getClip(Size size) {
    final Path path = Path();
    for (int i = 0; i < 6; i++) {
      final double angle = (math.pi / 3) * i - math.pi / 2;
      final Offset point = Offset(
        size.width / 2 + size.width / 2 * math.cos(angle),
        size.height / 2 + size.height / 2 * math.sin(angle),
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

class _OctagonClipper extends CustomClipper<Path> {
  const _OctagonClipper();

  @override
  Path getClip(Size size) {
    final Path path = Path();
    for (int i = 0; i < 8; i++) {
      final double angle = (math.pi / 4) * i + math.pi / 8;
      final Offset point = Offset(
        size.width / 2 + size.width / 2 * math.cos(angle),
        size.height / 2 + size.height / 2 * math.sin(angle),
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
