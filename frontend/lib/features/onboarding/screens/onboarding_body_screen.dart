import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:material_ui/material_ui.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../navigation/onboarding_navigation.dart';
import '../providers/onboarding_provider.dart';
import '../widgets/onboarding_shell.dart';
import '../widgets/onboarding_type.dart';

/// Onboarding 4 — Now, your body.
///
/// Height, weight and waist are optional. BMI and waist-to-height are derived
/// live from whatever the user has entered.
class OnboardingBodyScreen extends ConsumerStatefulWidget {
  const OnboardingBodyScreen({super.key});

  static const String routePath = RouteNames.onboardingBody;

  @override
  ConsumerState<OnboardingBodyScreen> createState() =>
      _OnboardingBodyScreenState();
}

class _OnboardingBodyScreenState extends ConsumerState<OnboardingBodyScreen> {
  late final TextEditingController _weightController;
  late final TextEditingController _waistController;

  @override
  void initState() {
    super.initState();
    final OnboardingState state = ref.read(onboardingProvider);
    _weightController = TextEditingController(text: state.weight);
    _waistController = TextEditingController(text: state.waist);
  }

  @override
  void dispose() {
    _weightController.dispose();
    _waistController.dispose();
    super.dispose();
  }

  void _setUnit(String unit) {
    final OnboardingController controller =
        ref.read(onboardingProvider.notifier);
    controller.setWeightUnit(unit);
    _weightController.text = ref.read(onboardingProvider).weight;
    _weightController.selection = TextSelection.collapsed(
      offset: _weightController.text.length,
    );
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final OnboardingState state = ref.watch(onboardingProvider);
    final OnboardingController controller =
        ref.read(onboardingProvider.notifier);

    return OnboardingShell(
      step: 4,
      title: 'Now, your body',
      subtitle: 'Add what you know. Blanks are fine.',
      ctaLabel: 'Share my daily habits',
      onCta: () => OnboardingNavigation.next(
        context,
        RouteNames.onboardingHabits,
      ),
      onBack: () => OnboardingNavigation.back(
        context,
        RouteNames.onboardingProfile,
      ),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            const SizedBox(height: 24),
            _BmiPanel(state: state),
            const SizedBox(height: 24),
            _MeasurementsCard(
              state: state,
              controller: controller,
              weightController: _weightController,
              waistController: _waistController,
              onUnitChanged: _setUnit,
            ),
          ],
        ),
      ),
    );
  }
}

double _heightInches(OnboardingState state) =>
    (state.heightFt * 12 + state.heightIn).toDouble();

double _bmiValue(OnboardingState state) {
  final double? raw = double.tryParse(state.weight.trim());
  if (raw == null || raw <= 0) return 0;
  final double kg = state.weightUnit == 'kg' ? raw : raw / 2.2046;
  final double metres = _heightInches(state) * 0.0254;
  if (metres <= 0) return 0;
  return kg / (metres * metres);
}

double _waistToHeight(OnboardingState state) {
  final double? waist = double.tryParse(state.waist.trim());
  final double inches = _heightInches(state);
  if (waist == null || waist <= 0 || inches <= 0) return 0;
  return waist / inches;
}

class _BmiPanel extends StatelessWidget {
  const _BmiPanel({required this.state});

  final OnboardingState state;

