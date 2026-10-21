import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Multi-line "Clinical Notes" input matching the design's 80px
/// bordered textarea with muted placeholder.
class NotesTextArea extends StatelessWidget {
  const NotesTextArea({
    super.key,
    this.controller,
    this.hintText,
    this.onChanged,
    this.height = 80,
  });

  final TextEditingController? controller;
  final String? hintText;
  final ValueChanged<String>? onChanged;

  final double height;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 11),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.dustyTaupe, width: 1.5),
      ),
      child: TextField(
        controller: controller,
        onChanged: onChanged,
        maxLines: null,
        expands: true,
        textAlignVertical: TextAlignVertical.top,
        cursorColor: AppColors.primaryMaroon,
        style: const TextStyle(
          fontSize: 14,
          height: 20 / 14,
          fontWeight: FontWeight.w500,
          color: AppColors.textPrimary,
        ),
        decoration: InputDecoration(
          isDense: true,
          border: InputBorder.none,
          contentPadding: EdgeInsets.zero,
          hintText: hintText,
          hintStyle: const TextStyle(
            fontSize: 14,
            height: 20 / 14,
            fontWeight: FontWeight.w400,
            color: AppColors.textMuted,
          ),
        ),
      ),
    );
  }
}
