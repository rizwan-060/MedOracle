import 'package:google_fonts/google_fonts.dart';
import 'package:flutter/material.dart';

import 'app_colors.dart';

/// Type scale of the MedOracle design reference.
///
/// Strictly adheres to @AGENTS.md:
/// - Headings: Instrument Serif (28.0 screen titles, 24.0 card titles).
/// - Body & Inputs: Lexend (14.0 labels/body, 12.0 helpers).
abstract final class AppTextStyles {
  /// Font family shared by the whole app.
  static const String fontFamily = 'Lexend';

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
    fontSize: 24,
    height: 24 / 17,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.headerText,
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
    color: AppColors.textPrimary,
  );

  /// Value typed into a text field (15 / 500).
  static const TextStyle fieldValue = TextStyle(
    fontFamily: fontFamily,
    fontSize: 15,
    height: 20 / 15,
    fontWeight: FontWeight.w500,
    fontVariations: <FontVariation>[FontVariation('wght', 500)],
    color: AppColors.textPrimary,
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
    color: AppColors.textPrimary,
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

  // ---------------------------------------------------------------------------
  // Assessment / results surfaces
  // ---------------------------------------------------------------------------

  /// Uppercase eyebrow above a results headline (12 / 16 / 800).
  static const TextStyle eyebrow = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    height: 16 / 12,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    letterSpacing: 1.2,
    color: AppColors.refSubtitle,
  );

  /// Results screen headline (30 / 38 / 800).
  static const TextStyle resultsHeadline = TextStyle(
    fontFamily: fontFamily,
    fontSize: 30,
    height: 38 / 30,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.headerText,
  );

  /// Serif italic accent inside the results headline (38 / 38 / 400).
  static const TextStyle resultsHeadlineAccent = TextStyle(
    fontFamily: 'Instrument Serif',
    fontFamilyFallback: <String>['Georgia', 'Times New Roman', 'serif'],
    fontSize: 38,
    height: 38 / 38,
    fontStyle: FontStyle.italic,
    fontWeight: FontWeight.w400,
    color: AppColors.headerText,
  );

  /// Body copy under a results headline (15 / 22 / 500).
  static const TextStyle resultsBody = TextStyle(
    fontFamily: fontFamily,
    fontSize: 15,
    height: 22 / 15,
    fontWeight: FontWeight.w500,
    fontVariations: <FontVariation>[FontVariation('wght', 500)],
    color: AppColors.refSubtitle,
  );

  /// Conclusion line inside a results card (20 / 26 / 800).
  static const TextStyle cardHeadline = TextStyle(
    fontFamily: fontFamily,
    fontSize: 20,
    height: 26 / 20,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.headerText,
  );

  /// Chip / pill label (13 / 18 / 600).
  static const TextStyle chipLabel = TextStyle(
    fontFamily: fontFamily,
    fontSize: 13,
    height: 18 / 13,
    fontWeight: FontWeight.w600,
    fontVariations: <FontVariation>[FontVariation('wght', 600)],
    color: AppColors.textPrimary,
  );

  /// Label above a value inside a detail tile (12 / 16 / 600).
  static const TextStyle statLabel = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    height: 16 / 12,
    fontWeight: FontWeight.w600,
    fontVariations: <FontVariation>[FontVariation('wght', 600)],
    color: AppColors.refSubtitle,
  );

  /// Value inside a detail tile (22 / 28 / 800).
  static const TextStyle statValue = TextStyle(
    fontFamily: fontFamily,
    fontSize: 28,
    height: 28 / 22,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.headerText,
  );

  /// Large headline metric (32 / 38 / 800).
  static const TextStyle metricValue = TextStyle(
    fontFamily: fontFamily,
    fontSize: 32,
    height: 38 / 32,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.headerText,
  );

  /// Caption next to a headline metric (13 / 18 / 600).
  static const TextStyle metricLabel = TextStyle(
    fontFamily: fontFamily,
    fontSize: 13,
    height: 18 / 13,
    fontWeight: FontWeight.w600,
    fontVariations: <FontVariation>[FontVariation('wght', 600)],
    color: AppColors.refSubtitle,
  );

  /// Emphasised body copy inside a callout (15 / 22 / 600).
  static const TextStyle bodyEmphasis = TextStyle(
    fontFamily: fontFamily,
    fontSize: 15,
    height: 22 / 15,
    fontWeight: FontWeight.w600,
    fontVariations: <FontVariation>[FontVariation('wght', 600)],
    color: AppColors.textPrimary,
  );

  /// `Completed` status label (12 / 16 / 700).
  static const TextStyle statusBadge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    height: 16 / 12,
    fontWeight: FontWeight.w700,
    fontVariations: <FontVariation>[FontVariation('wght', 700)],
    color: AppColors.mutedGreen,
  );

  /// Fine print under the results actions (12.5 / 18 / 600).
  static const TextStyle finePrint = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12.5,
    height: 18 / 12.5,
    fontWeight: FontWeight.w600,
    fontVariations: <FontVariation>[FontVariation('wght', 600)],
    color: AppColors.refSubtitle,
  );

  /// Conclusion bar of the reasoning map (15 / 20 / 800).
  static const TextStyle resultBarTitle = TextStyle(
    fontFamily: fontFamily,
    fontSize: 15,
    height: 20 / 15,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.onPlum,
  );

  /// Confidence line under the conclusion bar (13 / 18 / 600).
  static const TextStyle resultBarConfidence = TextStyle(
    fontFamily: fontFamily,
    fontSize: 13,
    height: 18 / 13,
    fontWeight: FontWeight.w600,
    fontVariations: <FontVariation>[FontVariation('wght', 600)],
    color: AppColors.onPlum,
  );

  // ---------------------------------------------------------------------------
  // Home dashboard
  // ---------------------------------------------------------------------------

  /// Dashboard greeting next to the avatar (22 / 28 / 800).
  static const TextStyle dashboardGreeting = TextStyle(
    fontFamily: fontFamily,
    fontSize: 28,
    height: 28 / 22,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.textPrimary,
  );

  /// Dashboard section heading (18 / 24 / 800).
  static const TextStyle dashboardSectionTitle = TextStyle(
    fontFamily: fontFamily,
    fontSize: 18,
    height: 24 / 18,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.textPrimary,
  );

  /// Trailing section action, e.g. `See all` (14 / 20 / 800).
  static const TextStyle dashboardSectionAction = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    height: 20 / 14,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.primaryMaroon,
  );

  /// Title of a wide dashboard action card (16 / 22 / 800).
  static const TextStyle dashboardCardTitle = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    height: 22 / 16,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.textPrimary,
  );

  /// Sub-title of a wide dashboard action card (13 / 18 / 500).
  static const TextStyle dashboardCardSubtitle = TextStyle(
    fontFamily: fontFamily,
    fontSize: 13,
    height: 18 / 13,
    fontWeight: FontWeight.w500,
    fontVariations: <FontVariation>[FontVariation('wght', 500)],
    color: AppColors.textMuted,
  );

  /// Title of a compact dashboard action card (15 / 20 / 800).
  static const TextStyle dashboardCompactTitle = TextStyle(
    fontFamily: fontFamily,
    fontSize: 15,
    height: 20 / 15,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.textPrimary,
  );

  /// Sub-title of a compact dashboard action card (12 / 17 / 500).
  static const TextStyle dashboardCompactSubtitle = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    height: 17 / 12,
    fontWeight: FontWeight.w500,
    fontVariations: <FontVariation>[FontVariation('wght', 500)],
    color: AppColors.textMuted,
  );

  /// Condition name inside the hero metric card (20 / 26 / 800).
  static const TextStyle dashboardHeroTitle = TextStyle(
    fontFamily: fontFamily,
    fontSize: 20,
    height: 26 / 20,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.onPlum,
  );

  /// Uppercase eyebrow inside the hero metric card (12 / 16 / 800).
  static const TextStyle dashboardHeroEyebrow = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    height: 16 / 12,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    letterSpacing: 0.96,
    color: AppColors.onPlum,
  );

  /// Big number inside the risk gauge (56 / 56 / 800).
  static const TextStyle dashboardGaugeValue = TextStyle(
    fontFamily: fontFamily,
    fontSize: 56,
    height: 56 / 56,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.onPlum,
  );

  /// Caption under the gauge number (14 / 16 / 600).
  static const TextStyle dashboardGaugeCaption = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    height: 16 / 14,
    fontWeight: FontWeight.w600,
    fontVariations: <FontVariation>[FontVariation('wght', 600)],
    color: AppColors.onPlum,
  );

  /// End-of-scale labels under the gauge (12 / 16 / 700).
  static const TextStyle dashboardGaugeScale = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    height: 16 / 12,
    fontWeight: FontWeight.w700,
    fontVariations: <FontVariation>[FontVariation('wght', 700)],
    color: AppColors.onPlum,
  );

  /// Urgency pill of the hero metric card (13 / 16 / 800).
  static const TextStyle dashboardUrgency = TextStyle(
    fontFamily: fontFamily,
    fontSize: 13,
    height: 16 / 13,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.maroonDark,
  );

  /// Label of the hero call to action (16 / 20 / 800).
  static const TextStyle dashboardHeroAction = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    height: 20 / 16,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.textPrimary,
  );

  /// Month label of a recent-assessment date chip (11 / 13 / 800).
  static const TextStyle dashboardDateMonth = TextStyle(
    fontFamily: fontFamily,
    fontSize: 11,
    height: 13 / 11,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    letterSpacing: 0.6,
    color: AppColors.textMuted,
  );

  /// Day label of a recent-assessment date chip (19 / 23 / 800).
  static const TextStyle dashboardDateDay = TextStyle(
    fontFamily: fontFamily,
    fontSize: 19,
    height: 23 / 19,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.textPrimary,
  );

  /// Title of a recent-assessment row (15 / 20 / 800).
  static const TextStyle dashboardActivityTitle = TextStyle(
    fontFamily: fontFamily,
    fontSize: 15,
    height: 20 / 15,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.textPrimary,
  );

  /// Status pill of a recent-assessment row (12 / 16 / 800).
  static const TextStyle dashboardStatusBadge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    height: 16 / 12,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.refAutosaveTick,
  );

  /// Bottom navigation label (11 / 14 / 700).
  static const TextStyle dashboardNavLabel = TextStyle(
    fontFamily: fontFamily,
    fontSize: 11,
    height: 14 / 11,
    fontWeight: FontWeight.w700,
    fontVariations: <FontVariation>[FontVariation('wght', 700)],
    color: AppColors.textMuted,
  );

  /// Bottom navigation label of the selected tab (11 / 14 / 800).
  static const TextStyle dashboardNavLabelActive = TextStyle(
    fontFamily: fontFamily,
    fontSize: 11,
    height: 14 / 11,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.textPrimary,
  );

  // ---------------------------------------------------------------------------
  // Lifestyle simulation
  // ---------------------------------------------------------------------------

  /// Title of the simulation header band (28 / 34 / 800).
  static const TextStyle simulationTitle = TextStyle(
    fontFamily: fontFamily,
    fontSize: 28,
    height: 34 / 28,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    letterSpacing: -0.02 * 28,
    color: AppColors.onPlum,
  );

  /// Subtitle of the simulation header band (15 / 22 / 500).
  static const TextStyle simulationSubtitle = TextStyle(
    fontFamily: fontFamily,
    fontSize: 15,
    height: 22 / 15,
    fontWeight: FontWeight.w500,
    fontVariations: <FontVariation>[FontVariation('wght', 500)],
    color: AppColors.refBandSubtitle,
  );

  /// Status line of the simulation header band (13 / 18 / 700).
  static const TextStyle simulationBandStatus = TextStyle(
    fontFamily: fontFamily,
    fontSize: 13,
    height: 18 / 13,
    fontWeight: FontWeight.w700,
    fontVariations: <FontVariation>[FontVariation('wght', 700)],
    color: AppColors.refBandStatus,
  );

  /// Label above the baseline risk number (14 / 20 / 700).
  static const TextStyle simulationBaselineLabel = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    height: 20 / 14,
    fontWeight: FontWeight.w700,
    fontVariations: <FontVariation>[FontVariation('wght', 700)],
    color: AppColors.textMuted,
  );

  /// Baseline risk number (56 / 60 / 800).
  static const TextStyle simulationBaselineValue = TextStyle(
    fontFamily: fontFamily,
    fontSize: 56,
    height: 60 / 56,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    letterSpacing: -0.03 * 56,
    color: AppColors.textPrimary,
  );

  /// Unit next to the baseline risk number (18 / 24 / 600).
  static const TextStyle simulationBaselineUnit = TextStyle(
    fontFamily: fontFamily,
    fontSize: 18,
    height: 24 / 18,
    fontWeight: FontWeight.w600,
    fontVariations: <FontVariation>[FontVariation('wght', 600)],
    color: AppColors.textMuted,
  );

  /// Title of a what-if control row (16 / 22 / 700).
  static const TextStyle simulationControlTitle = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    height: 22 / 16,
    fontWeight: FontWeight.w700,
    fontVariations: <FontVariation>[FontVariation('wght', 700)],
    color: AppColors.textPrimary,
  );

  /// Read-out of a what-if control row (16 / 22 / 800).
  static const TextStyle simulationControlValue = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    height: 22 / 16,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.refControlAccent,
    fontFeatures: <FontFeature>[FontFeature.tabularFigures()],
  );

  /// Hint under a what-if control title (13 / 18 / 500).
  static const TextStyle simulationControlHint = TextStyle(
    fontFamily: fontFamily,
    fontSize: 13,
    height: 18 / 13,
    fontWeight: FontWeight.w500,
    fontVariations: <FontVariation>[FontVariation('wght', 500)],
    color: AppColors.textMuted,
  );

  /// End-of-scale labels under a slider (12 / 16 / 600).
  static const TextStyle simulationScaleLabel = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    height: 16 / 12,
    fontWeight: FontWeight.w600,
    fontVariations: <FontVariation>[FontVariation('wght', 600)],
    color: AppColors.textMuted,
  );

  /// Label of the simulated risk bar (13 / 18 / 700).
  static const TextStyle simulationBarLabel = TextStyle(
    fontFamily: fontFamily,
    fontSize: 13,
    height: 18 / 13,
    fontWeight: FontWeight.w700,
    fontVariations: <FontVariation>[FontVariation('wght', 700)],
    color: AppColors.textMuted,
  );

  /// Simulated risk number (40 / 44 / 800).
  static const TextStyle simulationBarValue = TextStyle(
    fontFamily: fontFamily,
    fontSize: 40,
    height: 44 / 40,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    letterSpacing: -0.03 * 40,
    color: AppColors.textPrimary,
    fontFeatures: <FontFeature>[FontFeature.tabularFigures()],
  );

  /// Unit next to the simulated risk number (14 / 20 / 600).
  static const TextStyle simulationBarUnit = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    height: 20 / 14,
    fontWeight: FontWeight.w600,
    fontVariations: <FontVariation>[FontVariation('wght', 600)],
    color: AppColors.textMuted,
  );

  /// Text of the delta pill (14 / 20 / 800).
  static const TextStyle simulationDeltaLabel = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    height: 20 / 14,
    fontWeight: FontWeight.w800,
    fontVariations: <FontVariation>[FontVariation('wght', 800)],
    color: AppColors.refAutosaveTick,
  );

  // ---------------------------------------------------------------------------
  // Design System Typography (Instrument Serif & Lexend)
  // ---------------------------------------------------------------------------

  /// Header font: Instrument Serif
  static TextStyle instrumentSerif({
    double fontSize = 28,
    FontWeight fontWeight = FontWeight.w600,
    Color color = AppColors.headerText,
    double height = 1.2,
    double letterSpacing = -0.5,
  }) {
    return GoogleFonts.instrumentSerif(
      fontSize: fontSize,
      fontWeight: fontWeight,
      color: color,
      height: height,
      letterSpacing: letterSpacing,
    );
  }

  /// Lexend font for body, inputs, buttons, and captions
  static TextStyle lexend({
    double fontSize = 14,
    FontWeight fontWeight = FontWeight.w400,
    Color color = AppColors.textPrimary,
    double? height,
    double? letterSpacing,
  }) {
    return GoogleFonts.lexend(
      fontSize: fontSize,
      fontWeight: fontWeight,
      color: color,
      height: height,
      letterSpacing: letterSpacing,
    );
  }
}
