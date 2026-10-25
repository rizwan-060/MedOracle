import 'package:flutter/material.dart';

import '../../../core/widgets/field_group.dart';
import '../../../core/widgets/unit_text_field.dart';
import '../../../data/models/patient_profile_model.dart';

/// "Body Measurements" section of Step 1.
///
/// Height and weight sit side by side (`.two` in the reference), waist
/// circumference spans the full width below them.
class BodyMeasurementsSection extends StatelessWidget {
  const BodyMeasurementsSection({
    super.key,
    required this.profile,
    required this.onChanged,
  });

  final PatientProfile profile;

  /// Called whenever one of the measurements changes.
  final ValueChanged<PatientProfile> onChanged;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Expanded(
              child: FieldGroup(
                label: 'Height',
                isFirst: true,
                control: UnitTextField(
                  unit: 'cm',
                  initialValue: _format(profile.heightCm),
                  semanticLabel: 'Height',
                  onChanged: (String raw) => onChanged(
                    profile.copyWith(heightCm: _parse(raw, profile.heightCm)),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: FieldGroup(
                label: 'Weight',
                isFirst: true,
                control: UnitTextField(
                  unit: 'kg',
                  initialValue: _format(profile.weightKg),
                  semanticLabel: 'Weight',
                  onChanged: (String raw) => onChanged(
                    profile.copyWith(weightKg: _parse(raw, profile.weightKg)),
                  ),
                ),
              ),
            ),
          ],
        ),
        FieldGroup(
          label: 'Waist Circumference',
          control: UnitTextField(
            unit: 'cm',
            initialValue: _format(profile.waistCircumferenceCm),
            semanticLabel: 'Waist Circumference',
            onChanged: (String raw) => onChanged(
              profile.copyWith(
                waistCircumferenceCm:
                    _parse(raw, profile.waistCircumferenceCm),
              ),
            ),
          ),
        ),
      ],
    );
  }

  /// Renders a measurement without a trailing `.0` (170 rather than 170.0).
  static String _format(double value) {
    if (value == value.roundToDouble()) {
      return value.round().toString();
    }
    return value.toString();
  }

  /// Parses user input, keeping the previous value while the field is empty.
  static double _parse(String raw, double fallback) {
    final double? parsed = double.tryParse(raw.trim());
    if (parsed == null || parsed <= 0) {
      return fallback;
    }
    return parsed;
  }
}
