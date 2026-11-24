import 'package:material_ui/material_ui.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import 'intake_screen_chrome.dart';

/// `/intake/step-4` — labs and vitals. Accordion supports both reference states.
class LabsAndVitalsScreen extends StatefulWidget {
  const LabsAndVitalsScreen({super.key});

  static const String routePath = RouteNames.step4Labs;

  @override
  State<LabsAndVitalsScreen> createState() => _LabsAndVitalsScreenState();
}

class _LabsAndVitalsScreenState extends State<LabsAndVitalsScreen> {
  final Set<int> _open = <int>{0};
  int _weightUnit = 0;
  int _heightFeet = 5;
  int _heightInches = 9;
  int _systolic = 120;
  int _diastolic = 80;

  void _toggle(int index) {
    setState(() {
      if (_open.contains(index)) {
        _open.remove(index);
      } else {
        _open.add(index);
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
            const IntakeHeader(step: 4),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(20, 28, 20, 32),
                children: <Widget>[
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: Row(
                      children: <Widget>[
                        Text(
                          'Labs & Vitals',
                          style: IntakeType.serif(
                            26,
                            FontWeight.w600,
                            AppColors.deepInk,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(999),
                            border: Border.all(
                              color: AppColors.headerText.withValues(alpha: 0.3),
                            ),
                          ),
                          child: Text(
                            'Optional',
                            style: IntakeType.sans(
                              11,
                              FontWeight.w500,
                              AppColors.headerText.withValues(alpha: 0.8),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.only(left: 4, top: 6),
                    child: Text(
                      'Add what you have and skip the rest. Tap a row to open it.',
                      style: IntakeType.sans(
                        13.5,
                        FontWeight.w300,
                        AppColors.headerText.withValues(alpha: 0.85),
                        height: 20 / 13.5,
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  _Section(
                    title: 'Body Measurements',
                    subtitle: '2 of 3 added',
                    open: _open.contains(0),
                    onToggle: () => _toggle(0),
                    child: _BodySection(
                      feet: _heightFeet,
                      inches: _heightInches,
                      weightUnit: _weightUnit,
                      onFeet: (int value) =>
                          setState(() => _heightFeet = value.clamp(0, 8)),
                      onInches: (int value) =>
                          setState(() => _heightInches = value.clamp(0, 11)),
                      onUnit: (int value) => setState(() => _weightUnit = value),
                    ),
                  ),
                  const SizedBox(height: 20),
                  _Section(
                    title: 'Heart Vitals',
                    subtitle: '2 of 2 added',
                    open: _open.contains(1),
                    onToggle: () => _toggle(1),
                    child: _HeartSection(
                      systolic: _systolic,
                      diastolic: _diastolic,
                      onSystolic: (int value) =>
                          setState(() => _systolic = value.clamp(0, 250)),
                      onDiastolic: (int value) =>
                          setState(() => _diastolic = value.clamp(0, 180)),
                    ),
                  ),
                  const SizedBox(height: 20),
                  _Section(
                    title: 'Blood Test Results',
                    subtitle: '3 of 6 added',
                    open: _open.contains(2),
                    onToggle: () => _toggle(2),
                    child: const _BloodSection(),
                  ),
                  const SizedBox(height: 20),
                  _Section(
                    title: 'Lab Record Details',
                    subtitle: 'Not added yet',
                    open: _open.contains(3),
                    onToggle: () => _toggle(3),
                    child: const _LabRecordSection(),
                  ),
                ],
              ),
            ),
            IntakeFooter(
              ctaLabel: 'Next: Review & Confirm',
              onBack: () => context.go(RouteNames.step3Symptoms),
              onContinue: () => context.go(RouteNames.step5Review),
            ),
          ],
        ),
      ),
    );
  }
}

class _Section extends StatelessWidget {
  const _Section({
    required this.title,
    required this.subtitle,
    required this.open,
    required this.onToggle,
    required this.child,
  });

  final String title;
  final String subtitle;
  final bool open;
  final VoidCallback onToggle;
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
            color: AppColors.headerText.withValues(alpha: 0.45),
            blurRadius: 28,
            spreadRadius: -16,
            offset: const Offset(0, 12),
          ),
          BoxShadow(
            color: AppColors.headerText.withValues(alpha: 0.06),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          GestureDetector(
            onTap: onToggle,
            child: Row(
              children: <Widget>[
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Text(
                        title,
                        style: IntakeType.serif(
                          21,
                          FontWeight.w600,
                          AppColors.deepInk,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        subtitle,
                        style: IntakeType.sans(
                          12.5,
                          FontWeight.w300,
                          AppColors.headerText.withValues(alpha: 0.7),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Container(
                  height: 36,
                  padding: const EdgeInsets.symmetric(horizontal: 14),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(
                      color: AppColors.headerText.withValues(alpha: 0.3),
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      Icon(
                        open ? Icons.expand_more : Icons.expand_less,
                        size: 16,
                        color: AppColors.headerText,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        open ? 'Close' : 'Open',
                        style: IntakeType.sans(
                          13,
                          FontWeight.w500,
                          AppColors.headerText,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          if (open) ...<Widget>[
            const SizedBox(height: 24),
            Container(
              height: 1,
              color: AppColors.headerText.withValues(alpha: 0.1),
            ),
            const SizedBox(height: 24),
            child,
          ],
        ],
      ),
    );
  }
}

class _BodySection extends StatelessWidget {
  const _BodySection({
    required this.feet,
    required this.inches,
    required this.weightUnit,
    required this.onFeet,
    required this.onInches,
    required this.onUnit,
  });

  final int feet;
  final int inches;
  final int weightUnit;
  final ValueChanged<int> onFeet;
  final ValueChanged<int> onInches;
  final ValueChanged<int> onUnit;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        Text(
          'Height',
          style: IntakeType.sans(14, FontWeight.w500, AppColors.headerText),
        ),
        const SizedBox(height: 12),
        Row(
          children: <Widget>[
            Expanded(
              child: _HeightField(
                label: 'Feet',
                value: feet,
                unit: 'ft',
                onDecrease: () => onFeet(feet - 1),
                onIncrease: () => onFeet(feet + 1),
              ),
            ),
            const SizedBox(width: 24),
            Expanded(
              child: _HeightField(
                label: 'Inches',
                value: inches,
                unit: 'in',
                onDecrease: () => onInches(inches - 1),
                onIncrease: () => onInches(inches + 1),
              ),
            ),
          ],
        ),
        const SizedBox(height: 32),
        Text(
          'Weight',
          style: IntakeType.sans(14, FontWeight.w500, AppColors.headerText),
        ),
        const SizedBox(height: 4),
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: <Widget>[
            Expanded(
              child: Text(
                '172',
                style: IntakeType.sans(
                  24,
                  FontWeight.w500,
                  AppColors.headerText,
                ),
              ),
            ),
            Container(
              width: 2,
              height: 24,
              color: AppColors.terraCotta,
            ),
            const SizedBox(width: 12),
            Container(
              padding: const EdgeInsets.all(2),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(999),
                border: Border.all(
                  color: AppColors.headerText.withValues(alpha: 0.3),
                ),
              ),
              child: Row(
                children: <Widget>[
                  for (int i = 0; i < 2; i++)
                    GestureDetector(
                      onTap: () => onUnit(i),
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: weightUnit == i ? AppColors.headerText : null,
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: Text(
                          i == 0 ? 'lbs' : 'kg',
                          style: IntakeType.sans(
                            12,
                            FontWeight.w500,
                            weightUnit == i
                                ? AppColors.cardSurface
                                : AppColors.headerText,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 32),
        Text(
          'Waist circumference',
          style: IntakeType.sans(14, FontWeight.w500, AppColors.headerText),
        ),
        const SizedBox(height: 4),
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: <Widget>[
            Expanded(
              child: Text(
                'Tap to enter',
                style: IntakeType.sans(
                  18,
                  FontWeight.w400,
                  AppColors.headerText.withValues(alpha: 0.4),
                ),
              ),
            ),
            Text(
              'in',
              style: IntakeType.sans(
                13,
                FontWeight.w500,
                AppColors.headerText.withValues(alpha: 0.7),
              ),
            ),
          ],
        ),
        Container(
          height: 2,
          color: AppColors.headerText.withValues(alpha: 0.3),
        ),
      ],
    );
  }
}

class _HeightField extends StatelessWidget {
  const _HeightField({
    required this.label,
    required this.value,
    required this.unit,
    required this.onDecrease,
    required this.onIncrease,
  });

  final String label;
  final int value;
  final String unit;
  final VoidCallback onDecrease;
  final VoidCallback onIncrease;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(
          label,
          style: IntakeType.sans(
            13,
            FontWeight.w500,
            AppColors.headerText.withValues(alpha: 0.7),
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: <Widget>[
            StepperButton(icon: Icons.remove, onTap: onDecrease),
            const SizedBox(width: 10),
            SizedBox(
              width: 34,
              child: Text(
                '$value',
                textAlign: TextAlign.center,
                style: IntakeType.sans(
                  28,
                  FontWeight.w600,
                  AppColors.headerText,
                  height: 1,
                ),
              ),
            ),
            const SizedBox(width: 10),
            StepperButton(icon: Icons.add, onTap: onIncrease),
          ],
        ),
        const SizedBox(height: 6),
        Text(
          unit,
          style: IntakeType.sans(
            12,
            FontWeight.w300,
            AppColors.headerText.withValues(alpha: 0.6),
          ),
        ),
      ],
    );
  }
}

class _HeartSection extends StatelessWidget {
  const _HeartSection({
    required this.systolic,
    required this.diastolic,
    required this.onSystolic,
    required this.onDiastolic,
  });

  final int systolic;
  final int diastolic;
  final ValueChanged<int> onSystolic;
  final ValueChanged<int> onDiastolic;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 20),
      decoration: BoxDecoration(
        color: AppColors.headerText.withValues(alpha: 0.8),
        borderRadius: BorderRadius.circular(24),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.deepInk.withValues(alpha: 0.55),
            blurRadius: 30,
            spreadRadius: -16,
            offset: const Offset(0, 18),
          ),
        ],
      ),
      child: Column(
        children: <Widget>[
          Row(
            children: <Widget>[
              const Icon(Icons.favorite_border,
                  size: 20, color: AppColors.cardSurface),
              const SizedBox(width: 6),
              Text(
                'BLOOD PRESSURE',
                style: IntakeType.sans(
                  11,
                  FontWeight.w500,
                  AppColors.cardSurface.withValues(alpha: 0.7),
                  spacing: 1.76,
                ),
              ),
              const Spacer(),
              Text(
                'mmHg',
                style: IntakeType.sans(
                  11,
                  FontWeight.w500,
                  AppColors.cardSurface.withValues(alpha: 0.7),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 16),
            decoration: BoxDecoration(
              color: AppColors.headerText,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              children: <Widget>[
                Expanded(
                  child: _PressureValue(
                    label: 'SYS',
                    value: systolic,
                    onDecrease: () => onSystolic(systolic - 1),
                    onIncrease: () => onSystolic(systolic + 1),
                  ),
                ),
                Container(
                  width: 1,
                  height: 80,
                  color: AppColors.cardSurface.withValues(alpha: 0.25),
                ),
                Expanded(
                  child: _PressureValue(
                    label: 'DIA',
                    value: diastolic,
                    onDecrease: () => onDiastolic(diastolic - 1),
                    onIncrease: () => onDiastolic(diastolic + 1),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'Use − and + to match the reading on your cuff',
            textAlign: TextAlign.center,
            style: IntakeType.sans(
              11.5,
              FontWeight.w300,
              AppColors.cardSurface.withValues(alpha: 0.7),
            ),
          ),
        ],
      ),
    );
  }
}

class _PressureValue extends StatelessWidget {
  const _PressureValue({
    required this.label,
    required this.value,
    required this.onDecrease,
    required this.onIncrease,
  });

  final String label;
  final int value;
  final VoidCallback onDecrease;
  final VoidCallback onIncrease;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        Text(
          label,
          style: IntakeType.sans(
            11,
            FontWeight.w500,
            AppColors.cardSurface.withValues(alpha: 0.7),
            spacing: 1.76,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          '$value',
          style: IntakeType.sans(
            52,
            FontWeight.w300,
            AppColors.cardSurface,
            height: 56 / 52,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            StepperButton(
              size: 40,
              icon: Icons.remove,
              onTap: onDecrease,
            ),
            const SizedBox(width: 12),
            StepperButton(
              size: 40,
              icon: Icons.add,
              onTap: onIncrease,
            ),
          ],
        ),
      ],
    );
  }
}

class _BloodSection extends StatelessWidget {
  const _BloodSection();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        for (final _LabValue value in const <_LabValue>[
          _LabValue('HbA1c', '5.4', '%', 'Ref: < 5.7%'),
          _LabValue('Total Cholesterol', '195', 'mg/dL', 'Ref: < 200 mg/dL'),
          _LabValue('HDL Cholesterol', '52', 'mg/dL', 'Ref: > 40 mg/dL'),
          _LabValue('LDL Cholesterol', 'Tap to enter', 'mg/dL', 'Ref: < 100 mg/dL'),
          _LabValue('Serum Creatinine', 'Tap to enter', 'mg/dL', 'Ref: 0.6 to 1.3 mg/dL'),
          _LabValue('Fasting Blood Glucose', 'Tap to enter', 'mg/dL', 'Ref: 70 to 99 mg/dL'),
        ])
          Padding(
            padding: const EdgeInsets.only(bottom: 32),
            child: _LabField(value: value),
          ),
      ],
    );
  }
}

class _LabValue {
  const _LabValue(this.name, this.value, this.unit, this.reference);

  final String name;
  final String value;
  final String unit;
  final String reference;
}

class _LabField extends StatelessWidget {
  const _LabField({required this.value});

  final _LabValue value;

  @override
  Widget build(BuildContext context) {
    final bool empty = value.value == 'Tap to enter';
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(
          value.name,
          style: IntakeType.sans(14, FontWeight.w500, AppColors.headerText),
        ),
        const SizedBox(height: 4),
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: <Widget>[
            Expanded(
              child: Text(
                value.value,
                style: IntakeType.sans(
                  empty ? 18 : 24,
                  empty ? FontWeight.w400 : FontWeight.w500,
                  AppColors.headerText.withValues(alpha: empty ? 0.4 : 1),
                ),
              ),
            ),
            SizedBox(
              width: 52,
              child: Text(
                value.unit,
                textAlign: TextAlign.right,
                style: IntakeType.sans(
                  13,
                  FontWeight.w500,
                  AppColors.headerText.withValues(alpha: 0.7),
                ),
              ),
            ),
          ],
        ),
        Container(
          height: 2,
          color: AppColors.headerText.withValues(alpha: 0.3),
        ),
        const SizedBox(height: 8),
        Text(
          value.reference,
          style: IntakeType.sans(
            12,
            FontWeight.w300,
            AppColors.headerText.withValues(alpha: 0.65),
          ),
        ),
      ],
    );
  }
}

class _LabRecordSection extends StatelessWidget {
  const _LabRecordSection();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        _UnderlineField(label: 'Test date', hint: 'MM / DD / YYYY', icon: Icons.calendar_month_outlined),
        const SizedBox(height: 32),
        _UnderlineField(label: 'Lab name', hint: 'Name of lab or clinic'),
        const SizedBox(height: 32),
        Text(
          'Photo of your report',
          style: IntakeType.sans(14, FontWeight.w500, AppColors.headerText),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: AppColors.headerText.withValues(alpha: 0.4),
              width: 2,
              style: BorderStyle.solid,
            ),
          ),
          child: Row(
            children: <Widget>[
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: AppColors.headerText.withValues(alpha: 0.3),
                  ),
                ),
                child: Icon(
                  Icons.camera_alt_outlined,
                  size: 20,
                  color: AppColors.headerText,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Text(
                      'Attach or take a photo',
                      style: IntakeType.sans(
                        14,
                        FontWeight.w500,
                        AppColors.headerText,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'JPG or PNG, up to 10 MB',
                      style: IntakeType.sans(
                        12,
                        FontWeight.w300,
                        AppColors.headerText.withValues(alpha: 0.7),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(999),
                  border: Border.all(
                    color: AppColors.headerText.withValues(alpha: 0.4),
                  ),
                ),
                child: Text(
                  'Upload',
                  style: IntakeType.sans(
                    13,
                    FontWeight.w500,
                    AppColors.headerText,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _UnderlineField extends StatelessWidget {
  const _UnderlineField({
    required this.label,
    required this.hint,
    this.icon,
  });

  final String label;
  final String hint;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(
          label,
          style: IntakeType.sans(14, FontWeight.w500, AppColors.headerText),
        ),
        const SizedBox(height: 4),
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: <Widget>[
            Expanded(
              child: Text(
                hint,
                style: IntakeType.sans(
                  18,
                  FontWeight.w400,
                  AppColors.headerText.withValues(alpha: 0.4),
                ),
              ),
            ),
            if (icon != null)
              Icon(icon, size: 20, color: AppColors.headerText.withValues(alpha: 0.7)),
          ],
        ),
        Container(
          height: 2,
          color: AppColors.headerText.withValues(alpha: 0.3),
        ),
      ],
    );
  }
}
