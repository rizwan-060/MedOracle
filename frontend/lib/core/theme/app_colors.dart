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

  /// Primary ink used for body copy, headings and chevrons (`#261B22`).
  static const Color refInk = Color(0xFF261B22);

  /// Plum-maroon used for the header, primary CTA and selected controls.
  static const Color refPlum = Color(0xFF614051);

  /// Top stop of the primary CTA / selected-segment gradient.
  static const Color refPlumLight = Color(0xFF755062);

  /// Bottom stop of the primary CTA gradient.
  static const Color refPlumDark = Color(0xFF523543);

  /// Border colour of resting text fields and segmented options.
  static const Color refFieldBorder = Color(0xFF7D6E83);

  /// Secondary text: field sub-values, units, card sub-titles.
  static const Color refSubtitle = Color(0xFF5B4A55);

  /// Mint tint used for "positive" micro-labels.
  static const Color refMint = Color(0xFFDFF0E6);

  /// Fill of the autosaved check circle.
  static const Color refAutosaveCircle = Color(0xFF8FC4A8);

  /// Stroke of the autosaved check tick.
  static const Color refAutosaveTick = Color(0xFF1A4D37);

  /// Progress rail colour for inactive steps (white at 22% opacity).
  static const Color refProgressIdle = Color(0x38FFFFFF);

  /// Left stop of the active progress rail gradient.
  static const Color refProgressActiveStart = Color(0xFFC5C7D8);

  /// Right stop of the active progress rail gradient.
  static const Color refProgressActiveEnd = Color(0xFF8C92AC);

  /// Canvas gradient stops (top -> mid -> bottom).
  static const Color refCanvasTop = Color(0xFFDDD5DC);
  static const Color refCanvasMid = Color(0xFFEAE4EA);
  static const Color refCanvasBottom = Color(0xFFF5F1F5);

  /// Glow tints painted behind the expanded (active) card.
  static const Color refGlowA = Color(0xFF8C92AC);
  static const Color refGlowB = Color(0xFFC3C7D8);

  /// Hairline ring drawn around white cards.
  static const Color refCardRing = Color(0x38321926); // rgba(50,25,38,0.22)

  /// Soft drop shadow under white cards.
  static const Color refCardShadow = Color(0x0F321926); // rgba(50,25,38,0.06)

  /// Text colour used on maroon surfaces.
  static const Color onPlum = Color(0xFFFFFFFF);

  //
  // ---------------------------------------------------------------------------
  // Gradients
  // ---------------------------------------------------------------------------
  //

  /// Full-screen canvas wash behind scrollable cards.
  static const LinearGradient canvasGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [refCanvasTop, refCanvasMid, refCanvasBottom],
    stops: [0.0, 0.45, 1.0],
  );

  /// Primary call-to-action background.
  static const LinearGradient ctaGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [refPlumLight, refPlum, refPlumDark],
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

  /// Active progress rail.
  static const LinearGradient progressActiveGradient = LinearGradient(
    colors: [refProgressActiveStart, refProgressActiveEnd],
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
