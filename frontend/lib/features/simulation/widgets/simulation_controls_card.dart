import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../models/simulation_models.dart';
import 'lifestyle_slider.dart';
import 'lifestyle_switch.dart';

/// White card holding the four what-if controls.
///
/// Two sliders (weight, blood pressure) and two switches (smoking, walking)
/// are separated by hairline dividers
/// (design: v8 Step 6C "What-if controls" card).
class SimulationControlsCard extends StatelessWidget {
  const SimulationControlsCard({
    super.key,
    required this.weightKg,
    required this.bloodPressureMmHg,
    required this.quitSmoking,
    required this.walkThirtyMinutesDaily,
    required this.onWeightChanged,
    required this.onBloodPressureChanged,
    required this.onQuitSmokingToggled,
    required this.onWalkToggled,
  });

  /// Current weight reduction, in kilograms.
  final int weightKg;

  /// Current blood pressure reduction, in mmHg.
  final int bloodPressureMmHg;

  /// Whether the user has quit smoking.
  final bool quitSmoking;

  /// Whether the user walks 30 minutes every day.
  final bool walkThirtyMinutesDaily;

  /// Called with the new weight reduction.
  final ValueChanged<int> onWeightChanged;

  /// Called with the new blood pressure reduction.
  final ValueChanged<int> onBloodPressureChanged;

  /// Called when the "quit smoking" switch is flipped.
  final ValueChanged<bool> onQuitSmokingToggled;

  /// Called when the "walk 30 mins daily" switch is flipped.
  final ValueChanged<bool> onWalkToggled;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 16),
      padding: const EdgeInsets.fromLTRB(20, 4, 20, 4),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(
          color: AppColors.dustyTaupe.withValues(alpha: 0.45),
        ),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.primaryMaroon.withValues(alpha: 0.30),
            offset: const Offset(0, 14),
            blurRadius: 30,
            spreadRadius: -12,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          _SliderRow(
            title: 'Weight reduction',
            valueLabel: _weightLabel(weightKg),
            hint: 'Up to 4 points lower',
            value: weightKg,
            max: LifestyleInputs.maxWeightKg,
            minScaleLabel: '0 kg',
            maxScaleLabel:
                '${LifestyleInputs.minusSign}${LifestyleInputs.maxWeightKg} kg',
            onChanged: onWeightChanged,
          ),
          const _RowDivider(),
          _SliderRow(
            title: 'Blood pressure',
            valueLabel: _bloodPressureLabel(bloodPressureMmHg),
            hint: 'Up to 5 points lower',
            value: bloodPressureMmHg,
            max: LifestyleInputs.maxBloodPressureMmHg,
            minScaleLabel: '0 mmHg',
            maxScaleLabel:
                '${LifestyleInputs.minusSign}'
                '${LifestyleInputs.maxBloodPressureMmHg} mmHg',
            onChanged: onBloodPressureChanged,
          ),
          const _RowDivider(),
          _SwitchRow(
            title: 'Quit smoking',
            hint: 'About 7 points lower',
            value: quitSmoking,
            onChanged: onQuitSmokingToggled,
          ),
          const _RowDivider(),
          _SwitchRow(
            title: 'Walk 30 mins daily',
            hint: 'About 3 points lower',
            value: walkThirtyMinutesDaily,
            onChanged: onWalkToggled,
          ),
        ],
      ),
    );
  }

  static String _weightLabel(int weightKg) {
    return weightKg == 0
        ? '0 kg'
        : '${LifestyleInputs.minusSign}$weightKg kg';
  }

  static String _bloodPressureLabel(int bloodPressureMmHg) {
    return bloodPressureMmHg == 0
        ? '0 mmHg'
        : '${LifestyleInputs.minusSign}$bloodPressureMmHg mmHg';
  }
}

/// Hairline divider between two control rows.
class _RowDivider extends StatelessWidget {
  const _RowDivider();

  @override
  Widget build(BuildContext context) {
    return const SizedBox(
      height: 1,
      child: ColoredBox(color: AppColors.refControlDivider),
    );
  }
}

/// A titled slider row with a hint and the scale below the track.
class _SliderRow extends StatelessWidget {
  const _SliderRow({
    required this.title,
    required this.valueLabel,
    required this.hint,
    required this.value,
    required this.max,
    required this.minScaleLabel,
    required this.maxScaleLabel,
    required this.onChanged,
  });

  final String title;
  final String valueLabel;
  final String hint;
  final int value;
  final int max;
  final String minScaleLabel;
  final String maxScaleLabel;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Row(
            children: <Widget>[
              Expanded(
                child: Text(
                  title,
                  style: AppTextStyles.simulationControlTitle,
                ),
              ),
              const SizedBox(width: 12),
              Text(valueLabel, style: AppTextStyles.simulationControlValue),
            ],
          ),
          const SizedBox(height: 2),
          Text(hint, style: AppTextStyles.simulationControlHint),
          const SizedBox(height: 10),
          LifestyleSlider(
            value: value,
            max: max,
            onChanged: onChanged,
            semanticLabel: title,
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: <Widget>[
              Text(minScaleLabel, style: AppTextStyles.simulationScaleLabel),
              Text(maxScaleLabel, style: AppTextStyles.simulationScaleLabel),
            ],
          ),
        ],
      ),
    );
  }
}

/// A titled switch row with a hint underneath the title.
class _SwitchRow extends StatelessWidget {
  const _SwitchRow({
    required this.title,
    required this.hint,
    required this.value,
    required this.onChanged,
  });

  final String title;
  final String hint;
  final bool value;
  final ValueChanged<bool> onChanged;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 18),
      child: Row(
        children: <Widget>[
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: <Widget>[
                Text(title, style: AppTextStyles.simulationControlTitle),
                const SizedBox(height: 2),
                Text(hint, style: AppTextStyles.simulationControlHint),
              ],
            ),
          ),
          const SizedBox(width: 16),
          LifestyleSwitch(
            value: value,
            onChanged: onChanged,
            semanticLabel: title,
          ),
        ],
      ),
    );
  }
}
