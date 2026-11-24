import 'dart:math' as math;

import 'package:material_ui/material_ui.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import 'intake_screen_chrome.dart';

const List<String> _cardNames = <String>[
  '1. Symptoms',
  '2. Clinical Status & History',
  '3. Labs & Vitals',
  '4. Lab Record Details',
];

/// `/intake/step-5` — review and confirm.
class ReviewAndConfirmScreen extends StatefulWidget {
  const ReviewAndConfirmScreen({super.key});

  static const String routePath = RouteNames.step5Review;

  @override
  State<ReviewAndConfirmScreen> createState() => _ReviewAndConfirmScreenState();
}

class _ReviewAndConfirmScreenState extends State<ReviewAndConfirmScreen> {
  int _index = 0;

  void _goTo(int index) => setState(() => _index = index.clamp(0, 3));

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
            const IntakeHeader(step: 5),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: <Widget>[
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4),
                      child: Text(
                        'Step 5 of 5',
                        style: IntakeType.sans(
                          11.5,
                          FontWeight.w600,
                          AppColors.headerText,
                          spacing: 1.38,
                        ),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4),
                      child: Text(
                        'Review Your Data',
                        style: IntakeType.serif(
                          28,
                          FontWeight.w600,
                          AppColors.deepInk,
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Expanded(
                      child: SizedBox(
                        height: 646,
                        child: Stack(
                          clipBehavior: Clip.none,
                          children: <Widget>[
                            for (int i = 0; i < 4; i++)
                              _StackedCard(
                                index: i,
                                current: _index,
                                title: _cardNames[i],
                                onTap: () => _goTo(i),
                                child: _cardBody(i),
                              ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 4),
                    _CarouselControls(
                      index: _index,
                      onPrevious: () => _goTo(_index - 1),
                      onNext: () => _goTo(_index + 1),
                      onDot: _goTo,
                    ),
                  ],
                ),
              ),
            ),
            IntakeFooter(
              ctaLabel: 'Submit Assessment',
              onBack: () => context.go(RouteNames.step4Labs),
              onContinue: () => context.go(RouteNames.resultsReports),
            ),
          ],
        ),
      ),
    );
  }

  Widget _cardBody(int index) {
    return switch (index) {
      0 => const _SymptomsCard(),
      1 => const _ClinicalCard(),
      2 => const _LabsCard(),
      _ => const _RecordCard(),
    };
  }
}

class _StackedCard extends StatelessWidget {
  const _StackedCard({
    required this.index,
    required this.current,
    required this.title,
    required this.onTap,
    required this.child,
  });

  final int index;
  final int current;
  final String title;
  final VoidCallback onTap;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final int offset = index - current;
    if (offset < 0) {
      return AnimatedPositioned(
        duration: const Duration(milliseconds: 300),
        left: -420,
        top: -8,
        right: 420,
        height: 590,
        child: Opacity(opacity: 0, child: SizedBox(key: ValueKey<int>(index))),
      );
    }

    final double dy = switch (offset) {
      0 => 0,
      1 => 20,
      2 => 38,
      _ => 54,
    };
    final double scale = switch (offset) {
      0 => 1,
      1 => 0.97,
      2 => 0.94,
      _ => 0.91,
    };
    final double angle = switch (offset) {
      0 => 0,
      1 => 1.4,
      2 => -1.6,
      _ => 1,
    };
    final bool active = offset == 0;

