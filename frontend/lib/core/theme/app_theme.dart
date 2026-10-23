import 'package:flutter/material.dart';

import 'app_colors.dart';
import 'app_text_styles.dart';

/// Global [ThemeData] for MedOracle adhering strictly to @AGENTS.md.
abstract final class AppTheme {
  static ThemeData get light {
    final ColorScheme scheme = ColorScheme(
      brightness: Brightness.light,
      primary: AppColors.headerText,
      onPrimary: Colors.white,
      primaryContainer: AppColors.secondarySurface,
      onPrimaryContainer: AppColors.headerText,
      secondary: AppColors.primaryAccent,
      onSecondary: Colors.white,
      tertiary: AppColors.mutedGreen,
      onTertiary: Colors.white,
      error: AppColors.alertMedium,
      onError: Colors.white,
      surface: AppColors.cardSurface,
      onSurface: AppColors.textPrimary,
      onSurfaceVariant: AppColors.textSecondary,
      outline: AppColors.borderSubtle,
      outlineVariant: AppColors.borderSubtle,
      shadow: AppColors.textPrimary,
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: scheme,
      fontFamily: AppTextStyles.fontFamily,
      scaffoldBackgroundColor: AppColors.canvasBackground,
      splashFactory: InkSparkle.splashFactory,
      dividerTheme: const DividerThemeData(
        color: AppColors.borderSubtle,
        thickness: 1,
        space: 1,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.cardSurface,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        hintStyle: AppTextStyles.fieldHint,
        border: _fieldBorder(AppColors.borderSubtle),
        enabledBorder: _fieldBorder(AppColors.borderSubtle),
        focusedBorder: _fieldBorder(AppColors.primaryAccent, width: 1.5),
      ),
      snackBarTheme: const SnackBarThemeData(
        backgroundColor: AppColors.textPrimary,
        contentTextStyle: AppTextStyles.helperText,
        behavior: SnackBarBehavior.floating,
      ),
      textSelectionTheme: const TextSelectionThemeData(
        cursorColor: AppColors.primaryAccent,
        selectionColor: Color(0x33E04E26),
        selectionHandleColor: AppColors.primaryAccent,
      ),
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: AppColors.primaryAccent,
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
