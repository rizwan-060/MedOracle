import 'package:material_ui/material_ui.dart';

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
  static const Color accentDark = Color(0xFFC03C17);
  static const Color cta = primaryAccent;
  // Backward-compatible aliases for primaryAccent (Burnt Orange)
  static const Color primaryMaroon = primaryAccent;
  static const Color maroonDark = accentDark;

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
  // Authentication (Login / Sign Up) Reference Tokens
  // ---------------------------------------------------------------------------
  //

  /// Warm parchment sheet that overlaps the slate hero header.
  static const Color authSheet = Color(0xFFF9F6EF);

  /// Soft off-white fill used by pill inputs and social buttons.
  static const Color authInputSurface = Color(0xFFFFFDF8);

  /// Ember call-to-action used by the authentication references.
  static const Color authCta = Color(0xFFB5583A);

  /// Canonical terracotta accent for the intake flow.
  static const Color terraCotta = authCta;

  /// Deep ink used for values typed into authentication fields.
  static const Color authInk = Color(0xFF1E2A33);

  /// Canonical deep ink for primary copy on design-reference surfaces.
  static const Color deepInk = authInk;

  /// Pastel surfaces from the design reference palette.
  static const Color pastelMist = Color(0xFFDCE6ED);
  static const Color pastelSage = Color(0xFFE2ECE9);
  static const Color pastelSand = Color(0xFFF4ECE1);
  static const Color pastelBlush = Color(0xFFF8E5E5);
  static const Color pastelButter = Color(0xFFF9F3DC);

  /// Onboarding reference tokens. These stay in the theme so widget files
  /// never hardcode design-ref hex values.
  static const Color onboardingPeachSurface = Color(0xFFFDF1E6);
  static const Color onboardingPeachBorder = Color(0xFFF3C9A4);
  static const Color onboardingAmber = Color(0xFFF0A56E);
  static const Color onboardingHeartFill = Color(0xFFF6C9A3);
  static const Color onboardingHeartStroke = Color(0xFFE8935A);
  static const Color onboardingSlateLight = Color(0xFF8AACC0);
  static const Color onboardingSlateSoft = Color(0xFF6C8FA3);
  static const Color onboardingSlateDeep = Color(0xFF5C7E94);
  static const Color onboardingMutedInk = Color(0xFF5E7382);
  static const Color onboardingHint = Color(0xFF8DA1B0);
  static const Color onboardingLine = Color(0xFFC9D6DE);
  static const Color onboardingGaugeLow = Color(0xFFD5DEE5);
  static const Color onboardingGaugeHealthy = Color(0xFFBFD8CE);
  static const Color onboardingGaugeMid = Color(0xFFEBD9B8);
  static const Color onboardingGaugeHigh = Color(0xFFE3BFB1);
  static const Color onboardingLabelInk = Color(0xFF334155);
  static const Color onboardingInfoBody = Color(0xFF4A5B66);
  static const Color onboardingCoreBorder = Color(0xFF3E5F77);
  static const Color onboardingVitalsFill = Color(0xFFA8C0D0);
  static const Color onboardingVitalsBorder = Color(0xFF6B8AA0);
  static const Color onboardingHistoryFill = Color(0xFFA8C4B0);
  static const Color onboardingHistoryBorder = Color(0xFF6B9080);
  static const Color onboardingLifestyleFill = Color(0xFFD8C4A0);
  static const Color onboardingLifestyleBorder = Color(0xFF9D8050);
  static const Color onboardingRiskFill = Color(0xFFD8A8A8);
  static const Color onboardingRiskBorder = Color(0xFFA07070);
  static const Color onboardingCounterfactualFill = Color(0xFFD4C77A);
  static const Color onboardingCounterfactualBorder = Color(0xFFA09850);
  static const Color onboardingAgeFill = Color(0xFFE6F0F2);
  static const Color onboardingSexFill = Color(0xFFE4EEE3);
  static const Color onboardingBloodFill = Color(0xFFF4ECE1);
  static const Color onboardingNumberFill = Color(0xFFE6EDF1);
  static const Color onboardingStepperShadow = Color(0xFF36566D);
  static const Color onboardingAgeSubLabel = Color(0xFF4D6573);
  static const Color onboardingFoldSurface = Color(0xFFC7D9E0);
  static const Color onboardingPinHighlight = Color(0xFFFF8A80);
  static const Color onboardingPinMid = Color(0xFFD93025);
  static const Color onboardingPinDeep = Color(0xFF9B1C14);

  /// White copy on the slate hero header.
  static const Color authOnSlate = Color(0xFFFFFFFF);
  static const Color authOnSlateMuted = Color(0xD9FFFFFF); // 85%

  /// Translucent glass pill used for the "Back to login" action.
  static const Color authGlassFill = Color(0x26FFFFFF); // 15%
  static const Color authGlassBorder = Color(0x66FFFFFF); // 40%

  /// Slate tints for rings, dividers, badges and secondary copy.
  static const Color authSlateTint = Color(0x1A4D738F); // 10%
  static const Color authSlateRing = Color(0x264D738F); // 15%
  static const Color authSlateDivider = Color(0x334D738F); // 20%
  static const Color authSlateHint = Color(0x8C4D738F); // 55%
  static const Color authSlate80 = Color(0xCC4D738F); // 80%
  static const Color authSlate85 = Color(0xD94D738F); // 85%

  /// Reference shadows for pill fields, the sheet and the ember CTA.
  static const Color authFieldShadow = Color(0x8C4D738F); // 55%
  static const Color authFieldShadowSoft = Color(0x244D738F); // 14%
  static const Color authSheetShadow = Color(0x731E2A33); // 45%
  static const Color authCtaShadow = Color(0xB3B5583A); // 70%

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
    colors: <Color>[Color(0x1AFFFFFF), Color(0x00FFFFFF), Color(0x00FFFFFF)],
    stops: <double>[0.0, 0.45, 1.0],
  );

  static const RadialGradient headerGlowGradient = RadialGradient(
    center: Alignment(0.8, -1.2),
    radius: 4.5,
    colors: <Color>[Color(0x4D4D738F), Color(0x004D738F)],
    stops: <double>[0.0, 0.55],
  );
}
