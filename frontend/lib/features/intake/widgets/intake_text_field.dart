import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// Standard clean un-nested text input adhering strictly to AGENTS.md
/// specifications (radius 12, AppColors.borderSubtle, Lexend typography).
///
/// With [showChevron] it doubles as a tappable dropdown field: tapping it
/// invokes [onTap] (e.g. to open an option picker sheet).
class IntakeTextField extends StatefulWidget {
  const IntakeTextField({
    super.key,
    this.controller,
    this.value,
    this.hintText,
    this.initialValue,
    this.onChanged,
    this.onTap,
    this.showChevron = false,
    this.readOnly = false,
    this.keyboardType,
    this.suffixText,
  });

  final TextEditingController? controller;

  /// Controlled text value. When provided (and [controller] is null) the
  /// field manages its own controller and stays in sync with this value —
  /// use for dropdown-style fields whose text is set from picked options.
  final String? value;

  final String? hintText;
  final String? initialValue;
  final ValueChanged<String>? onChanged;
  final VoidCallback? onTap;
  final bool showChevron;

  /// When true the field never shows the focus ring (dropdown-style fields
  /// react to taps instead of focus).
  final bool readOnly;

  final TextInputType? keyboardType;

  /// Small muted unit label shown inside the field on the right side,
  /// e.g. "days" for a duration input.
  final String? suffixText;

  @override
  State<IntakeTextField> createState() => _IntakeTextFieldState();
}

class _IntakeTextFieldState extends State<IntakeTextField> {
  late final TextEditingController _internalController =
      TextEditingController(text: widget.value ?? widget.initialValue);

  @override
  void didUpdateWidget(covariant IntakeTextField oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.controller == null &&
        widget.value != null &&
        widget.value != oldWidget.value &&
        widget.value != _internalController.text) {
      _internalController.text = widget.value!;
    }
  }

  @override
  void dispose() {
    _internalController.dispose();
    super.dispose();
  }

  Widget? _buildSuffix() {
    if (widget.suffixText == null && !widget.showChevron) {
      return null;
    }
    return Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.end,
      children: [
        if (widget.suffixText != null)
          Padding(
            padding: const EdgeInsets.only(right: 12.0),
            child: Text(
              widget.suffixText!,
              style: AppTextStyles.lexend(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: AppColors.textSecondary,
              ),
            ),
          ),
        if (widget.showChevron)
          const Padding(
            padding: EdgeInsets.only(right: 12.0),
            child: Icon(
              Icons.keyboard_arrow_down,
              size: 20,
              color: AppColors.textSecondary,
            ),
          ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final effectiveController = widget.controller ??
        (widget.value != null || widget.initialValue != null
            ? _internalController
            : null);

    return GestureDetector(
      onTap: widget.onTap,
      behavior: HitTestBehavior.opaque,
      child: IgnorePointer(
        ignoring: widget.onTap != null && widget.readOnly,
        child: TextField(
          controller: effectiveController,
          onChanged: widget.onChanged,
          onTap: widget.onTap,
          readOnly: widget.readOnly,
          showCursor: !widget.readOnly,
          keyboardType: widget.keyboardType,
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
            hintText: widget.hintText,
            hintStyle: AppTextStyles.lexend(
              fontSize: 14,
              fontWeight: FontWeight.w400,
              color: AppColors.textSecondary,
            ),
            suffixIcon: _buildSuffix(),
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
      ),
    );
  }
}
