import 'package:google_fonts/google_fonts.dart';
import 'package:material_ui/material_ui.dart';

/// Typography used by the assessment intake reference screens.
abstract final class AssessmentType {
  static const TextHeightBehavior compactHeight = TextHeightBehavior(
    applyHeightToFirstAscent: false,
    applyHeightToLastDescent: false,
  );

  static StrutStyle strut(double size, double height) => StrutStyle(
        fontSize: size,
        height: height,
        forceStrutHeight: true,
      );

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

  static TextStyle jakarta(
    double size,
    FontWeight weight,
    Color color, {
    double? height,
    double? spacing,
  }) =>
      TextStyle(
        fontFamily: 'Plus Jakarta Sans',
        fontSize: size,
        fontWeight: weight,
        color: color,
        height: height,
        letterSpacing: spacing,
      );
}
