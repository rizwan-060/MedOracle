import 'package:flutter/material.dart';

/// Central color palette for MedOracle.
///
/// Widget files must never hardcode hex values - every color used anywhere in
/// the app is declared here as a named token.
///
/// Two token groups live side by side:
///  * [brand]     - the MedOracle brand palette defined in the project rules.
///  * [ref] tokens - the exact values used by the `MedOracle v3.1 - Intake Flow`
///                   design reference, kept verbatim so screens can be
///                   translated 1:1.
abstract final class AppColors {
  //
  // ---------------------------------------------------------------------------
  // Brand palette (project design rules)
  // ---------------------------------------------------------------------------
  //
  static const Color primaryMaroon = Color(0xFF6C3B43);
  static const Color maroonDark = Color(0xFF4E2831);
  static const Color dustyTaupe = Color(0xFFB49C91);
  static const Color mutedGreen = Color(0xFF526853);
  static const Color greenSurface = Color(0xFFEAF1EB);
  static const Color amberWarning = Color(0xFFC4822B);
  static const Color amberSurface = Color(0xFFFBF5EB);
  static const Color canvasBackground = Color(0xFFF7F5F5);
  static const Color cardSurface = Color(0xFFFFFFFF);
  static const Color borderSubtle = Color(0xFFE8E2E1);
  static const Color textPrimary = Color(0xFF1C1819);
  static const Color textMuted = Color(0xFF6F6567);

  //
  // ---------------------------------------------------------------------------
  // Design reference tokens - MedOracle v3.1 intake flow (v8 frames)
  // ---------------------------------------------------------------------------
  //

  /// Primary ink used for body copy, headings and chevrons.
  ///
  /// Aliases [textPrimary] so Step 1 matches the palette used by Steps 2-5.
  static const Color refInk = textPrimary;

  /// Maroon used for the header, primary CTA and selected controls.
  ///
  /// Aliases [primaryMaroon] so Step 1 matches the palette used by Steps 2-5.
  static const Color refPlum = primaryMaroon;

  /// Top stop of the primary CTA / selected-segment gradient.
  static const Color refPlumLight = primaryMaroon;

  /// Bottom stop of the primary CTA gradient.
  static const Color refPlumDark = maroonDark;

  /// Border colour of resting text fields and segmented options.
  ///
  /// Aliases [dustyTaupe] so Step 1 matches the palette used by Steps 2-5.
  static const Color refFieldBorder = dustyTaupe;

  /// Secondary text: field sub-values, units, card sub-titles.
  ///
  /// Aliases [textMuted] so Step 1 matches the palette used by Steps 2-5.
  static const Color refSubtitle = textMuted;

  /// Tint used for "positive" micro-labels.
  ///
  /// Aliases [greenSurface] so Step 1 matches the palette used by Steps 2-5.
  static const Color refMint = greenSurface;

  /// Fill of the autosaved check circle.
  static const Color refAutosaveCircle = Color(0xFF8FC4A8);

  /// Stroke of the autosaved check tick.
  static const Color refAutosaveTick = Color(0xFF1A4D37);

  /// Progress rail colour for inactive steps (white at 22% opacity).
  static const Color refProgressIdle = Color(0x38FFFFFF);

  /// Active progress rail fill (matches Steps 2-5's solid white track).
  static const Color refProgressActive = onPlum;

  /// Canvas gradient stops (top -> mid -> bottom).
  static const Color refCanvasTop = dustyTaupe;
  static const Color refCanvasMid = canvasBackground;
  static const Color refCanvasBottom = canvasBackground;

  /// Glow tints painted behind the expanded (active) card.
  static const Color refGlowA = Color(0xFF8C92AC);
  static const Color refGlowB = Color(0xFFC3C7D8);

  /// Hairline ring drawn around white cards.
  static const Color refCardRing = Color(0x38321926); // rgba(50,25,38,0.22)

  /// Soft drop shadow under white cards.
  static const Color refCardShadow = Color(0x0F321926); // rgba(50,25,38,0.06)

  /// Text colour used on maroon surfaces.
  static const Color onPlum = Color(0xFFFFFFFF);

  /// Drop shadow under the maroon header (maroon dark at 80% opacity).
  static const Color headerShadow = Color(0xCC4E2831);

  /// 1px light top highlight on the maroon header (white at 14%).
  static const Color headerHighlight = Color(0x24FFFFFF);

  /// Soft maroon shadow cast by raised controls (maroon at 70%).
  static const Color controlShadowStrong = Color(0xB36C3B43);

  /// Tighter soft shadow under raised controls (ink at 30%).
  static const Color controlShadowSoft = Color(0x4D1C1819);

  /// Ring drawn around a focused field (maroon at 28%).
  static const Color focusRing = Color(0x476C3B43);

  /// Shadow under a selected segmented option (maroon at 65%).
  static const Color segmentShadowSelected = Color(0xA66C3B43);

  /// Shadow under an unselected segmented option (maroon at 30%).
  static const Color segmentShadowIdle = Color(0x4D6C3B43);

  /// Drop shadow under the footer glass pill (maroon at 38%).
  static const Color glassPillShadow = Color(0x616C3B43);

  /// 1px light border on the primary CTA (white at 22%).
  static const Color ctaBorder = Color(0x38FFFFFF);

  /// Fill of an unselected segmented option (white at 62%).
  static const Color segmentIdleFill = Color(0x9EFFFFFF);

  //
  // ---------------------------------------------------------------------------
  // Gradients
  // ---------------------------------------------------------------------------
  //

  /// Full-screen canvas wash behind scrollable cards.
  ///
  /// Matches the Steps 2-5 chrome: dusty taupe fading into the canvas
  /// background by 35% of the height.
  static const LinearGradient canvasGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [dustyTaupe, canvasBackground],
    stops: [0.0, 0.35],
  );

  /// Primary call-to-action background.
  static const LinearGradient ctaGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [primaryMaroon, primaryMaroon, maroonDark],
    stops: [0.0, 0.55, 1.0],
  );

  /// Selected segmented-control background.
  static const LinearGradient segmentSelectedGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [refPlumLight, refPlum],
  );

  /// Gloss highlight sweeping over the top half of the primary CTA.
  static const LinearGradient ctaGlossGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [Color(0x3DFFFFFF), Color(0x05FFFFFF)],
  );

  /// Active progress rail (solid white, matching Steps 2-5).
  static const LinearGradient progressActiveGradient = LinearGradient(
    colors: [refProgressActive, refProgressActive],
  );

  /// Glossy white pill fill used for secondary header/footer actions.
  static const LinearGradient pillGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [Color(0xF2FFFFFF), Color(0x00FFFFFF)],
  );

  /// Diagonal sheen painted over the maroon intake header (160deg in CSS).
  static const LinearGradient headerSheenGradient = LinearGradient(
    begin: Alignment(-0.342, -0.94),
    end: Alignment(0.342, 0.94),
    colors: <Color>[
      Color(0x1AFFFFFF), // rgba(255,255,255,0.10)
      Color(0x00FFFFFF), // rgba(255,255,255,0) @ 45%
      Color(0x33000000), // rgba(0,0,0,0.20)
    ],
    stops: <double>[0.0, 0.45, 1.0],
  );

  /// Soft plum glow in the top-right corner of the maroon header.
  static const RadialGradient headerGlowGradient = RadialGradient(
    center: Alignment(0.8, -1.2), // circle at 90% -10%
    radius: 4.5,
    colors: <Color>[Color(0x8CAA98A9), Color(0x00AA98A9)],
    stops: <double>[0.0, 0.55],
  );
}
