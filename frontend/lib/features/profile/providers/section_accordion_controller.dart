import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Tracks which accordion section of a screen is currently open.
///
/// Stores a single id rather than a set so exactly one section is expanded.
class SectionAccordionController extends Notifier<String> {
  SectionAccordionController({required this.initialSection});

  /// Section opened when first shown.
  final String initialSection;

  @override
  String build() => initialSection;

  /// Opens [id], closing whichever section was open before.
  void open(String id) => state = id;

  /// Collapses the section when it is already open, otherwise opens it.
  void toggle(String id) {
    if (state == id) {
      state = '';
    } else {
      state = id;
    }
  }
}
