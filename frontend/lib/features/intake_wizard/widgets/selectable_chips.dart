import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Wrap of removable pill chips (e.g. selected conditions, surgeries,
/// allergies). Each chip shows its label followed by an "x" remove glyph.
///
/// When [onRemoved] is null the chips render in read-only display mode
/// (no remove glyph, no tap) — used on the Review step.
class SelectableChips extends StatelessWidget {
  const SelectableChips({
    super.key,
    required this.items,
    this.onRemoved,
  });

  final List<String> items;

  final ValueChanged<String>? onRemoved;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: items.map((String item) => _Chip(label: item, onRemoved: onRemoved)).toList(),
    );
  }
}

class _Chip extends StatelessWidget {
  const _Chip({required this.label, required this.onRemoved});

  final String label;
  final ValueChanged<String>? onRemoved;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onRemoved == null ? null : () => onRemoved!(label),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: AppColors.canvasBackground,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: AppColors.dustyTaupe),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              label,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
            ),
            if (onRemoved != null) ...[
              const SizedBox(width: 4),
              const Text(
                '×',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textMuted,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
