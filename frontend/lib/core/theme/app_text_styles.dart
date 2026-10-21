import 'package:flutter/material.dart';

import 'app_colors.dart';

/// Type scale of the MedOracle design reference.
///
/// Every style uses **Plus Jakarta Sans** (bundled in `assets/fonts`) with the
/// exact size / line-height / weight pairs measured from the v8 intake frames.
abstract final class AppTextStyles {
  /// Font family shared by the whole app.
  static const String fontFamily = 'Plus Jakarta Sans';

  // ---------------------------------------------------------------------------
  // Chrome
  // ---------------------------------------------------------------------------

  /// "MedOracle" wordmark in the maroon header (16 / 800).
  static const TextStyle brand = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    height: 20 / 16,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.onPlum,
  );

  /// "Autosaved" micro status in the header (12 / 700).
  static const TextStyle autosave = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    height: 16 / 12,
    fontWeight: FontWeight.w700,
    fontVariations: <FontVariation>[FontVariation('wght', 700)],
    color: AppColors.refMint,
  );

  /// "Save & exit" glass pill (13 / 800).
  static const TextStyle headerAction = TextStyle(
    fontFamily: fontFamily,
    fontSize: 13,
    height: 16 / 13,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.onPlum,
  );

  // ---------------------------------------------------------------------------
  // Cards
  // ---------------------------------------------------------------------------

  /// Expandable section title (17 / 24 / 800).
  static const TextStyle sectionTitle = TextStyle(
    fontFamily: fontFamily,
    fontSize: 17,
    height: 24 / 17,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.refInk,
  );

  /// Optional section sub-title (13 / 18 / 500).
  static const TextStyle sectionSubtitle = TextStyle(
    fontFamily: fontFamily,
    fontSize: 13,
    height: 18 / 13,
    fontWeight: FontWeight.w500,
    fontVariations: <FontVariation>[FontVariation('wght', 500)],
    color: AppColors.refSubtitle,
    overflow: TextOverflow.ellipsis,
  );

  // ---------------------------------------------------------------------------
  // Form controls
  // ---------------------------------------------------------------------------

  /// Field label above an input (12 / 16 / 700).
  static const TextStyle fieldLabel = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    height: 16 / 12,
    fontWeight: FontWeight.w700,
    fontVariations: <FontVariation>[FontVariation('wght', 700)],
    color: AppColors.refInk,
  );

  /// Value typed into a text field (15 / 500).
  static const TextStyle fieldValue = TextStyle(
    fontFamily: fontFamily,
    fontSize: 15,
    height: 20 / 15,
    fontWeight: FontWeight.w500,
    fontVariations: <FontVariation>[FontVariation('wght', 500)],
    color: AppColors.refInk,
  );

  /// Unit suffix inside a text field (13 / 600).
  static const TextStyle fieldUnit = TextStyle(
    fontFamily: fontFamily,
    fontSize: 13,
    height: 18 / 13,
    fontWeight: FontWeight.w600,
    fontVariations: <FontVariation>[FontVariation('wght', 600)],
    color: AppColors.refSubtitle,
  );

  /// Placeholder / hint inside a text field (15 / 500).
  static const TextStyle fieldHint = TextStyle(
    fontFamily: fontFamily,
    fontSize: 15,
    height: 20 / 15,
    fontWeight: FontWeight.w500,
    fontVariations: <FontVariation>[FontVariation('wght', 500)],
    color: AppColors.refSubtitle,
  );

  /// Unselected segmented option (14 / 500).
  static const TextStyle segmentOption = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    height: 18 / 14,
    fontWeight: FontWeight.w500,
    fontVariations: <FontVariation>[FontVariation('wght', 500)],
    color: AppColors.refInk,
  );

  /// Selected segmented option (14 / 800).
  static const TextStyle segmentOptionSelected = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    height: 18 / 14,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.onPlum,
  );

  // ---------------------------------------------------------------------------
  // Actions
  // ---------------------------------------------------------------------------

  /// Primary pill CTA (16 / 700).
  static const TextStyle primaryAction = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    height: 20 / 16,
    fontWeight: FontWeight.w700,
    fontVariations: <FontVariation>[FontVariation('wght', 700)],
    color: AppColors.onPlum,
    shadows: <Shadow>[Shadow(color: Color(0x47000000), offset: Offset(0, 1))],
  );

  /// Glass "Back" pill (14 / 700).
  static const TextStyle secondaryAction = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    height: 18 / 14,
    fontWeight: FontWeight.w700,
    fontVariations: <FontVariation>[FontVariation('wght', 700)],
    color: AppColors.refPlum,
  );

  /// Body copy used by helper/disclaimer text (13 / 500).
  static const TextStyle helperText = TextStyle(
    fontFamily: fontFamily,
    fontSize: 13,
    height: 18 / 13,
    fontWeight: FontWeight.w500,
    fontVariations: <FontVariation>[FontVariation('wght', 500)],
    color: AppColors.refSubtitle,
  );
}
