import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Immutable form state for the "Clinical Status" wizard step.
class ClinicalStatusState {
  const ClinicalStatusState({
    this.conditions = const ['Hypertension', 'Dyslipidemia'],
    this.surgeries = const ['Appendectomy'],
    this.allergies = const ['Penicillin'],
    this.conditionQuery = '',
    this.notes = '',
  });

  final List<String> conditions;
  final List<String> surgeries;
  final List<String> allergies;

  /// Live text inside the "Chronic Conditions" typeahead field.
  final String conditionQuery;

  final String notes;

  ClinicalStatusState copyWith({
    List<String>? conditions,
    List<String>? surgeries,
    List<String>? allergies,
    String? conditionQuery,
    String? notes,
  }) {
    return ClinicalStatusState(
      conditions: conditions ?? this.conditions,
      surgeries: surgeries ?? this.surgeries,
      allergies: allergies ?? this.allergies,
      conditionQuery: conditionQuery ?? this.conditionQuery,
      notes: notes ?? this.notes,
    );
  }
}

class ClinicalStatusController extends Notifier<ClinicalStatusState> {
  @override
  ClinicalStatusState build() => const ClinicalStatusState();

  void setConditionQuery(String value) {
    state = state.copyWith(conditionQuery: value);
  }

  /// Commits the typed query (or an explicit [name]) as a new condition chip.
  void addCondition([String? name]) {
    final String candidate = (name ?? state.conditionQuery).trim();
    if (candidate.isEmpty || state.conditions.contains(candidate)) return;
    state = state.copyWith(
      conditions: [...state.conditions, candidate],
      conditionQuery: '',
    );
  }

  void removeCondition(String condition) {
    state = state.copyWith(
      conditions: state.conditions.where((c) => c != condition).toList(),
    );
  }

  void addSurgery(String name) {
    if (name.isEmpty || state.surgeries.contains(name)) return;
    state = state.copyWith(surgeries: [...state.surgeries, name]);
  }

  void removeSurgery(String surgery) {
    state = state.copyWith(
      surgeries: state.surgeries.where((s) => s != surgery).toList(),
    );
  }

  void addAllergy(String name) {
    if (name.isEmpty || state.allergies.contains(name)) return;
    state = state.copyWith(allergies: [...state.allergies, name]);
  }

  void removeAllergy(String allergy) {
    state = state.copyWith(
      allergies: state.allergies.where((a) => a != allergy).toList(),
    );
  }

  void setNotes(String value) {
    state = state.copyWith(notes: value);
  }
}

final clinicalStatusProvider =
    NotifierProvider<ClinicalStatusController, ClinicalStatusState>(
  ClinicalStatusController.new,
);
