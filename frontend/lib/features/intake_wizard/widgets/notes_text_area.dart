import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// Standard clean single-container multi-line input adhering to AGENTS.md
/// specifications (radius 12, AppColors.borderSubtle, Lexend typography).
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

  /// Retained for backwards-compatibility; text area defaults to comfortable 3-5 line sizing.
  final double height;

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      onChanged: onChanged,
      minLines: 3,
      maxLines: 5,
      cursorColor: AppColors.cta,
      cursorWidth: 2,
      style: AppTextStyles.lexend(
        fontSize: 14,
        height: 20 / 14,
        fontWeight: FontWeight.w500,
        color: AppColors.textPrimary,
      ),
      decoration: InputDecoration(
        filled: true,
        fillColor: AppColors.cardSurface,
        contentPadding: const EdgeInsets.all(16.0),
        hintText: hintText,
        hintStyle: AppTextStyles.lexend(
          fontSize: 14,
          height: 20 / 14,
          fontWeight: FontWeight.w400,
          color: AppColors.textSecondary,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12.0),
          borderSide: const BorderSide(
            color: AppColors.borderSubtle,
            width: 1.5,
          ),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12.0),
          borderSide: const BorderSide(
            color: AppColors.borderSubtle,
            width: 1.5,
          ),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12.0),
          borderSide: const BorderSide(
            color: AppColors.cta,
            width: 1.5,
          ),
        ),
      ),
    );
  }
}
