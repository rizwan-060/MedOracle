import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// Standard clean single-container combo-box input adhering to AGENTS.md
/// specifications (radius 12, AppColors.borderSubtle, Lexend typography).
///
/// Leading search glyph, free text with a live caret, and trailing dropdown chevron.
/// Used by the "Chronic Conditions" typeahead on the Clinical Status step.
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
    return TextField(
      controller: controller,
      onChanged: onChanged,
      onSubmitted: onSubmitted,
      cursorColor: AppColors.cta,
      cursorWidth: 2,
      style: AppTextStyles.lexend(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: AppColors.textPrimary,
      ),
      decoration: InputDecoration(
        filled: true,
        fillColor: AppColors.cardSurface,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16.0,
          vertical: 16.0,
        ),
        hintText: hintText,
        hintStyle: AppTextStyles.lexend(
          fontSize: 14,
          fontWeight: FontWeight.w400,
          color: AppColors.textSecondary,
        ),
        prefixIcon: const Icon(
          Icons.search,
          size: 20,
          color: AppColors.textSecondary,
        ),
        suffixIcon: const Icon(
          Icons.keyboard_arrow_down,
          size: 20,
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
