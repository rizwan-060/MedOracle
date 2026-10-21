import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../data/models/medical_history_model.dart';
import '../../../data/providers/repository_providers.dart';
import 'medications_family_provider.dart';

/// Immutable form state for the "Clinical Status" wizard step.
class ClinicalStatusState {
  const ClinicalStatusState({
    this.conditions = const ['Hypertension', 'Dyslipidemia'],
    this.surgeries = const ['Appendectomy'],
    this.allergies = const ['Penicillin'],
    this.conditionQuery = '',
    this.notes = '',
    this.isLoading = false,
  });

  final List<String> conditions;
  final List<String> surgeries;
  final List<String> allergies;

  /// Live text inside the "Chronic Conditions" typeahead field.
  final String conditionQuery;

  final String notes;
  final bool isLoading;

  ClinicalStatusState copyWith({
    List<String>? conditions,
    List<String>? surgeries,
    List<String>? allergies,
    String? conditionQuery,
    String? notes,
    bool? isLoading,
  }) {
    return ClinicalStatusState(
      conditions: conditions ?? this.conditions,
      surgeries: surgeries ?? this.surgeries,
      allergies: allergies ?? this.allergies,
      conditionQuery: conditionQuery ?? this.conditionQuery,
      notes: notes ?? this.notes,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class ClinicalStatusController extends Notifier<ClinicalStatusState> {
  @override
  ClinicalStatusState build() {
    Future<void>.microtask(_load);
    return const ClinicalStatusState();
  }

  Future<void> _load() async {
    try {
      final MedicalHistoryModel history = await ref
          .read(medicalHistoryRepositoryProvider)
          .fetchMedicalHistory();
      if (history.chronicConditions.isNotEmpty ||
          history.pastSurgeries.isNotEmpty ||
          history.allergies.isNotEmpty ||
          (history.notes != null && history.notes!.isNotEmpty)) {
        state = state.copyWith(
          conditions: history.chronicConditions.isNotEmpty
              ? history.chronicConditions
              : state.conditions,
          surgeries: history.pastSurgeries.isNotEmpty
              ? history.pastSurgeries
              : state.surgeries,
          allergies: history.allergies.isNotEmpty
              ? history.allergies
              : state.allergies,
          notes: history.notes ?? state.notes,
        );
      }
    } catch (_) {
      // Retain seeded defaults on network error
    }
  }

  Future<void> save() async {
    try {
      final MedicationsFamilyState medsState =
          ref.read(medicationsFamilyProvider);
      final MedicalHistoryModel model = MedicalHistoryModel(
        chronicConditions: state.conditions,
        pastSurgeries: state.surgeries,
        allergies: state.allergies,
        notes: state.notes,
        currentMedications: medsState.medications
            .map((m) => <String, dynamic>{
                  'name': m.name,
                  'dosage': m.dosage,
                  'frequency': m.frequency,
                })
            .toList(),
        familyHistory: medsState.familyRecords
            .map((f) => <String, dynamic>{
                  'relative': f.relative,
                  'age_at_onset': int.tryParse(f.ageAtDiagnosis) ?? 50,
                  'condition': f.condition,
                })
            .toList(),
      );
      await ref
          .read(medicalHistoryRepositoryProvider)
          .saveMedicalHistory(model);
    } catch (_) {
      // Retain state on network error
    }
  }

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
    save();
  }

  void removeCondition(String condition) {
    state = state.copyWith(
      conditions: state.conditions.where((c) => c != condition).toList(),
    );
    save();
  }

  void addSurgery(String name) {
    if (name.isEmpty || state.surgeries.contains(name)) return;
    state = state.copyWith(surgeries: [...state.surgeries, name]);
    save();
  }

  void removeSurgery(String surgery) {
    state = state.copyWith(
      surgeries: state.surgeries.where((s) => s != surgery).toList(),
    );
    save();
  }

  void addAllergy(String name) {
    if (name.isEmpty || state.allergies.contains(name)) return;
    state = state.copyWith(allergies: [...state.allergies, name]);
    save();
  }

  void removeAllergy(String allergy) {
    state = state.copyWith(
      allergies: state.allergies.where((a) => a != allergy).toList(),
    );
    save();
  }

  void setNotes(String value) {
    state = state.copyWith(notes: value);
    save();
  }
}

final NotifierProvider<ClinicalStatusController, ClinicalStatusState>
    clinicalStatusProvider =
    NotifierProvider<ClinicalStatusController, ClinicalStatusState>(
  ClinicalStatusController.new,
);
