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
    if (unit == ref.read(onboardingProvider).weightUnit) return;
    ref.read(onboardingProvider.notifier).setWeightUnit(unit);
    final String converted = ref.read(onboardingProvider).weight;
    _weightController.text = converted;
    _weightController.selection = TextSelection.collapsed(
      offset: converted.length,
    );
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
        RouteNames.onboardingBloodType,
      ),
      child: LayoutBuilder(
        builder: (BuildContext context, BoxConstraints constraints) {
          return SingleChildScrollView(
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              // OnboardingShell already supplies 20px on each side, so this
              // completes the requested fromLTRB(20, 0, 20, 16) content inset.
              child: Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: <Widget>[
                    _FigureBmiRow(state: state),
                    const SizedBox(height: 46),
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
            ),
          );
        },
      ),
    );
  }
}

double _heightInches(OnboardingState state) =>
    (state.heightFt * 12 + state.heightIn).toDouble();

double? _weightValue(OnboardingState state) {
  final double? value = double.tryParse(state.weight.trim());
  if (value == null || value <= 0) return null;
  return value;
}

double _weightKg(OnboardingState state) {
  final double? value = _weightValue(state);
  if (value == null) return 0;
  return state.weightUnit == 'kg' ? value : value / 2.2046;
}

double _bmiValue(OnboardingState state) {
  final double kg = _weightKg(state);
  final double metres = _heightInches(state) * 0.0254;
  if (kg <= 0 || metres <= 0) return 0;
  return kg / (metres * metres);
}

double? _waistInches(OnboardingState state) {
  final double? value = double.tryParse(state.waist.trim());
  if (value == null || value <= 0) return null;
  return value;
}

double? _waistToHeight(OnboardingState state) {
  final double? waist = _waistInches(state);
  final double height = _heightInches(state);
  if (waist == null || height <= 0) return null;
  return waist / height;
}

double _heightScale(OnboardingState state) =>
    (_heightInches(state) / 69).clamp(0.75, 1.25).toDouble();

double _bodyWidthScale(OnboardingState state) =>
    (_weightKg(state) / 78.0186).clamp(0.75, 1.35).toDouble();

double _waistScale(OnboardingState state) {
  final double? waist = _waistInches(state);
  if (waist == null) return 1;
  return (waist / 34).clamp(0.6, 1.6).toDouble();
}

class _FigureBmiRow extends StatelessWidget {
  const _FigureBmiRow({required this.state});

  final OnboardingState state;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: <Widget>[
          _FigureTile(
            heightScale: _heightScale(state),
            widthScale: _bodyWidthScale(state),
            waistScale: _waistScale(state),
          ),
          const SizedBox(width: 24),
          Expanded(child: _BmiReadout(state: state)),
        ],
      ),
    );
  }
}

class _FigureTile extends StatefulWidget {
  const _FigureTile({
    required this.heightScale,
    required this.widthScale,
    required this.waistScale,
  });

  final double heightScale;
  final double widthScale;
  final double waistScale;

  @override
  State<_FigureTile> createState() => _FigureTileState();
}

class _FigureTileState extends State<_FigureTile>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final CurvedAnimation _curve;
  late Animation<double> _height;
  late Animation<double> _width;
  late Animation<double> _waist;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
    _curve = CurvedAnimation(parent: _controller, curve: Curves.easeOut);
    _height = Tween<double>(
      begin: widget.heightScale,
      end: widget.heightScale,
    ).animate(_curve);
    _width = Tween<double>(
      begin: widget.widthScale,
      end: widget.widthScale,
    ).animate(_curve);
    _waist = Tween<double>(
      begin: widget.waistScale,
      end: widget.waistScale,
    ).animate(_curve);
    _controller.value = 1;
  }

  @override
  void didUpdateWidget(covariant _FigureTile oldWidget) {
    super.didUpdateWidget(oldWidget);
    bool changed = false;

    if (widget.heightScale != oldWidget.heightScale) {
      _height = Tween<double>(
        begin: _height.value,
        end: widget.heightScale,
      ).animate(_curve);
      changed = true;
    }
    if (widget.widthScale != oldWidget.widthScale) {
      _width = Tween<double>(
        begin: _width.value,
        end: widget.widthScale,
      ).animate(_curve);
      changed = true;
    }
    if (widget.waistScale != oldWidget.waistScale) {
      _waist = Tween<double>(
        begin: _waist.value,
        end: widget.waistScale,
      ).animate(_curve);
      changed = true;
    }

    if (changed) _controller.forward(from: 0);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 112,
      height: 176,
      padding: const EdgeInsets.fromLTRB(2, 6, 2, 0),
      decoration: BoxDecoration(
        color: AppColors.headerText.withValues(alpha: 0.07),
        borderRadius: BorderRadius.circular(16),
      ),
      child: AnimatedBuilder(
        animation: _controller,
        builder: (BuildContext context, Widget? child) {
          return CustomPaint(
            painter: _FigurePainter(
              heightScale: _height.value,
              widthScale: _width.value,
              waistScale: _waist.value,
            ),
            size: Size.infinite,
          );
        },
      ),
    );
  }
}

