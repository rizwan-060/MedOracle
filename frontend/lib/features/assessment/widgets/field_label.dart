import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Small bold field caption used above inputs inside a section card,
/// e.g. "Medication Name", "Dosage", "Relative".
class FieldLabel extends StatelessWidget {
  const FieldLabel(this.text, {super.key});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: const TextStyle(
        fontSize: 12,
        height: 16 / 12,
        fontWeight: FontWeight.w700,
        color: AppColors.textPrimary,
      ),
    );
  }
}
