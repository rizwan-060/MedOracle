import 'package:material_ui/material_ui.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import 'intake_screen_chrome.dart';

const List<String> _locations = <String>[
  'Head',
  'Neck',
  'Arm',
  'Chest',
  'Abdomen',
];

/// `/intake/step-3` — symptoms (one section open).
class SymptomsReviewScreen extends StatefulWidget {
  const SymptomsReviewScreen({super.key});

  static const String routePath = RouteNames.step3Symptoms;

  @override
  State<SymptomsReviewScreen> createState() => _SymptomsReviewScreenState();
}

class _SymptomsReviewScreenState extends State<SymptomsReviewScreen> {
  final TextEditingController _symptomController = TextEditingController();
  final List<String> _symptoms = <String>['Headache'];
  final List<String> _selectedLocations = <String>['Head'];
  final List<String> _selectedTriggers = <String>['Stress'];
  bool _severityMode = true;
  int _value = 4;

  static const List<String> _triggers = <String>[
    'Stress',
    'Activity',
    'Lack of sleep',
    'Food',
    'Weather',
  ];

  @override
  void dispose() {
    _symptomController.dispose();
    super.dispose();
  }

  void _addSymptom() {
    final String value = _symptomController.text.trim();
    if (value.isEmpty) return;
    setState(() {
      _symptoms.add(value);
      _symptomController.clear();
    });
  }

  void _toggleLocation(String location) {
    setState(() {
      if (_selectedLocations.contains(location)) {
        _selectedLocations.remove(location);
      } else {
        _selectedLocations.add(location);
      }
    });
  }

