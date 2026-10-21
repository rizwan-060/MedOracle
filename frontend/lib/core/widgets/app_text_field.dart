import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// Highly configurable, generic input field widget.
///
/// Encapsulates:
/// - An optional [label] rendered above the input box
/// - Custom placeholder / [hintText]
/// - Pre-filled [value] or [controller]
/// - Single-line and multiline ([maxLines] > 1) support
/// - Unit suffix ([suffixText] / [unit], e.g. "cm", "kg", "mg/dL", "%", "days")
/// - Dropdown / modal trigger styling via [showChevron] and [readOnly]
/// - Comprehensive style overrides ([backgroundColor], [borderColor], [textColor], etc.)
class AppTextField extends StatefulWidget {
  const AppTextField({
    super.key,
    this.label,
    this.hintText,
    this.value,
    this.initialValue,
    this.controller,
    this.onChanged,
    this.onSubmitted,
    this.onTap,
    this.readOnly = false,
    this.showChevron = false,
    this.suffixText,
    this.unit,
    this.prefixIcon,
    this.suffixIcon,
    this.keyboardType,
    this.maxLines = 1,
    this.height,
    this.backgroundColor,
    this.borderColor,
    this.focusedBorderColor,
    this.textColor,
    this.hintColor,
    this.labelColor,
    this.errorText,
    this.semanticLabel,
  });

  /// Optional label rendered above the text field.
  final String? label;

  /// Placeholder text displayed when input is empty.
  final String? hintText;

  /// Controlled value. Automatically keeps field synchronized when updated.
  final String? value;

  /// Initial static text value.
  final String? initialValue;

  /// Explicit external TextEditingController, if provided.
  final TextEditingController? controller;

  /// Callback when text changes.
  final ValueChanged<String>? onChanged;

  /// Callback when submitted via keyboard enter action.
  final ValueChanged<String>? onSubmitted;

  /// Tap callback (for picker sheets or dropdown modal triggers).
  final VoidCallback? onTap;

  /// Whether user can type directly into the field.
  final bool readOnly;

  /// Whether to display a trailing dropdown chevron.
  final bool showChevron;

  /// Inline unit or suffix text (e.g., "mg/dL", "cm", "days").
  final String? suffixText;

  /// Alias for suffixText.
  final String? unit;

  /// Optional widget rendered before the text input.
  final Widget? prefixIcon;

  /// Optional widget rendered after the text input (or before the chevron).
  final Widget? suffixIcon;

  /// Virtual keyboard type (number, text, decimal, etc.).
  final TextInputType? keyboardType;

  /// Number of lines. Set > 1 for multiline text areas.
  final int maxLines;

  /// Explicit height override (defaults to 44px for single-line inputs).
  final double? height;

  /// Custom background fill color (defaults to [AppColors.cardSurface]).
  final Color? backgroundColor;

  /// Unfocused container outline color (defaults to [AppColors.borderSubtle]).
  final Color? borderColor;

  /// Focused container outline color (defaults to [AppColors.primaryMaroon]).
  final Color? focusedBorderColor;

  /// Text color (defaults to [AppColors.textPrimary]).
  final Color? textColor;

  /// Hint placeholder color (defaults to [AppColors.textMuted]).
  final Color? hintColor;

  /// Label text color (defaults to [AppColors.textPrimary]).
  final Color? labelColor;

  /// Validation error text displayed below the field.
  final String? errorText;

  /// Accessibility label.
  final String? semanticLabel;

  @override
  State<AppTextField> createState() => _AppTextFieldState();
}

class _AppTextFieldState extends State<AppTextField> {
  late final FocusNode _focusNode = FocusNode()..addListener(() => setState(() {}));
  late final TextEditingController _internalController =
      TextEditingController(text: widget.value ?? widget.initialValue);

  TextEditingController get _effectiveController =>
      widget.controller ?? _internalController;

