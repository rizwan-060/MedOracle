import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/misc.dart';

import 'section_accordion_controller.dart';

/// Accordion state for the step currently on screen.
///
/// Riverpod instantiates notifiers through the unnamed constructor, so every
/// intake screen overrides this provider in a local [ProviderScope] with a
/// small subclass that passes its own starting section:
///
/// ```dart
/// class _DetailsFirstAccordion extends SectionAccordionController {
///   _DetailsFirstAccordion() : super(initialSection: 'details');
/// }
///
/// ProviderScope(
///   overrides: <Override>[
///     sectionAccordionProvider.overrideWith(_DetailsFirstAccordion.new),
///   ],
///   child: const ProfileScreen(),
/// )
/// ```
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
