import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../data/models/symptom_model.dart';
import '../../../data/providers/repository_providers.dart';

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
    this.durationValue = '3',
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
  SymptomsState build() {
    Future<void>.microtask(_load);
    return const SymptomsState();
  }

  Future<void> _load() async {
    try {
      final List<SymptomReportModel> reports =
          await ref.read(symptomsRepositoryProvider).fetchSymptoms();
      if (reports.isNotEmpty) {
        final SymptomReportModel latest = reports.first;
        state = state.copyWith(
          symptoms: latest.structuredSymptoms.isNotEmpty
              ? latest.structuredSymptoms
              : state.symptoms,
          bodyLocations: latest.bodyLocations.isNotEmpty
              ? latest.bodyLocations
              : state.bodyLocations,
          triggers: latest.triggers.isNotEmpty
              ? latest.triggers
              : state.triggers,
          severity: latest.severitySelfRating ?? state.severity,
          durationValue: latest.durationDays != null
              ? latest.durationDays.toString()
              : state.durationValue,
          notes: latest.reportedText.isNotEmpty
              ? latest.reportedText
              : state.notes,
        );
      }
    } catch (_) {
      // Retain defaults on network error
    }
  }

  Future<void> save() async {
    try {
      final SymptomReportModel model = SymptomReportModel(
        reportedText: state.notes.isNotEmpty
            ? state.notes
            : (state.symptoms.isNotEmpty
                ? state.symptoms.join(', ')
                : 'Intake reported symptoms'),
        severitySelfRating: state.severity,
        durationDays: int.tryParse(state.durationValue) ?? 3,
        bodyLocations: state.bodyLocations,
        triggers: state.triggers,
        structuredSymptoms: state.symptoms,
      );
      await ref.read(symptomsRepositoryProvider).submitSymptoms(model);
    } catch (_) {
      // Retain state on network error
    }
  }

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
    save();
  }

  void removeSymptom(String symptom) {
    state = state.copyWith(
      symptoms: state.symptoms.where((s) => s != symptom).toList(),
    );
    save();
  }

  void addBodyLocation(String name) {
    final String candidate = name.trim();
    if (candidate.isEmpty || state.bodyLocations.contains(candidate)) return;
    state = state.copyWith(bodyLocations: [...state.bodyLocations, candidate]);
    save();
  }

  void removeBodyLocation(String location) {
    state = state.copyWith(
      bodyLocations: state.bodyLocations.where((l) => l != location).toList(),
    );
    save();
  }

  void addTrigger(String name) {
    final String candidate = name.trim();
    if (candidate.isEmpty || state.triggers.contains(candidate)) return;
    state = state.copyWith(triggers: [...state.triggers, candidate]);
    save();
  }

  void removeTrigger(String trigger) {
    state = state.copyWith(
      triggers: state.triggers.where((t) => t != trigger).toList(),
    );
    save();
  }

  void setSeverity(int value) {
    state = state.copyWith(severity: value.clamp(1, 10));
    save();
  }

  void setDurationValue(String value) {
    state = state.copyWith(durationValue: value);
    save();
  }

  void setNotes(String value) {
    state = state.copyWith(notes: value);
    save();
  }
}

final NotifierProvider<SymptomsController, SymptomsState> symptomsProvider =
    NotifierProvider<SymptomsController, SymptomsState>(SymptomsController.new);