    return AnimatedPositioned(
      duration: const Duration(milliseconds: 300),
      left: 0,
      right: 0,
      top: dy,
      height: 590,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        transform: Matrix4.identity()
          ..rotateZ(angle * math.pi / 180)
          ..scaleByDouble(scale, scale, 1, 1),
        transformAlignment: Alignment.bottomCenter,
        child: GestureDetector(
          onTap: active ? null : onTap,
          child: Container(
            decoration: BoxDecoration(
              color: AppColors.cardSurface,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppColors.borderSubtle),
              boxShadow: <BoxShadow>[
                BoxShadow(
                  color: AppColors.deepInk.withValues(alpha: 0.55),
                  blurRadius: 34,
                  spreadRadius: -18,
                  offset: const Offset(0, 22),
                ),
                BoxShadow(
                  color: AppColors.deepInk.withValues(alpha: 0.12),
                  blurRadius: 8,
                ),
              ],
            ),
            child: Stack(
              children: <Widget>[
                if (active)
                  Positioned(
                    top: -10,
                    left: 0,
                    right: 0,
                    child: Center(
                      child: Container(
                        width: 64,
                        height: 20,
                        decoration: BoxDecoration(
                          color: AppColors.headerText,
                          borderRadius: BorderRadius.circular(6),
                          boxShadow: <BoxShadow>[
                            BoxShadow(
                              color: AppColors.deepInk.withValues(alpha: 0.35),
                              blurRadius: 6,
                            ),
                          ],
                        ),
                        child: Center(
                          child: Container(
                            width: 44,
                            height: 4,
                            decoration: BoxDecoration(
                              color: AppColors.cardSurface.withValues(alpha: 0.35),
                              borderRadius: BorderRadius.circular(999),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(20, 24, 20, 20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: <Widget>[
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: <Widget>[
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: <Widget>[
                                Text(
                                  title,
                                  style: IntakeType.serif(
                                    22,
                                    FontWeight.w600,
                                    AppColors.deepInk,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  switch (index) {
                                    0 => 'From Step 3 · what you reported',
                                    1 => 'From Steps 2A and 2B',
                                    2 => 'From Step 4 · vitals and blood tests',
                                    _ => 'From Step 4 · test and report',
                                  },
                                  style: IntakeType.sans(
                                    12.5,
                                    FontWeight.w400,
                                    AppColors.headerText,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 12),
                          SizedBox(
                            width: 44,
                            height: 44,
                            child: Icon(
                              Icons.edit_outlined,
                              size: 18,
                              color: AppColors.headerText,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Container(
                        height: 1,
                        color: AppColors.headerText.withValues(alpha: 0.15),
                      ),
                      const SizedBox(height: 16),
                      Expanded(
                        child: SingleChildScrollView(
                          physics: const NeverScrollableScrollPhysics(),
                          child: child,
                        ),
                      ),
                    ],
                  ),
                ),
                if (active)
                  Positioned(
                    left: 0,
                    right: 0,
                    bottom: 0,
                    child: Container(
                      height: 17,
                      padding: const EdgeInsets.symmetric(horizontal: 20),
                      decoration: BoxDecoration(
                        color: AppColors.lightNeutralFill,
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: <Widget>[
                          Text(
                            offset == 3 ? title : 'Next · ${_nextName(index)}',
                            style: IntakeType.sans(
                              11,
                              FontWeight.w500,
                              AppColors.headerText,
                            ),
                          ),
                          Text(
                            '›',
                            style: IntakeType.sans(
                              11,
                              FontWeight.w500,
                              AppColors.headerText,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  String _nextName(int index) => switch (index) {
        0 => _cardNames[1],
        1 => _cardNames[2],
        _ => _cardNames[3],
      };
}

class _CarouselControls extends StatelessWidget {
  const _CarouselControls({
    required this.index,
    required this.onPrevious,
    required this.onNext,
    required this.onDot,
  });

  final int index;
  final VoidCallback onPrevious;
  final VoidCallback onNext;
  final ValueChanged<int> onDot;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: <Widget>[
        _RoundButton(
          icon: Icons.chevron_left,
          enabled: index > 0,
          onTap: onPrevious,
        ),
        Column(
          children: <Widget>[
            Text(
              '‹ Swipe to Review ›',
              style: IntakeType.sans(13, FontWeight.w500, AppColors.headerText),
            ),
            const SizedBox(height: 4),
            Row(
              children: <Widget>[
                for (int i = 0; i < 4; i++)
                  GestureDetector(
                    onTap: () => onDot(i),
                    child: SizedBox(
                      width: 24,
                      height: 24,
                      child: Center(
                        child: Container(
                          width: i == index ? 24 : 10,
                          height: 10,
                          decoration: BoxDecoration(
                            color: i == index
                                ? AppColors.headerText
                                : AppColors.headerText.withValues(alpha: 0.3),
                            borderRadius: BorderRadius.circular(999),
                          ),
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ],
        ),
        _RoundButton(
          icon: Icons.chevron_right,
          enabled: index < 3,
          onTap: onNext,
        ),
      ],
    );
  }
}

class _RoundButton extends StatelessWidget {
  const _RoundButton({
    required this.icon,
    required this.enabled,
    required this.onTap,
  });

  final IconData icon;
  final bool enabled;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: enabled ? onTap : null,
      child: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: AppColors.cardSurface,
          shape: BoxShape.circle,
          border: Border.all(color: AppColors.headerText.withValues(alpha: 0.35)),
        ),
        child: Icon(
          icon,
          size: 16,
          color: enabled ? AppColors.headerText : AppColors.textMuted,
        ),
      ),
    );
  }
}

Widget _label(String text) => Text(
      text.toUpperCase(),
      style: IntakeType.sans(
        11.5,
        FontWeight.w600,
        AppColors.headerText,
        spacing: 0.92,
      ),
    );

Widget _tag(String label, {bool alert = false}) => Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      decoration: BoxDecoration(
        color: alert
            ? AppColors.terraCotta.withValues(alpha: 0.1)
            : AppColors.headerText.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(
          color: alert
              ? AppColors.terraCotta.withValues(alpha: 0.4)
              : AppColors.headerText.withValues(alpha: 0.3),
        ),
      ),
      child: Text(
        label,
        style: IntakeType.sans(
          13.5,
          FontWeight.w500,
          alert ? AppColors.terraCotta : AppColors.deepInk,
        ),
      ),
    );

Widget _row(String left, String value, [String? suffix]) => Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: <Widget>[
          Expanded(
            child: Text(
              left,
              style: IntakeType.sans(13.5, FontWeight.w400, AppColors.headerText),
            ),
          ),
          Text(
            value,
            style: IntakeType.sans(15, FontWeight.w600, AppColors.deepInk),
          ),
          if (suffix != null) ...<Widget>[
            const SizedBox(width: 4),
            Text(
              suffix,
              style: IntakeType.sans(12.5, FontWeight.w400, AppColors.headerText),
            ),
          ],
        ],
      ),
    );

Widget _blockTitle(String text) {
  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: <Widget>[
      _label(text),
      const SizedBox(height: 8),
    ],
  );
}

class _SymptomsCard extends StatelessWidget {
  const _SymptomsCard();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        _blockTitle('Reported symptoms'),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: <Widget>[
            _tag('Headache'),
            _tag('Fatigue'),
            _tag('Chest Pain'),
          ],
        ),
        const SizedBox(height: 16),
        _blockTitle('Body location'),
        Row(
          children: <Widget>[
            Container(
              width: 78,
              height: 104,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: AppColors.headerText.withValues(alpha: 0.2),
                ),
                color: AppColors.canvasBackground,
              ),
              child: Icon(
                Icons.accessibility_new,
                size: 52,
                color: AppColors.headerText,
              ),
            ),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Wrap(
                  spacing: 8,
                  children: <Widget>[_tag('Head'), _tag('Chest (left)')],
                ),
                const SizedBox(height: 8),
                Text(
                  '2 pins placed',
                  style: IntakeType.sans(
                    12.5,
                    FontWeight.w400,
                    AppColors.headerText,
                  ),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 16),
        _blockTitle('Severity & duration'),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.canvasBackground,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            children: <Widget>[
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: <Widget>[
                  Text('Moderate',
                      style: IntakeType.sans(
                        15,
                        FontWeight.w600,
                        AppColors.deepInk,
                      )),
                  RichText(
                    text: TextSpan(
                      style: IntakeType.sans(
                        15,
                        FontWeight.w600,
                        AppColors.deepInk,
                      ),
                      children: <TextSpan>[
                        const TextSpan(text: '6 '),
                        TextSpan(
                          text: '/ 10',
                          style: IntakeType.sans(
                            12.5,
                            FontWeight.w400,
                            AppColors.headerText,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: <Widget>[
                  for (int i = 0; i < 10; i++)
                    Expanded(
                      child: Container(
                        margin: const EdgeInsets.only(right: 4),
                        height: 8,
                        decoration: BoxDecoration(
                          color: i < 6
                              ? AppColors.headerText
                              : AppColors.headerText.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(999),
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: <Widget>[
                  Text('Duration',
                      style: IntakeType.sans(
                        13.5,
                        FontWeight.w400,
                        AppColors.headerText,
                      )),
                  RichText(
                    text: TextSpan(
                      style: IntakeType.sans(
                        15,
                        FontWeight.w600,
                        AppColors.deepInk,
                      ),
                      children: <TextSpan>[
                        const TextSpan(text: '3 '),
                        TextSpan(
                          text: 'days',
                          style: IntakeType.sans(
                            12.5,
                            FontWeight.w400,
                            AppColors.headerText,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        _blockTitle('Triggers'),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: <Widget>[
            _tag('Exertion'),
            _tag('Stress'),
            _tag('After meals'),
          ],
        ),
      ],
    );
  }
}

class _ClinicalCard extends StatelessWidget {
  const _ClinicalCard();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        _blockTitle('Active conditions'),
        Wrap(spacing: 8, children: <Widget>[_tag('Hypertension'), _tag('Dyslipidemia')]),
        const SizedBox(height: 16),
        _blockTitle('Current medications'),
        _row('Amlodipine', '5 mg', 'Once daily'),
        _row('Metformin', '500 mg', 'Twice daily'),
        const SizedBox(height: 16),
        _blockTitle('Known allergies'),
        Wrap(children: <Widget>[_tag('Penicillin', alert: true)]),
        const SizedBox(height: 16),
        _blockTitle('Family history'),
        _row('Father', 'Heart attack', 'at 52'),
        _row('Mother', 'Type 2 diabetes', 'at 61'),
      ],
    );
  }
}

class _LabsCard extends StatelessWidget {
  const _LabsCard();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  _label('Body'),
                  const SizedBox(height: 8),
                  _row('Height', '5 ft 9 in'),
                  _row('Weight', '172', 'lbs'),
                  _row('Waist', '34', 'in'),
                ],
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  _label('Heart vitals'),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.canvasBackground,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Text('Blood pressure',
                            style: IntakeType.sans(
                              12.5,
                              FontWeight.w400,
                              AppColors.headerText,
                            )),
                        const SizedBox(height: 4),
                        Text('120/80',
                            style: IntakeType.sans(
                              26,
                              FontWeight.w600,
                              AppColors.deepInk,
                            )),
                        Text('mmHg',
                            style: IntakeType.sans(
                              12.5,
                              FontWeight.w400,
                              AppColors.headerText,
                            )),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        _blockTitle('Blood test panel'),
        for (final _TestResult result in const <_TestResult>[
          _TestResult('HbA1c', 'In range · < 5.7', '5.4', '%', false),
          _TestResult('Total cholesterol', 'In range · < 200', '195', 'mg/dL', false),
          _TestResult('LDL cholesterol', 'High · < 100', '112', 'mg/dL', true),
          _TestResult('Serum creatinine', 'In range · 0.6–1.3', '1.0', 'mg/dL', false),
          _TestResult('Fasting glucose', 'In range · 70–99', '92', 'mg/dL', false),
        ])
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 4),
            child: Row(
              children: <Widget>[
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Text(result.name,
                          style: IntakeType.sans(
                            13.5,
                            FontWeight.w400,
                            AppColors.deepInk,
                          )),
                      const SizedBox(height: 2),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: result.alert
                              ? AppColors.terraCotta.withValues(alpha: 0.1)
                              : AppColors.headerText.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: Text(
                          result.range,
                          style: IntakeType.sans(
                            11.5,
                            FontWeight.w500,
                            result.alert
                                ? AppColors.terraCotta
                                : AppColors.headerText,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                Text(result.value,
                    style: IntakeType.sans(
                      15,
                      FontWeight.w600,
                      AppColors.deepInk,
                    )),
                const SizedBox(width: 4),
                Text(result.unit,
                    style: IntakeType.sans(
                      12.5,
                      FontWeight.w400,
                      AppColors.headerText,
                    )),
              ],
            ),
          ),
      ],
    );
  }
}

class _TestResult {
  const _TestResult(this.name, this.range, this.value, this.unit, this.alert);

  final String name;
  final String range;
  final String value;
  final String unit;
  final bool alert;
}

class _RecordCard extends StatelessWidget {
  const _RecordCard();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        _blockTitle('Test details'),
        _row('Test date', '12 Oct 2026'),
        _row('Lab / clinic', 'City Diagnostics'),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: <Widget>[
              Text('Fasting when tested',
                  style: IntakeType.sans(
                    13.5,
                    FontWeight.w400,
                    AppColors.headerText,
                  )),
              Row(
                children: <Widget>[
                  Text('Yes',
                      style: IntakeType.sans(
                        15,
                        FontWeight.w600,
                        AppColors.deepInk,
                      )),
                  const SizedBox(width: 8),
                  Container(
                    width: 44,
                    height: 24,
                    padding: const EdgeInsets.all(2),
                    decoration: BoxDecoration(
                      color: AppColors.headerText,
                      borderRadius: BorderRadius.circular(999),
                    ),
                    alignment: Alignment.centerRight,
                    child: Container(
                      width: 20,
                      height: 20,
                      decoration: BoxDecoration(
                        color: AppColors.cardSurface,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        _blockTitle('Lab report'),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppColors.canvasBackground,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: AppColors.headerText.withValues(alpha: 0.25),
            ),
          ),
          child: Column(
            children: <Widget>[
              Container(
                height: 170,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: AppColors.cardSurface,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: AppColors.headerText.withValues(alpha: 0.2),
                  ),
                ),
                child: Icon(
                  Icons.description_outlined,
                  size: 108,
                  color: AppColors.headerText.withValues(alpha: 0.35),
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: <Widget>[
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Text(
                          'lab-report-12-oct.jpg',
                          overflow: TextOverflow.ellipsis,
                          style: IntakeType.sans(
                            14.5,
                            FontWeight.w600,
                            AppColors.deepInk,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '1.2 MB · photo of report',
                          style: IntakeType.sans(
                            12.5,
                            FontWeight.w400,
                            AppColors.headerText,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: AppColors.headerText.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(999),
                      border: Border.all(
                        color: AppColors.headerText.withValues(alpha: 0.3),
                      ),
                    ),
                    child: Text(
                      'Uploaded',
                      style: IntakeType.sans(
                        12,
                        FontWeight.w500,
                        AppColors.headerText,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }
}
