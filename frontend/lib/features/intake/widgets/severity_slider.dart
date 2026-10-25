import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Human-readable band for a 1–10 severity value.
String severityDescriptor(int value) {
  if (value <= 3) return 'Mild';
  if (value <= 6) return 'Moderate';
  return 'Severe';
}

/// Custom 1–10 severity control from the design: hint + live badge row,
/// an 8px gradient track with a 26px thumb, and min/max scale labels.
class SeveritySlider extends StatelessWidget {
  const SeveritySlider({
    super.key,
    required this.value,
    required this.onChanged,
    this.min = 1,
    this.max = 10,
    this.hint = 'Drag to rate',
  });

  final int value;
  final ValueChanged<int> onChanged;
  final int min;
  final int max;
  final String hint;

  String get _descriptor => severityDescriptor(value);

  @override
  Widget build(BuildContext context) {
    final double fraction = (value - min) / (max - min);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              hint,
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: AppColors.textMuted,
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: AppColors.primaryMaroon,
                borderRadius: BorderRadius.circular(999),
              ),
              child: Text(
                '$value / $max · $_descriptor',
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: AppColors.cardSurface,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 18),
        LayoutBuilder(
          builder: (BuildContext context, BoxConstraints constraints) {
            return GestureDetector(
              behavior: HitTestBehavior.opaque,
              onHorizontalDragUpdate: (DragUpdateDetails details) {
                final double local =
                    details.localPosition.dx.clamp(0.0, constraints.maxWidth);
                final double t = constraints.maxWidth == 0
                    ? 0
                    : local / constraints.maxWidth;
                final int next = (min + t * (max - min)).round();
                if (next != value) onChanged(next.clamp(min, max));
              },
              child: SizedBox(
                height: 26,
                child: Stack(
                  alignment: Alignment.centerLeft,
                  children: [
                    // Inactive track.
                    Container(
                      height: 8,
                      decoration: BoxDecoration(
                        color: AppColors.borderSubtle,
                        borderRadius: BorderRadius.circular(999),
                      ),
                    ),
                    // Active gradient track.
                    Container(
                      height: 8,
                      width: constraints.maxWidth * fraction,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [
                            AppColors.dustyTaupe,
                            AppColors.primaryMaroon,
                          ],
                        ),
                        borderRadius: BorderRadius.circular(999),
                      ),
                    ),
                    // Thumb.
                    Positioned(
                      left: constraints.maxWidth * fraction - 13,
                      child: Container(
                        width: 26,
                        height: 26,
                        decoration: BoxDecoration(
                          color: AppColors.cardSurface,
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: AppColors.dustyTaupe,
                            width: 3,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: AppColors.textPrimary.withValues(alpha: 0.3),
                              blurRadius: 6,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        ),
        const SizedBox(height: 14),
        const Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '1',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: AppColors.textMuted,
              ),
            ),
            Text(
              '10',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: AppColors.textMuted,
              ),
            ),
          ],
        ),
      ],
    );
  }
}
