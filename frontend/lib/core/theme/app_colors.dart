import 'package:flutter/material.dart';

/// Central color palette for MedOracle adhering strictly to @AGENTS.md.
///
/// Widget files must never hardcode hex values - every color used anywhere in
/// the app is declared here as a named token.
abstract final class AppColors {
  //
  // ---------------------------------------------------------------------------
  // Strict AGENTS.md Design Tokens
  // ---------------------------------------------------------------------------
  //

  /// Canvas Background: #FAF9F5 (Warm cream / ecru background)
  static const Color canvasBackground = Color(0xFFFAF9F5);
  static const Color canvas = canvasBackground;

  /// Card Surface: #FFFFFF (Core reasoning cards, white pill buttons)
  static const Color cardSurface = Color(0xFFFFFFFF);
  static const Color card = cardSurface;

  /// Text Primary: #2C2520 (Earth brown text)
  static const Color textPrimary = Color(0xFF2C2520);

  /// Header Text: #4D738F (Soft Slate / Powder Blue for headers)
  static const Color headerText = Color(0xFF4D738F);
  static const Color primary = headerText;
  static const Color headerBg = headerText;

  /// Primary Accent: #E04E26 (Burnt Orange active elements/buttons)
  static const Color primaryAccent = Color(0xFFE04E26);
  static const Color cta = primaryAccent;
  static const Color primaryMaroon = primaryAccent;
  static const Color maroonDark = Color(0xFFC03C17);

  /// Alert Medium: #E89A3E (Ochre / Amber indicators)
  static const Color alertMedium = Color(0xFFE89A3E);
  static const Color amberWarning = alertMedium;
  static const Color amberSurface = Color(0xFFFBF5EB);

  /// Border Subtle: #D6CFC4 (Subtle neutral container outlines)
  static const Color borderSubtle = Color(0xFFD6CFC4);
  static const Color border = borderSubtle;
  static const Color dustyTaupe = borderSubtle;
  static const Color refFieldBorder = borderSubtle;

  //
  // ---------------------------------------------------------------------------
  // Supporting Neutral & Semantic Tokens
  // ---------------------------------------------------------------------------
  //
  static const Color textMuted = Color(0xFF6C757D);
  static const Color textSecondary = Color(0xFF6C757D);
  static const Color secondarySurface = Color(0xFFE8EEF3);
  static const Color lightNeutralFill = Color(0xFFF3EFEA);

  static const Color mutedGreen = Color(0xFF2D7D68);
  static const Color greenSurface = Color(0xFFE2F1EC);

  // Status & Badges
  static const Color successBadgeFill = Color(0xFFE2F1EC);
  static const Color successBadgeText = Color(0xFF2D7D68);
  static const Color urgencyBadgeFill = Color(0xFFFCEEE9);
  static const Color urgencyBadgeText = Color(0xFFE04E26);
  static const Color neutralTagFill = Color(0xFFEFECE6);
  static const Color neutralTagText = Color(0xFF5A626A);

  // Navigation
  static const Color navActive = Color(0xFFE04E26);
  static const Color navInactive = Color(0xFF8C959D);

  //
  // ---------------------------------------------------------------------------
  // Design Reference Compat Tokens
  // ---------------------------------------------------------------------------
  //
  static const Color refInk = textPrimary;
  static const Color refPlum = primaryAccent;
  static const Color refPlumLight = primaryAccent;
  static const Color refPlumDark = maroonDark;
  static const Color refSubtitle = textMuted;
  static const Color refMint = greenSurface;
  static const Color refAutosaveCircle = Color(0xFF8FC4A8);
  static const Color refAutosaveTick = Color(0xFF1A4D37);
  static const Color refProgressIdle = Color(0x38FFFFFF);
  static const Color refProgressActive = onPlum;

  static const Color refCanvasTop = borderSubtle;
  static const Color refCanvasMid = canvasBackground;
  static const Color refCanvasBottom = canvasBackground;

  static const Color refGlowA = Color(0xFF8C92AC);
  static const Color refGlowB = Color(0xFFC3C7D8);
  static const Color refControlAccent = headerText;
  static const Color refControlTrackIdle = Color(0xFFD9D2DC);
  static const Color refControlDivider = Color(0xFFECE7EE);

  static const Color refBandStatus = Color(0xFFDFF0E6);
  static const Color refBandSubtitle = Color(0xFFDDD8E4);
  static const Color refDeltaSurface = Color(0xFFDFF0E6);
  static const Color refPillBorderIdle = Color(0xFFCFC5CE);
  static const Color refPillSurfaceIdle = Color(0xFFF3EDF2);
  static const Color refBarSurface = Color(0xC7F8F6F9);