class _FigurePainter extends CustomPainter {
  const _FigurePainter({
    required this.heightScale,
    required this.widthScale,
    required this.waistScale,
  });

  final double heightScale;
  final double widthScale;
  final double waistScale;

  @override
  void paint(Canvas canvas, Size size) {
    canvas.save();
    canvas.scale(size.width / 160, size.height / 250);

    canvas.drawOval(
      Rect.fromCenter(
        center: const Offset(80, 241),
        width: 92,
        height: 10,
      ),
      Paint()..color = AppColors.headerText.withValues(alpha: 0.14),
    );

    canvas.save();
    canvas.translate(80, 238);
    canvas.scale(1, heightScale);
    canvas.translate(-80, -238);

    canvas.drawCircle(
      const Offset(80, 30),
      15,
      Paint()..color = AppColors.headerText,
    );

    canvas.save();
    canvas.translate(80, 130);
    canvas.scale(widthScale, 1);
    canvas.translate(-80, -130);

    final Paint bodyPaint = Paint()..color = AppColors.headerText;
    final Path torso = Path()
      ..moveTo(52, 56)
      ..quadraticBezierTo(80, 46, 108, 56)
      ..lineTo(104, 132)
      ..quadraticBezierTo(80, 142, 56, 132)
      ..close();
    canvas.drawPath(torso, bodyPaint);

    canvas.drawRRect(
      RRect.fromRectAndRadius(
        const Rect.fromLTWH(38, 58, 11, 64),
        const Radius.circular(5.5),
      ),
      bodyPaint,
    );
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        const Rect.fromLTWH(111, 58, 11, 64),
        const Radius.circular(5.5),
      ),
      bodyPaint,
    );
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        const Rect.fromLTWH(57, 130, 20, 106),
        const Radius.circular(10),
      ),
      bodyPaint,
    );
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        const Rect.fromLTWH(83, 130, 20, 106),
        const Radius.circular(10),
      ),
      bodyPaint,
    );

    final double bandWidth = 52 * waistScale;
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(80 - bandWidth / 2, 94, bandWidth, 9),
        const Radius.circular(4.5),
      ),
      Paint()..color = AppColors.authInputSurface.withValues(alpha: 0.92),
    );

    canvas.restore();
    canvas.restore();
    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant _FigurePainter oldDelegate) =>
      heightScale != oldDelegate.heightScale ||
      widthScale != oldDelegate.widthScale ||
      waistScale != oldDelegate.waistScale;
}

class _BmiReadout extends StatelessWidget {
  const _BmiReadout({required this.state});

  final OnboardingState state;

