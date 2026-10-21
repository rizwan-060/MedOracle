import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Combo-box style input: leading search glyph, free text with a live
/// caret while focused, and a trailing dropdown chevron. Used by the
/// "Chronic Conditions" typeahead on the Clinical Status step.
class ComboInputField extends StatefulWidget {
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
  State<ComboInputField> createState() => _ComboInputFieldState();
}

class _ComboInputFieldState extends State<ComboInputField> {
  late final FocusNode _focusNode = FocusNode()..addListener(() => setState(() {}));

  @override
  void dispose() {
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final bool focused = _focusNode.hasFocus;

    return Container(
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
          const Icon(Icons.search, size: 16, color: AppColors.textMuted),
          const SizedBox(width: 8),
          Expanded(
            child: TextField(
              focusNode: _focusNode,
              controller: widget.controller,
              onChanged: widget.onChanged,
              onSubmitted: widget.onSubmitted,
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
          const Icon(
            Icons.keyboard_arrow_down,
            size: 20,
            color: AppColors.textMuted,
          ),
        ],
      ),
    );
  }
}
