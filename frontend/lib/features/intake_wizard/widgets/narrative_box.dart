import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Muted inset panel used to display free-text narrative on the review
/// screen (design's `.nar`).
class NarrativeBox extends StatelessWidget {
  const NarrativeBox(this.text, {super.key});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 6),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 11),
      decoration: BoxDecoration(
        color: AppColors.canvasBackground,
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Text(
        text,
        style: const TextStyle(
          fontSize: 14,
          height: 20 / 14,
          fontWeight: FontWeight.w400,
          color: AppColors.textPrimary,
        ),
      ),
    );
  }
}