  @override
  Widget build(BuildContext context) {
    final double bmi = _bmiValue(state);
    final String number = bmi <= 0 ? '--' : bmi.toStringAsFixed(1);
    final String status;
    final Color statusColor;

    if (bmi <= 0) {
      status = 'Add your weight';
      statusColor = AppColors.headerText.withValues(alpha: 0.75);
    } else if (bmi < 18.5) {
      status = 'Below healthy range';
      statusColor = AppColors.headerText;
    } else if (bmi <= 24.9) {
      status = 'Healthy range';
      statusColor = AppColors.onboardingBmiHealthy;
    } else if (bmi <= 29.9) {
      status = 'Above healthy range';
      statusColor = AppColors.onboardingBmiAbove;
    } else {
      status = 'Well above healthy range';
      statusColor = AppColors.terraCotta;
    }

    final double fraction = bmi <= 0
        ? 0
        : ((bmi - 15) / 25).clamp(0.0, 1.0).toDouble();
    final double? ratio = _waistToHeight(state);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(
          'BMI',
          style: OnboardingType.sans(
            13,
            FontWeight.w500,
            AppColors.headerText.withValues(alpha: 0.8),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          number,
          style: OnboardingType.serif(
            36,
            FontWeight.w600,
            AppColors.deepInk,
            height: 38 / 36,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          status,
          style: OnboardingType.sans(12, FontWeight.w500, statusColor),
        ),
        const SizedBox(height: 12),
        _BmiBar(fraction: fraction, showPin: bmi > 0),
        const SizedBox(height: 12),
        Text.rich(
          TextSpan(
            style: OnboardingType.sans(
              12.5,
              FontWeight.w300,
              AppColors.headerText.withValues(alpha: 0.85),
            ),
            children: <InlineSpan>[
              const TextSpan(text: 'Waist to height '),
              TextSpan(
                text: ratio == null ? '--' : ratio.toStringAsFixed(2),
                style: OnboardingType.sans(
                  12.5,
                  FontWeight.w600,
                  AppColors.deepInk,
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

class _BmiBar extends StatefulWidget {
  const _BmiBar({required this.fraction, required this.showPin});

  final double fraction;
  final bool showPin;

  @override
  State<_BmiBar> createState() => _BmiBarState();
}

class _BmiBarState extends State<_BmiBar> with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final CurvedAnimation _curve;
  late Animation<double> _fraction;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
    _curve = CurvedAnimation(parent: _controller, curve: Curves.easeOut);
    _fraction = Tween<double>(
      begin: widget.fraction,
      end: widget.fraction,
    ).animate(_curve);
    _controller.value = 1;
  }

  @override
  void didUpdateWidget(covariant _BmiBar oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.fraction != oldWidget.fraction) {
      _fraction = Tween<double>(
        begin: _fraction.value,
        end: widget.fraction,
      ).animate(_curve);
      _controller.forward(from: 0);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (BuildContext context, BoxConstraints constraints) {
        final double barWidth = constraints.maxWidth;
        return AnimatedBuilder(
          animation: _controller,
          builder: (BuildContext context, Widget? child) {
            return Stack(
              children: <Widget>[
                ClipRRect(
                  borderRadius: BorderRadius.circular(999),
                  child: Row(
                    children: const <Widget>[
                      Expanded(
                        flex: 14,
                        child: _GaugeSegment(
                          color: AppColors.onboardingGaugeLow,
                        ),
                      ),
                      Expanded(
                        flex: 26,
                        child: _GaugeSegment(
                          color: AppColors.onboardingGaugeHealthy,
                        ),
                      ),
                      Expanded(
                        flex: 20,
                        child: _GaugeSegment(
                          color: AppColors.onboardingGaugeMid,
                        ),
                      ),
                      Expanded(
                        flex: 40,
                        child: _GaugeSegment(
                          color: AppColors.onboardingGaugeHigh,
                        ),
                      ),
                    ],
                  ),
                ),
                if (widget.showPin)
                  Positioned(
                    left: _fraction.value * barWidth - 9,
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
                        boxShadow: <BoxShadow>[
                          BoxShadow(
                            color: AppColors.deepInk.withValues(alpha: 0.22),
                            offset: const Offset(0, 2),
                            blurRadius: 3,
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            );
          },
        );
      },
    );
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
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
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
          BoxShadow(
            color: AppColors.headerText.withValues(alpha: 0.06),
            offset: const Offset(0, 2),
            blurRadius: 6,
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
          const SizedBox(height: 12),
          Container(height: 1, color: AppColors.headerText.withValues(alpha: 0.1)),
          Padding(
            padding: const EdgeInsets.only(top: 12),
            child: Column(
              children: <Widget>[
                _HeightSection(
                  feet: state.heightFt,
                  inches: state.heightIn,
                  canDecreaseFeet: state.heightFt > 3,
                  canIncreaseFeet: state.heightFt < 7,
                  canDecreaseInches: state.heightFt > 3 || state.heightIn > 0,
                  canIncreaseInches: state.heightFt < 7 || state.heightIn < 11,
                  onFeetDecrease: () => controller.changeHeightFeet(-1),
                  onFeetIncrease: () => controller.changeHeightFeet(1),
                  onInchesDecrease: () => controller.changeHeightInches(-1),
                  onInchesIncrease: () => controller.changeHeightInches(1),
                ),
                const SizedBox(height: 16),
                _WeightWaistRow(
                  state: state,
                  controller: controller,
                  weightController: weightController,
                  waistController: waistController,
                  onUnitChanged: onUnitChanged,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _HeightSection extends StatelessWidget {
  const _HeightSection({
    required this.feet,
    required this.inches,
    required this.canDecreaseFeet,
    required this.canIncreaseFeet,
    required this.canDecreaseInches,
    required this.canIncreaseInches,
    required this.onFeetDecrease,
    required this.onFeetIncrease,
    required this.onInchesDecrease,
    required this.onInchesIncrease,
  });

  final int feet;
  final int inches;
  final bool canDecreaseFeet;
  final bool canIncreaseFeet;
  final bool canDecreaseInches;
  final bool canIncreaseInches;
  final VoidCallback onFeetDecrease;
  final VoidCallback onFeetIncrease;
  final VoidCallback onInchesDecrease;
  final VoidCallback onInchesIncrease;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(
          'Height',
          style: OnboardingType.sans(14, FontWeight.w500, AppColors.headerText),
        ),
        const SizedBox(height: 12),
        Row(
          children: <Widget>[
            Expanded(
              child: _HeightHalf(
                unit: 'ft',
                value: feet,
                canDecrease: canDecreaseFeet,
                canIncrease: canIncreaseFeet,
                onDecrease: onFeetDecrease,
                onIncrease: onFeetIncrease,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _HeightHalf(
                unit: 'in',
                value: inches,
                canDecrease: canDecreaseInches,
                canIncrease: canIncreaseInches,
                onDecrease: onInchesDecrease,
                onIncrease: onInchesIncrease,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _HeightHalf extends StatelessWidget {
  const _HeightHalf({
    required this.unit,
    required this.value,
    required this.canDecrease,
    required this.canIncrease,
    required this.onDecrease,
    required this.onIncrease,
  });

  final String unit;
  final int value;
  final bool canDecrease;
  final bool canIncrease;
  final VoidCallback onDecrease;
  final VoidCallback onIncrease;

  @override
  Widget build(BuildContext context) {
    return FittedBox(
      fit: BoxFit.scaleDown,
      alignment: Alignment.center,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          _SmallCircleButton(
            plus: false,
            label: 'Less $unit',
            enabled: canDecrease,
            onTap: onDecrease,
          ),
          const SizedBox(width: 6),
          Row(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              SizedBox(
                width: 44,
                child: Text(
                  '$value',
                  textAlign: TextAlign.center,
                  style: OnboardingType.sans(
                    26,
                    FontWeight.w600,
                    AppColors.headerText,
                    height: 1,
                  ),
                ),
              ),
              const SizedBox(width: 4),
              Text(
                unit,
                style: OnboardingType.sans(
                  14,
                  FontWeight.w500,
                  AppColors.headerText.withValues(alpha: 0.6),
                ),
              ),
            ],
          ),
          const SizedBox(width: 6),
          _SmallCircleButton(
            plus: true,
            label: 'More $unit',
            enabled: canIncrease,
            onTap: onIncrease,
          ),
        ],
      ),
    );
  }
}

class _SmallCircleButton extends StatelessWidget {
  const _SmallCircleButton({
    required this.plus,
    required this.label,
    required this.enabled,
    required this.onTap,
  });

  final bool plus;
  final String label;
  final bool enabled;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      enabled: enabled,
      label: label,
      child: AnimatedOpacity(
        duration: const Duration(milliseconds: 150),
        opacity: enabled ? 1 : 0.35,
        child: GestureDetector(
          onTap: enabled ? onTap : null,
          child: Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: Colors.transparent,
              shape: BoxShape.circle,
              border: Border.all(
                color: AppColors.headerText.withValues(alpha: 0.35),
                width: 1,
              ),
            ),
            child: Center(
              child: CustomPaint(
                painter: _PlusMinusPainter(plus: plus),
                size: const Size(16, 16),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _PlusMinusPainter extends CustomPainter {
  const _PlusMinusPainter({required this.plus});

  final bool plus;

  @override
  void paint(Canvas canvas, Size size) {
    final Paint paint = Paint()
      ..color = AppColors.headerText
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.2
      ..strokeCap = StrokeCap.round;

    canvas.drawLine(
      Offset(1, size.height / 2),
      Offset(size.width - 1, size.height / 2),
      paint,
    );
    if (plus) {
      canvas.drawLine(
        Offset(size.width / 2, 1),
        Offset(size.width / 2, size.height - 1),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _PlusMinusPainter oldDelegate) =>
      plus != oldDelegate.plus;
}

class _WeightWaistRow extends StatelessWidget {
  const _WeightWaistRow({
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
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              FittedBox(
                fit: BoxFit.scaleDown,
                alignment: Alignment.centerLeft,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: <Widget>[
                    Text(
                      'Weight',
                      style: OnboardingType.sans(
                        14,
                        FontWeight.w500,
                        AppColors.headerText,
                      ),
                    ),
                    _UnitToggle(
                      value: state.weightUnit,
                      onChanged: onUnitChanged,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 4),
              _UnderlinedField(
                controller: weightController,
                hint: 'Tap to enter',
                label: 'Weight',
                borderAlpha: 1,
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
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: <Widget>[
                  Text(
                    'Waist',
                    style: OnboardingType.sans(
                      14,
                      FontWeight.w500,
                      AppColors.headerText,
                    ),
                  ),
                  Text(
                    'in',
                    style: OnboardingType.sans(
                      12,
                      FontWeight.w500,
                      AppColors.headerText.withValues(alpha: 0.7),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              _UnderlinedField(
                controller: waistController,
                hint: 'e.g. 34',
                label: 'Waist circumference',
                borderAlpha: 0.3,
                onChanged: controller.setWaist,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _UnitToggle extends StatelessWidget {
  const _UnitToggle({required this.value, required this.onChanged});

  final String value;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    final String active = value == 'kg' ? 'kg' : 'lbs';
    return Container(
      padding: const EdgeInsets.all(2),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.headerText.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          for (final String unit in <String>['lbs', 'kg'])
            GestureDetector(
              onTap: () => onChanged(unit == 'lbs' ? 'lb' : 'kg'),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 2),
                decoration: BoxDecoration(
                  color: active == unit
                      ? AppColors.pastelMist
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text(
                  unit,
                  style: OnboardingType.sans(
                    11,
                    FontWeight.w500,
                    active == unit ? AppColors.deepInk : AppColors.headerText,
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
    required this.borderAlpha,
    required this.onChanged,
  });

  final TextEditingController controller;
  final String hint;
  final String label;
  final double borderAlpha;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: label,
      child: Container(
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(
              color: AppColors.headerText.withValues(alpha: borderAlpha),
              width: 2,
            ),
          ),
        ),
        child: TextField(
          controller: controller,
          onChanged: onChanged,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          style: OnboardingType.sans(
            24,
            FontWeight.w500,
            AppColors.headerText,
            height: 32 / 24,
          ),
          decoration: InputDecoration(
            isDense: true,
            border: InputBorder.none,
            enabledBorder: InputBorder.none,
            focusedBorder: InputBorder.none,
            errorBorder: InputBorder.none,
            focusedErrorBorder: InputBorder.none,
            filled: false,
            fillColor: Colors.transparent,
            contentPadding: const EdgeInsets.only(bottom: 4),
            hintText: hint,
            hintStyle: OnboardingType.sans(
              16,
              FontWeight.w400,
              AppColors.headerText.withValues(alpha: 0.4),
            ),
          ),
        ),
      ),
    );
  }
}
