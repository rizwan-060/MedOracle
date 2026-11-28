import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Visual phase of the Step 2A clinical-status screen.
enum ClinicalStatusPhase { empty, adding, done }

/// Immutable form state for the "Clinical Status" wizard step.
class ClinicalStatusState {
  const ClinicalStatusState({
    this.phase = ClinicalStatusPhase.empty,
    this.conditions = const <String>[],
    this.surgeries = const <String>[],
    this.allergies = const <String>[],
    this.conditionQuery = '',
    this.notes = '',
  });

  final ClinicalStatusPhase phase;
  final List<String> conditions;
  final List<String> surgeries;
  final List<String> allergies;

  /// Live text inside the "Search or add conditions..." field.
  final String conditionQuery;

  final String notes;

  ClinicalStatusState copyWith({
    ClinicalStatusPhase? phase,
    List<String>? conditions,
    List<String>? surgeries,
    List<String>? allergies,
    String? conditionQuery,
    String? notes,
  }) {
    return ClinicalStatusState(
      phase: phase ?? this.phase,
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
      phase: ClinicalStatusPhase.adding,
      conditions: [...state.conditions, candidate],
      conditionQuery: '',
    );
  }

  void removeCondition(String condition) {
    final List<String> remaining =
        state.conditions.where((c) => c != condition).toList();
    state = state.copyWith(
      phase: remaining.isEmpty
          ? ClinicalStatusPhase.empty
          : ClinicalStatusPhase.adding,
      conditions: remaining,
    );
  }

  /// Moves the screen from "adding" to the "conditions added" summary.
  void completeAdding() {
    state = state.copyWith(phase: ClinicalStatusPhase.done);
  }

  /// Returns from the summary to the editable "adding" state.
  void editConditions() {
    state = state.copyWith(phase: ClinicalStatusPhase.adding);
  }

  /// Completes the flow with zero conditions ("I don't have any").
  void clearConditions() {
    state = state.copyWith(
      phase: ClinicalStatusPhase.done,
      conditions: const <String>[],
      conditionQuery: '',
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
