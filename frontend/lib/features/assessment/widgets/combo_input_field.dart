import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/app_text_field.dart';

/// Combo-box style input: leading search icon, free text, and trailing dropdown chevron.
/// Delegates directly to the generic [AppTextField] core widget.
class ComboInputField extends StatelessWidget {
  const ComboInputField({
    super.key,
    this.controller,
    this.hintText,
    this.onChanged,
    this.onSubmitted,
  });

  final TextEditingController? controller;
  final String? hintText;
  final ValueChanged<String>? onChanged;
  final ValueChanged<String>? onSubmitted;

  @override
  Widget build(BuildContext context) {
    return AppTextField(
      controller: controller,
      hintText: hintText,
      onChanged: onChanged,
      onSubmitted: onSubmitted,
      showChevron: true,
      prefixIcon: const Icon(Icons.search, size: 16, color: AppColors.textMuted),
      borderColor: AppColors.dustyTaupe,
    );
  }
}
