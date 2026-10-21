import 'package:flutter/material.dart';

import '../../../core/widgets/app_text_field.dart';

/// Standard 44px bordered text input used inside assessment section cards.
/// Delegates directly to the generic [AppTextField] core widget.
class AssessmentTextField extends StatelessWidget {
  const AssessmentTextField({
    super.key,
    this.controller,
    this.value,
    this.hintText,
    this.initialValue,
    this.onChanged,
    this.onSubmitted,
    this.onTap,
    this.showChevron = false,
    this.readOnly = false,
    this.keyboardType,
    this.suffixText,
    this.unit,
    this.maxLines = 1,
    this.height,
  });

  final TextEditingController? controller;
  final String? value;
  final String? hintText;
  final String? initialValue;
  final ValueChanged<String>? onChanged;
  final ValueChanged<String>? onSubmitted;
  final VoidCallback? onTap;
  final bool showChevron;
  final bool readOnly;
  final TextInputType? keyboardType;
  final String? suffixText;
  final String? unit;
  final int maxLines;
  final double? height;

  @override
  Widget build(BuildContext context) {
    return AppTextField(
      controller: controller,
      value: value,
      hintText: hintText,
      initialValue: initialValue,
      onChanged: onChanged,
      onSubmitted: onSubmitted,
      onTap: onTap,
      showChevron: showChevron,
      readOnly: readOnly,
      keyboardType: keyboardType,
      suffixText: suffixText ?? unit,
      maxLines: maxLines,
      height: height,
    );
  }
}

/// Backward compatibility typedef alias.
typedef IntakeTextField = AssessmentTextField;
