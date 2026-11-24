import 'package:google_fonts/google_fonts.dart';
import 'package:material_ui/material_ui.dart';

/// Typography helpers for the onboarding references.
///
/// Headlines use Newsreader; labels and body copy use Lexend.
abstract final class OnboardingType {
  static TextStyle sans(
    double size,
    FontWeight weight,
    Color color, {
    double? height,
    double? spacing,
  }) =>
      GoogleFonts.lexend(
        fontSize: size,
        fontWeight: weight,
        color: color,
        height: height,
        letterSpacing: spacing,
      );

  static TextStyle serif(
    double size,
    FontWeight weight,
    Color color, {
    double? height,
  }) =>
      GoogleFonts.newsreader(
        fontSize: size,
        fontWeight: weight,
        color: color,
        height: height,
      );
}
