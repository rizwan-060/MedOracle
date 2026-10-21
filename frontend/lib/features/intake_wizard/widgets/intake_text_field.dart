import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Standard 44px bordered text input used inside intake section cards.
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
  late final FocusNode _focusNode = FocusNode()..addListener(() => setState(() {}));
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
    _focusNode.dispose();
    _internalController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final bool focused = !widget.readOnly && _focusNode.hasFocus;

    return GestureDetector(
      onTap: widget.onTap,
      child: Container(
        height: 44,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        decoration: BoxDecoration(
          color: AppColors.cardSurface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: focused ? AppColors.primaryMaroon : AppColors.dustyTaupe,
            width: 1.5,
          ),
          boxShadow: focused
              ? [
                  BoxShadow(
                    color: AppColors.primaryMaroon.withValues(alpha: 0.28),
                    blurRadius: 4,
                    spreadRadius: 4,
                  ),
                ]
              : null,
        ),
        child: Row(
          children: [
            Expanded(
              child: TextField(
                focusNode: _focusNode,
                controller: widget.controller ??
                    (widget.value != null || widget.initialValue != null
                        ? _internalController
                        : null),
                onChanged: widget.onChanged,
                readOnly: widget.readOnly,
                showCursor: !widget.readOnly,
                keyboardType: widget.keyboardType,
                cursorColor: AppColors.primaryMaroon,
                cursorWidth: 2,
                cursorHeight: 18,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w500,
                  color: AppColors.textPrimary,
                ),
                decoration: InputDecoration(
                  isDense: true,
                  border: InputBorder.none,
                  contentPadding: EdgeInsets.zero,
                  hintText: widget.hintText,
                  hintStyle: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w400,
                    color: AppColors.textMuted,
                  ),
                ),
              ),
            ),
            if (widget.suffixText != null) ...[
              const SizedBox(width: 8),
              Text(
                widget.suffixText!,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textMuted,
                ),
              ),
            ],
            if (widget.showChevron)
              const Icon(
                Icons.keyboard_arrow_down,
                size: 20,
                color: AppColors.textMuted,
              ),
          ],
        ),
      ),
    );
  }
}
