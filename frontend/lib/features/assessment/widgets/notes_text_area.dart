import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/app_text_field.dart';

/// Multi-line notes input matching the design's bordered textarea with muted placeholder.
/// Delegates directly to the generic [AppTextField] core widget.
class NotesTextArea extends StatelessWidget {
  const NotesTextArea({
    super.key,
    this.controller,
    this.hintText,
    this.onChanged,
    this.height = 80,
  });

  final TextEditingController? controller;
  final String? hintText;
  final ValueChanged<String>? onChanged;
  final double height;

  @override
  Widget build(BuildContext context) {
    return AppTextField(
      controller: controller,
      hintText: hintText,
      onChanged: onChanged,
      maxLines: 3,
      height: height,
      borderColor: AppColors.dustyTaupe,
    );
  }
}