  static const Color refCardRing = borderSubtle;
  static const Color refCardShadow = Color(0x0F2C2520);
  static const Color onPlum = Color(0xFFFFFFFF);

  static const Color headerShadow = Color(0x334D738F);
  static const Color headerHighlight = Color(0x24FFFFFF);
  static const Color controlShadowStrong = Color(0x26E04E26);
  static const Color controlShadowSoft = Color(0x1A2C2520);
  static const Color focusRing = Color(0x40E04E26);
  static const Color segmentShadowSelected = Color(0x40E04E26);
  static const Color segmentShadowIdle = Color(0x1AE04E26);
  static const Color glassPillShadow = Color(0x1A4D738F);
  static const Color ctaBorder = Color(0x38FFFFFF);
  static const Color segmentIdleFill = Color(0x9EFFFFFF);

  //
  // ---------------------------------------------------------------------------
  // Gradients
  // ---------------------------------------------------------------------------
  //
  static const LinearGradient canvasGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [canvasBackground, canvasBackground],
  );

  static const LinearGradient ctaGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [primaryAccent, primaryAccent, maroonDark],
    stops: [0.0, 0.55, 1.0],
  );

  static const LinearGradient segmentSelectedGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [primaryAccent, maroonDark],
  );

  static const LinearGradient ctaGlossGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [Color(0x3DFFFFFF), Color(0x05FFFFFF)],
  );

  static const LinearGradient progressActiveGradient = LinearGradient(
    colors: [refProgressActive, refProgressActive],
  );

  static const LinearGradient pillGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [Color(0xF2FFFFFF), Color(0x00FFFFFF)],
  );

  static const LinearGradient headerSheenGradient = LinearGradient(
    begin: Alignment(-0.342, -0.94),
    end: Alignment(0.342, 0.94),
    colors: <Color>[
      Color(0x1AFFFFFF),
      Color(0x00FFFFFF),
      Color(0x33000000),
    ],
    stops: <double>[0.0, 0.45, 1.0],
  );

  static const RadialGradient headerGlowGradient = RadialGradient(
    center: Alignment(0.8, -1.2),
    radius: 4.5,
    colors: <Color>[Color(0x4D4D738F), Color(0x004D738F)],
    stops: <double>[0.0, 0.55],
  );

  //
  // ---------------------------------------------------------------------------
  // Onboarding Design Tokens (from Lovable Reference)
  // ---------------------------------------------------------------------------
  //
  /// Brand circle and primary CTA maroon (#A82D38)
  static const Color onboardingMaroon = Color(0xFFA82D38);

  /// Overline categories (WELCOME, A COMPLETE PICTURE, LOOK AHEAD) (#C95D3B)
  static const Color onboardingOverline = Color(0xFFC95D3B);

  /// Titles: #1B2533 (Deep charcoal / slate)
  static const Color onboardingTitle = Color(0xFF1B2533);

  /// Subtitles & body descriptions: #64748B
  static const Color onboardingBody = Color(0xFF64748B);

  /// Background ambient glows
  static const Color onboardingAuraTopLeft = Color(0xFFFBF0ED);
  static const Color onboardingAuraBottomRight = Color(0xFFFCF4EE);

  /// Soft pink pill background for icons & illustrative badge (#FCEEEB)
  static const Color onboardingBadgeFill = Color(0xFFFCEEEB);

  /// Silhouette body tone (#F7E5E1)
  static const Color onboardingSilhouette = Color(0xFFF7E5E1);
  static const Color onboardingSilhouetteStroke = Color(0xFFE8C9C1);

  /// ECG & active chart line (#A82D38)
  static const Color onboardingEcgLine = Color(0xFFA82D38);

  /// Inactive chart trajectory path & dashed lines (#94A3B8)
  static const Color onboardingInactiveLine = Color(0xFF94A3B8);

  /// Slider active track (#DE6B48)
  static const Color onboardingSliderActive = Color(0xFFDE6B48);
  static const Color onboardingSliderInactive = Color(0xFFE2E8F0);

  /// Pagination dots
  static const Color onboardingDotActive = Color(0xFFA82D38);
  static const Color onboardingDotInactive = Color(0xFFCBD5E1);

  /// Subtle card borders & dividers
  static const Color onboardingCardBorder = Color(0xFFEDE7E1);
  static const Color onboardingCardSurface = Color(0xFFFFFFFF);
  static const Color onboardingSkipBorder = Color(0xFFE2E8F0);
  static const Color onboardingSkipText = Color(0xFF475569);
}

