import 'package:flutter/material.dart';

import 'app_colors.dart';
import 'app_text_styles.dart';

/// Global [ThemeData] for MedOracle.
///
/// The app is a light-themed, mobile-first UI built around the maroon/plum
/// palette of the intake-flow design reference.
abstract final class AppTheme {
  static ThemeData get light {
    final ColorScheme scheme = ColorScheme(
      brightness: Brightness.light,
      primary: AppColors.refPlum,
      onPrimary: AppColors.onPlum,
      primaryContainer: AppColors.refPlumLight,
      onPrimaryContainer: AppColors.onPlum,
      secondary: AppColors.primaryMaroon,
      onSecondary: AppColors.onPlum,
      tertiary: AppColors.mutedGreen,
      onTertiary: AppColors.onPlum,
      error: AppColors.amberWarning,
      onError: AppColors.onPlum,
      surface: AppColors.cardSurface,
      onSurface: AppColors.refInk,
      onSurfaceVariant: AppColors.refSubtitle,
      outline: AppColors.refFieldBorder,
      outlineVariant: AppColors.borderSubtle,
      shadow: AppColors.refInk,
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: scheme,
      fontFamily: AppTextStyles.fontFamily,
      scaffoldBackgroundColor: AppColors.refCanvasBottom,
      splashFactory: InkSparkle.splashFactory,
      dividerTheme: const DividerThemeData(
        color: AppColors.borderSubtle,
        thickness: 1,
        space: 1,
      ),
      inputDecorationTheme: InputDecorationTheme(
        isDense: true,
        filled: true,
        fillColor: AppColors.cardSurface,
        contentPadding: const EdgeInsets.symmetric(horizontal: 12),
        hintStyle: AppTextStyles.fieldHint,
        border: _fieldBorder(AppColors.refFieldBorder),
        enabledBorder: _fieldBorder(AppColors.refFieldBorder),
        focusedBorder: _fieldBorder(AppColors.refPlum, width: 1.5),
      ),
      snackBarTheme: const SnackBarThemeData(
        backgroundColor: AppColors.refInk,
        contentTextStyle: AppTextStyles.helperText,
        behavior: SnackBarBehavior.floating,
      ),
      textSelectionTheme: const TextSelectionThemeData(
        cursorColor: AppColors.refPlum,
        selectionColor: Color(0x556C3B43),
        selectionHandleColor: AppColors.refPlum,
      ),
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: AppColors.refPlum,
      ),
    );
  }

  static OutlineInputBorder _fieldBorder(Color color, {double width = 1.5}) {
    return OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: color, width: width),
    );
  }
}