  void _toggleTrigger(String trigger) {
    setState(() {
      if (_selectedTriggers.contains(trigger)) {
        _selectedTriggers.remove(trigger);
      } else {
        _selectedTriggers.add(trigger);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      resizeToAvoidBottomInset: false,
      backgroundColor: AppColors.canvasBackground,
      body: SafeArea(
        bottom: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            const IntakeHeader(step: 3),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(24, 28, 24, 24),
                children: <Widget>[
                  Text(
                    'Tell us what is bothering you. Add a symptom, show where it is, then rate it. It takes about a minute.',
                    style: IntakeType.sans(
                      13,
                      FontWeight.w300,
                      AppColors.headerText.withValues(alpha: 0.8),
                      height: 20 / 13,
                    ),
                  ),
                  const SizedBox(height: 20),
                  _sectionTitle('Symptoms', 26),
                  const SizedBox(height: 4),
                  Text(
                    'What are you feeling right now?',
                    style: IntakeType.sans(
                      13,
                      FontWeight.w300,
                      AppColors.headerText.withValues(alpha: 0.7),
                    ),
                  ),
                  const SizedBox(height: 16),
                  _SymptomSearch(
                    controller: _symptomController,
                    onSubmit: _addSymptom,
                  ),
                  const SizedBox(height: 8),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: Text(
                      'Type a symptom, then tap + to add it.',
                      style: IntakeType.sans(
                        12,
                        FontWeight.w300,
                        AppColors.headerText.withValues(alpha: 0.7),
                        height: 16 / 12,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: <Widget>[
                      for (final String symptom in _symptoms)
                        _OutlineChip(
                          label: symptom,
                          trailing: Icons.close,
                          onTap: () =>
                              setState(() => _symptoms.remove(symptom)),
                        ),
                    ],
                  ),
                  const SizedBox(height: 36),
                  const SectionDivider(),
                  const SizedBox(height: 36),
                  _centeredTitle('Location', 22),
                  const SizedBox(height: 4),
                  Text(
                    'Tap the spot on the body. You can pick more than one.',
                    textAlign: TextAlign.center,
                    style: IntakeType.sans(
                      13,
                      FontWeight.w300,
                      AppColors.headerText.withValues(alpha: 0.7),
                    ),
                  ),
                  const SizedBox(height: 20),
                  Center(child: _BodyMap(
                    selected: _selectedLocations,
                    onTap: _toggleLocation,
                  )),
                  const SizedBox(height: 36),
                  const SectionDivider(),
                  const SizedBox(height: 36),
                  _Card(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: <Widget>[
                        _cardTitle('Severity/Duration'),
                        const SizedBox(height: 4),
                        Text(
                          'Choose one, then use − and + to set it.',
                          style: IntakeType.sans(
                            13,
                            FontWeight.w300,
                            AppColors.headerText.withValues(alpha: 0.7),
                          ),
                        ),
                        const SizedBox(height: 16),
                        Container(
                          height: 36,
                          padding: const EdgeInsets.all(2),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(999),
                            border: Border.all(
                              color: AppColors.headerText.withValues(alpha: 0.3),
                            ),
                          ),
                          child: Row(
                            children: <Widget>[
                              Expanded(
                                child: _Segment(
                                  label: 'Severity',
                                  active: _severityMode,
                                  onTap: () =>
                                      setState(() => _severityMode = true),
                                ),
                              ),
                              Expanded(
                                child: _Segment(
                                  label: 'Duration',
                                  active: !_severityMode,
                                  onTap: () =>
                                      setState(() => _severityMode = false),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 20),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: <Widget>[
                            StepperButton(
                              icon: Icons.remove,
                              onTap: () =>
                                  setState(() => _value = (_value - 1).clamp(0, 10)),
                            ),
                            const SizedBox(width: 24),
                            SizedBox(
                              width: 40,
                              child: Text(
                                '$_value',
                                textAlign: TextAlign.center,
                                style: IntakeType.sans(
                                  40,
                                  FontWeight.w600,
                                  AppColors.headerText,
                                  height: 1,
                                ),
                              ),
                            ),
                            const SizedBox(width: 24),
                            StepperButton(
                              icon: Icons.add,
                              filled: true,
                              onTap: () =>
                                  setState(() => _value = (_value + 1).clamp(0, 10)),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  _Card(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: <Widget>[
                        _cardTitle('Triggers'),
                        const SizedBox(height: 4),
                        Text(
                          'Optional. Tap any that apply, or add your own.',
                          style: IntakeType.sans(
                            13,
                            FontWeight.w300,
                            AppColors.headerText.withValues(alpha: 0.7),
                          ),
                        ),
                        const SizedBox(height: 16),
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: <Widget>[
                            for (final String trigger in _triggers)
                              _OutlineChip(
                                label: trigger,
                                selected: _selectedTriggers.contains(trigger),
                                onTap: () => _toggleTrigger(trigger),
                              ),
                            _OutlineChip(
                              label: 'Add trigger',
                              dashed: true,
                              trailing: Icons.add,
                              onTap: () {},
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 36),
                  _NotesButton(),
                ],
              ),
            ),
            IntakeFooter(
              ctaLabel: 'Next: Lifestyle & Habits',
              onBack: () => context.go(RouteNames.step2b),
              onContinue: () => context.go(RouteNames.step4Labs),
            ),
          ],
        ),
      ),
    );
  }
}

Widget _sectionTitle(String text, double size) => Text(
      text,
      style: IntakeType.serif(size, FontWeight.w600, AppColors.deepInk),
    );

Widget _centeredTitle(String text, double size) => Center(
      child: _sectionTitle(text, size),
    );

Widget _cardTitle(String text) => Text(
      text,
      style: IntakeType.serif(20, FontWeight.w600, AppColors.deepInk),
    );

class _SymptomSearch extends StatelessWidget {
  const _SymptomSearch({required this.controller, required this.onSubmit});

  final TextEditingController controller;
  final VoidCallback onSubmit;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 56,
      padding: const EdgeInsets.only(left: 16, right: 8),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.headerText.withValues(alpha: 0.2)),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.headerText.withValues(alpha: 0.4),
            blurRadius: 26,
            spreadRadius: -14,
            offset: const Offset(0, 10),
          ),
          BoxShadow(
            color: AppColors.headerText.withValues(alpha: 0.06),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: <Widget>[
          Icon(Icons.search, size: 20, color: AppColors.headerText),
          const SizedBox(width: 12),
          Expanded(
            child: TextField(
              controller: controller,
              onSubmitted: (_) => onSubmit(),
              decoration: InputDecoration(
                hintText: 'Search symptoms...',
                hintStyle: IntakeType.sans(
                  15,
                  FontWeight.w400,
                  AppColors.headerText.withValues(alpha: 0.55),
                ),
                border: InputBorder.none,
              ),
              style: IntakeType.sans(15, FontWeight.w400, AppColors.deepInk),
            ),
          ),
          GestureDetector(
            onTap: onSubmit,
            child: Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: AppColors.terraCotta,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.add, size: 20, color: AppColors.cardSurface),
            ),
          ),
        ],
      ),
    );
  }
}

class _OutlineChip extends StatelessWidget {
  const _OutlineChip({
    required this.label,
    this.trailing,
    this.selected = false,
    this.dashed = false,
    required this.onTap,
  });

  final String label;
  final IconData? trailing;
  final bool selected;
  final bool dashed;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: selected ? AppColors.headerText : AppColors.cardSurface,
          borderRadius: BorderRadius.circular(999),
          border: dashed
              ? Border.all(color: AppColors.headerText, width: 1.5)
              : selected
                  ? null
                  : Border.all(
                      color: AppColors.headerText.withValues(alpha: 0.3),
                    ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            Text(
              label,
              style: IntakeType.sans(
                13,
                selected ? FontWeight.w500 : FontWeight.w500,
                selected ? AppColors.cardSurface : AppColors.headerText,
              ),
            ),
            if (trailing != null) ...<Widget>[
              const SizedBox(width: 8),
              Icon(
                trailing,
                size: 12,
                color: selected
                    ? AppColors.cardSurface.withValues(alpha: 0.7)
                    : AppColors.headerText.withValues(alpha: 0.7),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _BodyMap extends StatelessWidget {
  const _BodyMap({required this.selected, required this.onTap});

  final List<String> selected;
  final ValueChanged<String> onTap;

  static const Map<String, Offset> _labelOffsets = <String, Offset>{
    'Head': Offset(258, 14),
    'Neck': Offset(0, 48),
    'Arm': Offset(0, 110),
    'Chest': Offset(258, 86),
    'Abdomen': Offset(258, 154),
  };

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 342,
      height: 210,
      child: Stack(
        children: <Widget>[
          Positioned.fill(
            child: CustomPaint(painter: _BodyMapPainter()),
          ),
          for (final String location in _locations)
            Positioned(
              left: _labelOffsets[location]!.dx,
              top: _labelOffsets[location]!.dy,
              child: GestureDetector(
                onTap: () => onTap(location),
                child: Container(
                  width: 84,
                  height: 36,
                  padding: const EdgeInsets.symmetric(horizontal: 10),
                  decoration: BoxDecoration(
                    color: selected.contains(location)
                        ? AppColors.terraCotta
                        : AppColors.cardSurface,
                    borderRadius: BorderRadius.circular(999),
                    border: selected.contains(location)
                        ? null
                        : Border.all(
                            color: AppColors.headerText.withValues(alpha: 0.3),
                          ),
                    boxShadow: <BoxShadow>[
                      BoxShadow(
                        color: AppColors.headerText.withValues(alpha: 0.4),
                        blurRadius: 26,
                        spreadRadius: -14,
                        offset: const Offset(0, 10),
                      ),
                    ],
                  ),
                  child: Row(
                    children: <Widget>[
                      Icon(
                        Icons.place,
                        size: 14,
                        color: selected.contains(location)
                            ? AppColors.cardSurface
                            : AppColors.headerText,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        location,
                        style: IntakeType.sans(
                          12.5,
                          FontWeight.w500,
                          selected.contains(location)
                              ? AppColors.cardSurface
                              : AppColors.headerText,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

void _drawDashedLine(
  Canvas canvas,
  Offset start,
  Offset end,
  Paint paint, {
  double dash = 4,
  double gap = 4,
}) {
  final Offset delta = end - start;
  final double length = delta.distance;
  if (length == 0) return;
  final int steps = (length / (dash + gap)).floor();
  for (int i = 0; i < steps; i++) {
    final double from = (i * (dash + gap)) / length;
    final double to = (i * (dash + gap) + dash) / length;
    if (to > 1) break;
    canvas.drawLine(start + delta * from, start + delta * to, paint);
  }
}

class _BodyMapPainter extends CustomPainter {
  const _BodyMapPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final Paint fill = Paint()
      ..color = AppColors.headerText.withValues(alpha: 0.1)
      ..style = PaintingStyle.fill;
    final Paint stroke = Paint()
      ..color = AppColors.headerText.withValues(alpha: 0.45)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.6;

    final Path body = Path()
      ..moveTo(96, 208)
      ..lineTo(96, 132)
      ..cubicTo(96, 108, 114, 96, 142, 88)
      ..cubicTo(148, 86, 150, 82, 150, 76)
      ..lineTo(150, 62)
      ..lineTo(192, 62)
      ..lineTo(192, 76)
      ..cubicTo(192, 82, 194, 86, 200, 88)
      ..cubicTo(228, 96, 246, 108, 246, 132)
      ..lineTo(246, 208)
      ..close();
    canvas.drawPath(body, fill);
    canvas.drawPath(body, stroke);
    canvas.drawCircle(const Offset(171, 32), 24, fill);
    canvas.drawCircle(const Offset(171, 32), 24, stroke);

    final Paint guide = Paint()
      ..color = AppColors.headerText.withValues(alpha: 0.5)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;
    final Paint headGuide = Paint()
      ..color = AppColors.terraCotta
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;
    _drawDashedLine(canvas, const Offset(195, 32), const Offset(258, 32), headGuide);
    _drawDashedLine(canvas, const Offset(171, 66), const Offset(84, 66), guide);
    _drawDashedLine(canvas, const Offset(118, 128), const Offset(84, 128), guide);
    _drawDashedLine(canvas, const Offset(200, 104), const Offset(258, 104), guide);
    _drawDashedLine(canvas, const Offset(186, 172), const Offset(258, 172), guide);

    canvas.drawCircle(
      const Offset(171, 32),
      10,
      Paint()..color = AppColors.terraCotta.withValues(alpha: 0.18),
    );
    canvas.drawCircle(
      const Offset(171, 32),
      5,
      Paint()..color = AppColors.terraCotta,
    );
    for (final Offset point in <Offset>[
      const Offset(171, 66),
      const Offset(118, 128),
      const Offset(200, 104),
      const Offset(186, 172),
    ]) {
      canvas.drawCircle(
        point,
        5,
        Paint()
          ..color = AppColors.canvasBackground
          ..style = PaintingStyle.fill,
      );
      canvas.drawCircle(
        point,
        5,
        Paint()
          ..color = AppColors.headerText
          ..style = PaintingStyle.stroke
          ..strokeWidth = 1.8,
      );
    }
  }

  @override
  bool shouldRepaint(_BodyMapPainter oldDelegate) => false;
}

class _Segment extends StatelessWidget {
  const _Segment({
    required this.label,
    required this.active,
    required this.onTap,
  });

  final String label;
  final bool active;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: active ? AppColors.headerText : Colors.transparent,
          borderRadius: BorderRadius.circular(999),
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Text(
            label,
            style: IntakeType.sans(
              14,
              FontWeight.w500,
              active ? AppColors.cardSurface : AppColors.headerText,
            ),
          ),
        ),
      ),
    );
  }
}

class _Card extends StatelessWidget {
  const _Card({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.headerText.withValues(alpha: 0.2)),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.headerText.withValues(alpha: 0.4),
            blurRadius: 26,
            spreadRadius: -14,
            offset: const Offset(0, 10),
          ),
          BoxShadow(
            color: AppColors.headerText.withValues(alpha: 0.06),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: child,
    );
  }
}

class _NotesButton extends StatelessWidget {
  const _NotesButton();

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 48,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.headerText, width: 2),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.headerText.withValues(alpha: 0.4),
            blurRadius: 26,
            spreadRadius: -14,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: RichText(
        text: TextSpan(
          style: IntakeType.sans(14, FontWeight.w500, AppColors.headerText),
          children: <TextSpan>[
            const TextSpan(text: '+ Add additional notes '),
            TextSpan(
              text: '(Optional)',
              style: TextStyle(
                color: AppColors.headerText.withValues(alpha: 0.6),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
