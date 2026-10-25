import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Small bold group caption inside a review card (design's `.sub`), e.g.
/// "Lipid Panel". When [dividerAbove] is true it gets the hairline
/// separator used between groups ("Current Medications", "Family History").
class ReviewSubHeader extends StatelessWidget {
  const ReviewSubHeader(this.text, {super.key, this.dividerAbove = false});

  final String text;
  final bool dividerAbove;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.only(top: dividerAbove ? 16 : 12),
      padding: dividerAbove
          ? const EdgeInsets.only(top: 12)
          : null,
      decoration: dividerAbove
          ? const BoxDecoration(
              border: Border(
                top: BorderSide(color: AppColors.borderSubtle),
              ),
            )
          : null,
      child: Text(
        text,
        style: const TextStyle(
          fontSize: 12,
          height: 16 / 12,
          fontWeight: FontWeight.w800,
          color: AppColors.textPrimary,
        ),
      ),
    );
  }
}
