import 'package:flutter/material.dart';

import 'app_text_field.dart';

/// Numeric text field with a unit suffix (`170 cm`, `72 kg`, ...).
/// Delegates directly to the generic [AppTextField] core widget.
class UnitTextField extends StatelessWidget {
  const UnitTextField({
    super.key,
    required this.unit,
    this.initialValue,
    this.hint,
    this.onChanged,
    this.semanticLabel,
  });

  final String unit;
  final String? initialValue;
  final String? hint;
  final ValueChanged<String>? onChanged;
  final String? semanticLabel;

  @override
  Widget build(BuildContext context) {
    return AppTextField(
      unit: unit,
      initialValue: initialValue,
      hintText: hint,
      onChanged: onChanged,
      semanticLabel: semanticLabel,
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
    );
  }
}
