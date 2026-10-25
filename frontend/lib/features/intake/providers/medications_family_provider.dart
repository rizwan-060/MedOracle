import 'package:flutter_riverpod/flutter_riverpod.dart';

/// A single committed medication entry.
class MedicationEntry {
  const MedicationEntry({
    required this.name,
    required this.dosage,
    required this.frequency,
  });

  final String name;
  final String dosage;
  final String frequency;

  String get label => '$name · $dosage · $frequency';
}

/// A single committed family-history record.
class FamilyHistoryRecord {
  const FamilyHistoryRecord({
    required this.relative,
    required this.ageAtDiagnosis,
    required this.condition,
  });

  final String relative;
  final String ageAtDiagnosis;
  final String condition;

  String get label => '$relative · age $ageAtDiagnosis · $condition';
}

/// Immutable form state for the "Medications & Family" wizard step.
class MedicationsFamilyState {
  const MedicationsFamilyState({
    this.medications = const [],
    this.familyRecords = const [],
    this.medNameDraft = '',
    this.dosageDraft = '',
    this.frequencyDraft = '',
    this.relativeDraft = '',
    this.ageDraft = '',
    this.conditionDraft = '',
    this.familyExpanded = true,
  });

  final List<MedicationEntry> medications;
  final List<FamilyHistoryRecord> familyRecords;

  /// Draft values for the "Current Medications" form.
  final String medNameDraft;
  final String dosageDraft;
  final String frequencyDraft;

  /// Draft values for the "Family History" form.
  final String relativeDraft;
  final String ageDraft;
  final String conditionDraft;

  /// Accordion state of the Family History card.
  final bool familyExpanded;

  bool get canAddMedication =>
      medNameDraft.trim().isNotEmpty &&
      dosageDraft.trim().isNotEmpty &&
      frequencyDraft.trim().isNotEmpty;

  bool get canAddFamilyRecord =>
      relativeDraft.trim().isNotEmpty &&
      ageDraft.trim().isNotEmpty &&
      conditionDraft.trim().isNotEmpty;

  MedicationsFamilyState copyWith({
    List<MedicationEntry>? medications,
    List<FamilyHistoryRecord>? familyRecords,
    String? medNameDraft,
    String? dosageDraft,
    String? frequencyDraft,
    String? relativeDraft,
    String? ageDraft,
    String? conditionDraft,
    bool? familyExpanded,
  }) {
    return MedicationsFamilyState(
      medications: medications ?? this.medications,
      familyRecords: familyRecords ?? this.familyRecords,
      medNameDraft: medNameDraft ?? this.medNameDraft,
      dosageDraft: dosageDraft ?? this.dosageDraft,
      frequencyDraft: frequencyDraft ?? this.frequencyDraft,
      relativeDraft: relativeDraft ?? this.relativeDraft,
      ageDraft: ageDraft ?? this.ageDraft,
      conditionDraft: conditionDraft ?? this.conditionDraft,
      familyExpanded: familyExpanded ?? this.familyExpanded,
    );
  }
}

class MedicationsFamilyController extends Notifier<MedicationsFamilyState> {
  @override
  MedicationsFamilyState build() => const MedicationsFamilyState();

  void setMedNameDraft(String value) =>
      state = state.copyWith(medNameDraft: value);

  void setDosageDraft(String value) =>
      state = state.copyWith(dosageDraft: value);

  void setFrequencyDraft(String value) =>
      state = state.copyWith(frequencyDraft: value);

  /// Commits the medication draft (or an explicit entry) and clears the
  /// draft fields.
  void addMedication() {
    if (!state.canAddMedication) return;
    state = state.copyWith(
      medications: [
        ...state.medications,
        MedicationEntry(
          name: state.medNameDraft.trim(),
          dosage: state.dosageDraft.trim(),
          frequency: state.frequencyDraft.trim(),
        ),
      ],
      medNameDraft: '',
      dosageDraft: '',
      frequencyDraft: '',
    );
  }

  void removeMedication(String label) {
    state = state.copyWith(
      medications: state.medications.where((m) => m.label != label).toList(),
    );
  }

  void toggleFamilyExpanded() {
    state = state.copyWith(familyExpanded: !state.familyExpanded);
  }

  void setRelativeDraft(String value) =>
      state = state.copyWith(relativeDraft: value);

  void setAgeDraft(String value) => state = state.copyWith(ageDraft: value);

  void setConditionDraft(String value) =>
      state = state.copyWith(conditionDraft: value);

  void addFamilyRecord() {
    if (!state.canAddFamilyRecord) return;
    state = state.copyWith(
      familyRecords: [
        ...state.familyRecords,
        FamilyHistoryRecord(
          relative: state.relativeDraft.trim(),
          ageAtDiagnosis: state.ageDraft.trim(),
          condition: state.conditionDraft.trim(),
        ),
      ],
      relativeDraft: '',
      ageDraft: '',
      conditionDraft: '',
    );
  }

  void removeFamilyRecord(String label) {
    state = state.copyWith(
      familyRecords:
          state.familyRecords.where((r) => r.label != label).toList(),
    );
  }
}

final medicationsFamilyProvider =
    NotifierProvider<MedicationsFamilyController, MedicationsFamilyState>(
  MedicationsFamilyController.new,
);
