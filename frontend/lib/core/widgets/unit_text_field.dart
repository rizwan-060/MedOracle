import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

/// Numeric text field with a unit suffix (`170 cm`, `72 kg`, ...).
///
/// Standard clean single-container input adhering strictly to AGENTS.md
/// tokens (radius 12, AppColors.borderSubtle, Lexend typography).
class UnitTextField extends StatefulWidget {
  const UnitTextField({
    super.key,
    required this.unit,
    this.initialValue,
    this.hint,
    this.onChanged,
    this.semanticLabel,
  });

  /// Unit rendered to the right of the value (`cm`, `kg`, ...).
  final String unit;

  /// Pre-filled value.
  final String? initialValue;

  /// Placeholder shown while empty.
  final String? hint;

  final ValueChanged<String>? onChanged;

  /// Field name for semantics / autofill.
  final String? semanticLabel;

  @override
  State<UnitTextField> createState() => _UnitTextFieldState();
}

class _UnitTextFieldState extends State<UnitTextField> {
  late final TextEditingController _controller =
      TextEditingController(text: widget.initialValue);

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: widget.semanticLabel,
      child: TextField(
        controller: _controller,
        cursorColor: AppColors.cta,
        cursorWidth: 2,
        style: AppTextStyles.lexend(
          fontSize: 14,
          fontWeight: FontWeight.w500,
          color: AppColors.textPrimary,
        ),
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        onChanged: widget.onChanged,
        decoration: InputDecoration(
          filled: true,
          fillColor: AppColors.cardSurface,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16.0,
            vertical: 16.0,
          ),
          hintText: widget.hint,
          hintStyle: AppTextStyles.lexend(
            fontSize: 14,
            fontWeight: FontWeight.w400,
            color: AppColors.textSecondary,
          ),
          suffixIcon: Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: Center(
              widthFactor: 1,
              child: Text(
                widget.unit,
                style: AppTextStyles.lexend(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textSecondary,
                ),
              ),
            ),
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
      ),
    );
  }
}