  @override
  Widget build(BuildContext context) {
    final double bmi = _bmiValue(state);
    final double ratio = _waistToHeight(state);

    String label;
    Color labelColor;
    if (bmi <= 0) {
      label = 'Add your weight';
      labelColor = AppColors.onboardingHint;
    } else if (bmi < 18.5) {
      label = 'Below healthy range';
      labelColor = AppColors.alertMedium;
    } else if (bmi < 25) {
      label = 'Healthy range';
      labelColor = AppColors.mutedGreen;
    } else if (bmi < 30) {
      label = 'Above healthy range';
      labelColor = AppColors.alertMedium;
    } else {
      label = 'Well above healthy range';
      labelColor = AppColors.terraCotta;
    }

    final double pinPercent = bmi <= 0
        ? 0
        : (bmi - 15) / 25 * 100;
    final double clampedPin = pinPercent.clamp(0, 100).toDouble();

    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: <Widget>[
        Container(
          width: 112,
          height: 176,
          decoration: BoxDecoration(
            color: AppColors.headerText.withValues(alpha: 0.07),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(
            Icons.accessibility_new_rounded,
            size: 104,
            color: AppColors.headerText,
          ),
        ),
        const SizedBox(width: 20),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Text(
                'BMI',
                style: OnboardingType.sans(
                  13,
                  FontWeight.w500,
                  AppColors.onboardingMutedInk,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                bmi <= 0 ? '—' : bmi.toStringAsFixed(1),
                style: OnboardingType.serif(
                  36,
                  FontWeight.w600,
                  AppColors.deepInk,
                  height: 38 / 36,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                label,
                style: OnboardingType.sans(12, FontWeight.w600, labelColor),
              ),
              const SizedBox(height: 16),
              Stack(
                children: <Widget>[
                  Row(
                    children: const <Widget>[
                      Expanded(
                        flex: 14,
                        child: _GaugeSegment(color: AppColors.onboardingGaugeLow),
                      ),
                      Expanded(
                        flex: 26,
                        child: _GaugeSegment(
                          color: AppColors.onboardingGaugeHealthy,
                        ),
                      ),
                      Expanded(
                        flex: 20,
                        child: _GaugeSegment(color: AppColors.onboardingGaugeMid),
                      ),
                      Expanded(
                        flex: 40,
                        child: _GaugeSegment(color: AppColors.onboardingGaugeHigh),
                      ),
                    ],
                  ),
                  if (bmi > 0)
                    Positioned(
                      left: clampedPin,
                      top: -5,
                      child: Container(
                        width: 18,
                        height: 18,
                        decoration: BoxDecoration(
                          color: AppColors.deepInk,
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: AppColors.authInputSurface,
                            width: 3,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 16),
              Text.rich(
                TextSpan(
                  style: OnboardingType.sans(
                    12,
                    FontWeight.w300,
                    AppColors.onboardingMutedInk,
                  ),
                  children: <InlineSpan>[
                    const TextSpan(text: 'Waist to height '),
                    TextSpan(
                      text:
                          ratio <= 0 ? '—' : ratio.toStringAsFixed(2),
                      style: OnboardingType.sans(
                        12,
                        FontWeight.w700,
                        AppColors.deepInk,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _GaugeSegment extends StatelessWidget {
  const _GaugeSegment({required this.color});

  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(height: 8, color: color);
  }
}

class _MeasurementsCard extends StatelessWidget {
  const _MeasurementsCard({
    required this.state,
    required this.controller,
    required this.weightController,
    required this.waistController,
    required this.onUnitChanged,
  });

  final OnboardingState state;
  final OnboardingController controller;
  final TextEditingController weightController;
  final TextEditingController waistController;
  final ValueChanged<String> onUnitChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.authInputSurface,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.headerText.withValues(alpha: 0.2)),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.headerText.withValues(alpha: 0.45),
            offset: const Offset(0, 12),
            blurRadius: 28,
            spreadRadius: -16,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          Text(
            'Body Measurements',
            style: OnboardingType.serif(
              20,
              FontWeight.w600,
              AppColors.deepInk,
              height: 24 / 20,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: <Widget>[
              Expanded(
                child: _HeightStepper(
                  label: 'ft',
                  value: state.heightFt,
                  onDecrease: () => controller.changeHeightFeet(-1),
                  onIncrease: () => controller.changeHeightFeet(1),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _HeightStepper(
                  label: 'in',
                  value: state.heightIn,
                  onDecrease: () => controller.changeHeightInches(-1),
                  onIncrease: () => controller.changeHeightInches(1),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Row(
                      children: <Widget>[
                        Text(
                          'Weight',
                          style: OnboardingType.sans(
                            14,
                            FontWeight.w500,
                            AppColors.onboardingMutedInk,
                          ),
                        ),
                        const Spacer(),
                        _UnitToggle(
                          value: state.weightUnit,
                          onChanged: onUnitChanged,
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    _UnderlinedField(
                      controller: weightController,
                      hint: 'Tap to enter',
                      label: 'Weight',
                      onChanged: controller.setWeight,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 24),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Row(
                      children: <Widget>[
                        Text(
                          'Waist',
                          style: OnboardingType.sans(
                            14,
                            FontWeight.w500,
                            AppColors.onboardingMutedInk,
                          ),
                        ),
                        const Spacer(),
                        Text(
                          'in',
                          style: OnboardingType.sans(
                            12,
                            FontWeight.w500,
                            AppColors.onboardingMutedInk,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    _UnderlinedField(
                      controller: waistController,
                      hint: 'e.g. 34',
                      label: 'Waist circumference',
                      onChanged: controller.setWaist,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _HeightStepper extends StatelessWidget {
  const _HeightStepper({
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
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: <Widget>[
            _SmallCircleButton(
              icon: Icons.remove_rounded,
              label: 'Less $label',
              onTap: onDecrease,
            ),
            Text(
              '$value $label',
              style: OnboardingType.sans(
                20,
                FontWeight.w600,
                AppColors.headerText,
              ),
            ),
            _SmallCircleButton(
              icon: Icons.add_rounded,
              label: 'More $label',
              onTap: onIncrease,
            ),
          ],
        ),
      ],
    );
  }
}

class _SmallCircleButton extends StatelessWidget {
  const _SmallCircleButton({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: label,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(20),
          child: Ink(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(
                color: AppColors.headerText.withValues(alpha: 0.35),
              ),
            ),
            child: Icon(icon, size: 18, color: AppColors.headerText),
          ),
        ),
      ),
    );
  }
}

class _UnitToggle extends StatelessWidget {
  const _UnitToggle({required this.value, required this.onChanged});

  final String value;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(2),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.headerText.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          for (final String unit in <String>['lb', 'kg'])
            GestureDetector(
              onTap: () => onChanged(unit),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: value == unit
                      ? AppColors.headerText
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text(
                  unit,
                  style: OnboardingType.sans(
                    11,
                    FontWeight.w600,
                    value == unit
                        ? AppColors.cardSurface
                        : AppColors.onboardingMutedInk,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _UnderlinedField extends StatelessWidget {
  const _UnderlinedField({
    required this.controller,
    required this.hint,
    required this.label,
    required this.onChanged,
  });

  final TextEditingController controller;
  final String hint;
  final String label;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: label,
      child: Container(
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(color: AppColors.headerText, width: 2),
          ),
        ),
        child: TextField(
          controller: controller,
          onChanged: onChanged,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          style: OnboardingType.sans(
            22,
            FontWeight.w600,
            AppColors.headerText,
          ),
          decoration: InputDecoration(
            isDense: true,
            border: InputBorder.none,
            hintText: hint,
            hintStyle: OnboardingType.sans(
              15,
              FontWeight.w400,
              AppColors.onboardingHint,
            ),
          ),
        ),
      ),
    );
  }
}