  @override
  void didUpdateWidget(covariant AppTextField oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.controller == null &&
        widget.value != null &&
        widget.value != _internalController.text) {
      _internalController.text = widget.value!;
    }
  }

  @override
  void dispose() {
    _focusNode.dispose();
    if (widget.controller == null) {
      _internalController.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final bool isFocused = _focusNode.hasFocus && !widget.readOnly;
    final String? effectiveSuffix = widget.suffixText ?? widget.unit;
    final double defaultHeight = widget.maxLines > 1 ? (widget.maxLines * 24.0 + 20.0) : 44.0;
    final double effectiveHeight = widget.height ?? defaultHeight;

    final Color effectiveBg = widget.backgroundColor ?? AppColors.cardSurface;
    final Color effectiveBorder = isFocused
        ? (widget.focusedBorderColor ?? AppColors.primaryMaroon)
        : (widget.borderColor ?? AppColors.borderSubtle);
    final Color effectiveText = widget.textColor ?? AppColors.textPrimary;
    final Color effectiveHint = widget.hintColor ?? AppColors.textMuted;
    final Color effectiveLabel = widget.labelColor ?? AppColors.textPrimary;

    Widget fieldWidget = AnimatedContainer(
      duration: const Duration(milliseconds: 150),
      height: widget.maxLines > 1 ? null : effectiveHeight,
      constraints: widget.maxLines > 1
          ? BoxConstraints(minHeight: effectiveHeight)
          : null,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: effectiveBg,
        border: Border.all(
          color: widget.errorText != null ? AppColors.amberWarning : effectiveBorder,
          width: 1.5,
        ),
        borderRadius: BorderRadius.circular(12),
        boxShadow: isFocused
            ? const <BoxShadow>[
                BoxShadow(
                  color: AppColors.focusRing,
                  blurRadius: 0,
                  spreadRadius: 3,
                ),
              ]
            : const <BoxShadow>[],
      ),
      child: Material(
        color: Colors.transparent,
        child: Row(
          crossAxisAlignment: widget.maxLines > 1
              ? CrossAxisAlignment.start
              : CrossAxisAlignment.center,
          children: <Widget>[
            if (widget.prefixIcon != null) ...[
              widget.prefixIcon!,
              const SizedBox(width: 8),
            ],
            Expanded(
              child: TextField(
                focusNode: _focusNode,
                controller: _effectiveController,
                readOnly: widget.readOnly,
                onTap: widget.onTap,
                keyboardType: widget.keyboardType,
                maxLines: widget.maxLines,
                style: TextStyle(
                  fontSize: 14,
                  height: 20 / 14,
                  fontWeight: FontWeight.w600,
                  color: effectiveText,
                ),
                decoration: InputDecoration.collapsed(
                  hintText: widget.hintText,
                  hintStyle: TextStyle(
                    fontSize: 14,
                    height: 20 / 14,
                    fontWeight: FontWeight.w400,
                    color: effectiveHint,
                  ),
                ),
                onChanged: widget.onChanged,
                onSubmitted: widget.onSubmitted,
              ),
            ),
            if (effectiveSuffix != null && effectiveSuffix.isNotEmpty) ...[
              const SizedBox(width: 6),
              Text(
                effectiveSuffix,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                  color: AppColors.textMuted,
                ),
              ),
            ],
            if (widget.suffixIcon != null) ...[
              const SizedBox(width: 6),
              widget.suffixIcon!,
            ],
            if (widget.showChevron) ...[
              const SizedBox(width: 6),
              const Icon(
                Icons.keyboard_arrow_down_rounded,
                size: 20,
                color: AppColors.textMuted,
              ),
            ],
          ],
        ),
      ),
    );

    if (widget.onTap != null && widget.readOnly) {
      fieldWidget = GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: widget.onTap,
        child: fieldWidget,
      );
    }

    if (widget.label != null && widget.label!.isNotEmpty) {
      fieldWidget = Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Text(
            widget.label!,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: effectiveLabel,
            ),
          ),
          const SizedBox(height: 5),
          fieldWidget,
          if (widget.errorText != null) ...[
            const SizedBox(height: 4),
            Text(
              widget.errorText!,
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w500,
                color: AppColors.amberWarning,
              ),
            ),
          ],
        ],
      );
    }

    return Semantics(
      label: widget.semanticLabel ?? widget.label,
      child: fieldWidget,
    );
  }
}
