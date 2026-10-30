import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

/// Horizontal pill-row selector used for categorical answers
/// (`Gender`, `Smoking Status`, ...).
class ChoiceSegment extends StatelessWidget {
  const ChoiceSegment({
    super.key,
    required this.options,
    required this.value,
    required this.onChanged,
    this.semanticLabel,
  });

  /// Ordered list of mutually exclusive options.
  final List<String> options;

  /// Currently selected option.
  final String value;

  final ValueChanged<String> onChanged;

  /// Optional group label for semantics.
  final String? semanticLabel;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      container: true,
      label: semanticLabel,
      child: Row(
        children: <Widget>[
          for (int i = 0; i < options.length; i++) ...<Widget>[
            if (i > 0) const SizedBox(width: 8),
            Expanded(child: _SegmentOption(
              label: options[i],
              selected: options[i] == value,
              onTap: () => onChanged(options[i]),
            )),
          ],
        ],
      ),
    );
  }
}

class _SegmentOption extends StatelessWidget {
  const _SegmentOption({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      selected: selected,
      label: label,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Ink(
            height: 52.0,
            decoration: BoxDecoration(
              gradient: selected ? AppColors.segmentSelectedGradient : null,
              color: selected ? null : AppColors.segmentIdleFill,
              border: Border.all(
                color: selected ? AppColors.refPlum : AppColors.refFieldBorder,
                width: 1.5,
              ),
              borderRadius: BorderRadius.circular(12),
              boxShadow: <BoxShadow>[
                if (selected)
                  const BoxShadow(
                    color: AppColors.segmentShadowSelected,
                    offset: Offset(0, 6),
                    blurRadius: 14,
                    spreadRadius: -6,
                  )
                else
                  const BoxShadow(
                    color: AppColors.segmentShadowIdle,
                    offset: Offset(0, 3),
                    blurRadius: 10,
                    spreadRadius: -4,
                  ),
              ],
            ),
            child: Center(
              child: Text(
                label,
                style: selected
                    ? AppTextStyles.segmentOptionSelected
                    : AppTextStyles.segmentOption,
                maxLines: 1,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
