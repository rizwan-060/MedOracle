import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Tracks which accordion section of an intake step is currently open.
///
/// The design reference shows exactly one section expanded at a time, so this
/// controller stores a single id rather than a set.
///
/// Riverpod builds the notifier through the unnamed constructor, so the
/// starting section is supplied by a screen-scoped subclass
/// ([sectionAccordionProvider] is overridden per screen):
///
/// ```dart
/// class _DetailsFirst extends SectionAccordionController {
///   _DetailsFirst() : super(initialSection: 'details');
/// }
/// ```
class SectionAccordionController extends Notifier<String> {
  SectionAccordionController({required this.initialSection});

  /// Section opened when the step is first shown.
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
