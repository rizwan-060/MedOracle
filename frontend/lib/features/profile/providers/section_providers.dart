import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/misc.dart';

import 'section_accordion_controller.dart';

/// Accordion state for the section currently on screen.
final NotifierProvider<SectionAccordionController, String>
    sectionAccordionProvider =
    NotifierProvider<SectionAccordionController, String>(
  () => throw UnimplementedError(
    'sectionAccordionProvider must be overridden by the active screen. '
    'See ${#sectionAccordionProvider} docs for the override pattern.',
  ),
);

/// Alias so screens can annotate their override lists without importing
/// `flutter_riverpod/misc.dart` themselves.
typedef AccordionOverride = Override;
