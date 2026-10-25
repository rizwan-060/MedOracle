import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Key/value summary row from the design's `.kv`: muted label on the left,
/// bold value (with optional muted unit) on the right, hairline divider on
/// top. Used on the Review & Confirm step.
class KeyValueRow extends StatelessWidget {
  const KeyValueRow({
    super.key,
    required this.label,
    required this.value,
    this.unit,
    this.badge,
    this.first = false,
  });

  final String label;
  final String value;

  /// Optional muted unit appended after the bold value ("170 cm").
  final String? unit;

  /// When set, renders a maroon pill with this text instead of the plain
  /// bold value (used for the Severity row: "7 / 10 · Severe").
  final String? badge;

  /// Hides the top divider for the first row in a group.
  final bool first;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8),
      decoration: BoxDecoration(
        border: first
            ? null
            : const Border(
                top: BorderSide(color: AppColors.borderSubtle),
              ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Text(
              label,
              style: const TextStyle(
                fontSize: 14,
                height: 20 / 14,
                fontWeight: FontWeight.w500,
                color: AppColors.textMuted,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Flexible(
            child: badge != null
                ? Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: AppColors.primaryMaroon,
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: Text(
                      badge!,
                      textAlign: TextAlign.right,
                      style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                        color: AppColors.cardSurface,
                      ),
                    ),
                  )
                : Text.rich(
                    TextSpan(
                      text: value,
                      style: const TextStyle(
                        fontSize: 14,
                        height: 20 / 14,
                        fontWeight: FontWeight.w700,
                        color: AppColors.textPrimary,
                      ),
                      children: [
                        if (unit != null)
                          TextSpan(
                            text: ' $unit',
                            style: const TextStyle(
                              fontSize: 14,
                              height: 20 / 14,
                              fontWeight: FontWeight.w500,
                              color: AppColors.textMuted,
                            ),
                          ),
                      ],
                    ),
                    textAlign: TextAlign.right,
                  ),
          ),
        ],
      ),
    );
  }
}
