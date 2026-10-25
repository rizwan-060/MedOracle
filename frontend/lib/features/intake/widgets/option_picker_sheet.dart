import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// Opens a bottom-sheet option picker (design's dropdown fields, e.g.
/// Frequency / Relative) and returns the chosen value, or null if
/// dismissed.
Future<String?> showOptionPickerSheet(
  BuildContext context, {
  required String title,
  required List<String> options,
}) {
  return showModalBottomSheet<String>(
    context: context,
    backgroundColor: AppColors.cardSurface,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
    ),
    builder: (BuildContext context) {
      return SafeArea(
        top: false,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 12),
              child: Text(
                title,
                style: AppTextStyles.instrumentSerif(
                  fontSize: 24,
                  fontWeight: FontWeight.w600,
                  color: AppColors.headerText,
                ),
              ),
            ),
            const Divider(height: 1, color: AppColors.borderSubtle),
            for (final String option in options)
              ListTile(
                dense: true,
                contentPadding: const EdgeInsets.symmetric(horizontal: 20),
                title: Text(
                  option,
                  style: AppTextStyles.lexend(
                    fontSize: 15,
                    fontWeight: FontWeight.w500,
                    color: AppColors.textPrimary,
                  ),
                ),
                onTap: () => Navigator.of(context).pop(option),
              ),
            const SizedBox(height: 8),
          ],
        ),
      );
    },
  );
}
