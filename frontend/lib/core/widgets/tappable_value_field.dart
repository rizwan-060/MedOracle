import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';
import 'ref_chevron.dart';

/// Suffix decoration of a [TappableValueField].
enum ValueFieldSuffix {
  /// Down chevron - field opens a selection list.
  chevron,

  /// Plum caret bar - shown while the field has focus (date entry).
  caret,

  /// No suffix.
  none,
}

/// Read-only value field (`Date of Birth`, `Blood Group`, `Activity Level`).
///
/// Tapping it invokes [onTap]; the whole box mirrors the reference's border,
/// radius and focus ring. Single clean un-nested container.
class TappableValueField extends StatefulWidget {
  const TappableValueField({
    super.key,
    required this.value,
    required this.onTap,
    this.hint,
    this.suffix = ValueFieldSuffix.chevron,
    this.semanticLabel,
  });

  /// Text shown inside the field.
  final String value;

  /// Placeholder while [value] is empty.
  final String? hint;

  final VoidCallback onTap;

  final ValueFieldSuffix suffix;

  /// Field name for semantics.
  final String? semanticLabel;

  @override
  State<TappableValueField> createState() => _TappableValueFieldState();
}

class _TappableValueFieldState extends State<TappableValueField> {
  final FocusNode _focusNode = FocusNode();

  @override
  void dispose() {
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final bool hasValue = widget.value.isNotEmpty;

    return Semantics(
      button: true,
      label: widget.semanticLabel,
      child: AnimatedBuilder(
        animation: _focusNode,
        builder: (BuildContext context, Widget? child) {
          final bool focused = _focusNode.hasFocus;
          return AnimatedContainer(
            duration: const Duration(milliseconds: 120),
            height: 52,
            padding: const EdgeInsets.symmetric(horizontal: 14),
            decoration: BoxDecoration(
              color: AppColors.cardSurface,
              border: Border.all(
                color: focused ? AppColors.cta : AppColors.border,
                width: 1.5,
              ),
              borderRadius: BorderRadius.circular(12),
              boxShadow: focused
                  ? [
                      BoxShadow(
                        color: AppColors.cta.withValues(alpha: 0.20),
                        blurRadius: 4,
                        spreadRadius: 2,
                      ),
                    ]
                  : const <BoxShadow>[],
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: () {
                  _focusNode.requestFocus();
                  widget.onTap();
                },
                borderRadius: BorderRadius.circular(12),
                child: Row(
                  children: <Widget>[
                    Expanded(
                      child: Text(
                        hasValue ? widget.value : (widget.hint ?? ''),
                        style: hasValue
                            ? AppTextStyles.lexend(
                                fontSize: 14,
                                fontWeight: FontWeight.w500,
                                color: AppColors.textPrimary,
                              )
                            : AppTextStyles.lexend(
                                fontSize: 14,
                                fontWeight: FontWeight.w400,
                                color: AppColors.textSecondary,
                              ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    switch (widget.suffix) {
                      ValueFieldSuffix.chevron => const RefChevron(
                          size: 16,
                          strokeWidth: 1.9,
                          color: AppColors.textSecondary,
                        ),
                      ValueFieldSuffix.caret =>
                        focused ? const _CaretBar() : const SizedBox(width: 2),
                      ValueFieldSuffix.none => const SizedBox.shrink(),
                    },
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

class _CaretBar extends StatefulWidget {
  const _CaretBar();

  @override
  State<_CaretBar> createState() => _CaretBarState();
}

class _CaretBarState extends State<_CaretBar>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 800),
  );

  @override
  void initState() {
    super.initState();
    _controller.repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: Tween<double>(begin: 0.15, end: 1).animate(_controller),
      child: const SizedBox(
        width: 2,
        height: 18,
        child: ColoredBox(color: AppColors.cta),
      ),
    );
  }
}
