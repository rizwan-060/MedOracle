import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

/// Numeric text field with a unit suffix (`170 cm`, `72 kg`, ...).
///
/// Reproduces the reference's 44px box, 1.5px border, 12px radius and the
/// 4px plum focus ring.
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
  late final FocusNode _focusNode = FocusNode();
  late final TextEditingController _controller =
      TextEditingController(text: widget.initialValue);

  @override
  void dispose() {
    _focusNode.dispose();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: widget.semanticLabel,
      child: AnimatedBuilder(
        animation: _focusNode,
        builder: (BuildContext context, Widget? child) {
          final bool focused = _focusNode.hasFocus;
          return AnimatedContainer(
            duration: const Duration(milliseconds: 120),
            height: 44,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            decoration: BoxDecoration(
              color: AppColors.cardSurface,
              border: Border.all(
                color:
                    focused ? AppColors.refPlum : AppColors.refFieldBorder,
                width: 1.5,
              ),
              borderRadius: BorderRadius.circular(12),
              boxShadow: focused
                  ? const <BoxShadow>[
                      BoxShadow(
                        color: AppColors.focusRing,
                        blurRadius: 0,
                        spreadRadius: 4,
                      ),
                    ]
                  : const <BoxShadow>[],
            ),
            // `TextField` needs a Material ancestor for its editing overlay.
            child: Material(
              color: Colors.transparent,
              child: child!,
            ),
          );
        },
        child: Row(
          children: <Widget>[
            Expanded(
              child: Center(
                child: TextField(
                  focusNode: _focusNode,
                  controller: _controller,
                  style: AppTextStyles.fieldValue,
                  textAlign: TextAlign.left,
                  keyboardType:
                      const TextInputType.numberWithOptions(decimal: true),
                  decoration: InputDecoration.collapsed(
                    hintText: widget.hint,
                    hintStyle: AppTextStyles.fieldHint,
                  ),
                  onChanged: widget.onChanged,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Text(widget.unit, style: AppTextStyles.fieldUnit),
          ],
        ),
      ),
    );
  }
}
