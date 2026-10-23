import 'package:flutter_riverpod/flutter_riverpod.dart';

/// The six collapsible sections of the Symptoms step.
enum SymptomsSection {
  symptoms('Symptoms'),
  bodyLocation('Body Location'),
  triggers('Triggers'),
  severityRating('Severity Rating'),
  duration('Duration'),
  contextualNotes('Contextual Notes');

  const SymptomsSection(this.title);

  final String title;
}

/// Immutable form state for the "Symptoms" wizard step.
class SymptomsState {
  const SymptomsState({
    this.symptoms = const ['Chest Pain', 'Shortness of Breath'],
    this.bodyLocations = const ['Chest'],
    this.triggers = const ['Physical Exertion'],
    this.severity = 7,
    this.durationValue = '',
    this.notes =
        'Chest tightness when climbing stairs, easing after a few minutes of rest.',
    this.openSection = SymptomsSection.symptoms,
  });

  final List<String> symptoms;
  final List<String> bodyLocations;
  final List<String> triggers;

  /// 1–10 severity rating.
  final int severity;

  /// Duration amount in days (free text, e.g. "3").
  final String durationValue;

  final String notes;

  /// Accordion state — only one section open at a time.
  final SymptomsSection? openSection;

  SymptomsState copyWith({
    List<String>? symptoms,
    List<String>? bodyLocations,
    List<String>? triggers,
    int? severity,
    String? durationValue,
    String? notes,
    SymptomsSection? openSection,
    bool clearOpenSection = false,
  }) {
    return SymptomsState(
      symptoms: symptoms ?? this.symptoms,
      bodyLocations: bodyLocations ?? this.bodyLocations,
      triggers: triggers ?? this.triggers,
      severity: severity ?? this.severity,
      durationValue: durationValue ?? this.durationValue,
      notes: notes ?? this.notes,
      openSection: clearOpenSection
          ? null
          : (openSection ?? this.openSection),
    );
  }
}

class SymptomsController extends Notifier<SymptomsState> {
  @override
  SymptomsState build() => const SymptomsState();

  /// Toggles the accordion: tapping the open section closes it, tapping a
  /// closed one opens it exclusively.
  void toggleSection(SymptomsSection section) {
    state = state.copyWith(
      clearOpenSection: state.openSection == section,
      openSection: state.openSection == section ? null : section,
    );
  }

  void addSymptom(String name) {
    final String candidate = name.trim();
    if (candidate.isEmpty || state.symptoms.contains(candidate)) return;
    state = state.copyWith(symptoms: [...state.symptoms, candidate]);
  }

  void removeSymptom(String symptom) {
    state = state.copyWith(
      symptoms: state.symptoms.where((s) => s != symptom).toList(),
    );
  }

  void addBodyLocation(String name) {
    final String candidate = name.trim();
    if (candidate.isEmpty || state.bodyLocations.contains(candidate)) return;
    state = state.copyWith(bodyLocations: [...state.bodyLocations, candidate]);
  }

  void removeBodyLocation(String location) {
    state = state.copyWith(
      bodyLocations: state.bodyLocations.where((l) => l != location).toList(),
    );
  }

  void addTrigger(String name) {
    final String candidate = name.trim();
    if (candidate.isEmpty || state.triggers.contains(candidate)) return;
    state = state.copyWith(triggers: [...state.triggers, candidate]);
  }

  void removeTrigger(String trigger) {
    state = state.copyWith(
      triggers: state.triggers.where((t) => t != trigger).toList(),
    );
  }

  void setSeverity(int value) {
    state = state.copyWith(severity: value.clamp(1, 10));
  }

  void setDurationValue(String value) {
    state = state.copyWith(durationValue: value);
  }

  void setNotes(String value) {
    state = state.copyWith(notes: value);
  }
}

final symptomsProvider =
    NotifierProvider<SymptomsController, SymptomsState>(SymptomsController.new);
