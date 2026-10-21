import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../data/models/medical_history_model.dart';
import '../../../data/providers/repository_providers.dart';
import 'clinical_status_provider.dart';

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
    this.medications = const [
      MedicationEntry(
        name: 'Amlodipine',
        dosage: '5mg',
        frequency: 'Once Daily',
      ),
      MedicationEntry(
        name: 'Atorvastatin',
        dosage: '20mg',
        frequency: 'At bedtime',
      ),
    ],
    this.familyRecords = const [
      FamilyHistoryRecord(
        relative: 'Father',
        ageAtDiagnosis: '55',
        condition: 'Myocardial infarction',
      ),
      FamilyHistoryRecord(
        relative: 'Mother',
        ageAtDiagnosis: '62',
        condition: 'Type 2 Diabetes',
      ),
    ],
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
  MedicationsFamilyState build() {
    Future<void>.microtask(_load);
    return const MedicationsFamilyState();
  }

  Future<void> _load() async {
    try {
      final MedicalHistoryModel history = await ref
          .read(medicalHistoryRepositoryProvider)
          .fetchMedicalHistory();
      if (history.currentMedications.isNotEmpty ||
          history.familyHistory.isNotEmpty) {
        final List<MedicationEntry> meds = history.currentMedications
            .map((m) => MedicationEntry(
                  name: m['name']?.toString() ?? '',
                  dosage: m['dosage']?.toString() ?? '',
                  frequency: m['frequency']?.toString() ?? '',
                ))
            .where((m) => m.name.isNotEmpty)
            .toList();

        final List<FamilyHistoryRecord> family = history.familyHistory
            .map((f) => FamilyHistoryRecord(
                  relative: f['relative']?.toString() ?? '',
                  ageAtDiagnosis: f['age_at_onset']?.toString() ?? '',
                  condition: f['condition']?.toString() ?? '',
                ))
            .where((f) => f.relative.isNotEmpty)
            .toList();

        state = state.copyWith(
          medications: meds.isNotEmpty ? meds : state.medications,
          familyRecords: family.isNotEmpty ? family : state.familyRecords,
        );
      }
    } catch (_) {
      // Retain seeded defaults on network error
    }
  }

  Future<void> save() async {
    try {
      final ClinicalStatusState clinical = ref.read(clinicalStatusProvider);
      final MedicalHistoryModel model = MedicalHistoryModel(
        chronicConditions: clinical.conditions,
        pastSurgeries: clinical.surgeries,
        allergies: clinical.allergies,
        notes: clinical.notes,
        currentMedications: state.medications
            .map((m) => <String, dynamic>{
                  'name': m.name,
                  'dosage': m.dosage,
                  'frequency': m.frequency,
                })
            .toList(),
        familyHistory: state.familyRecords
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

  void setMedNameDraft(String value) =>
      state = state.copyWith(medNameDraft: value);

  void setDosageDraft(String value) =>
      state = state.copyWith(dosageDraft: value);

  void setFrequencyDraft(String value) =>
      state = state.copyWith(frequencyDraft: value);

  /// Commits the medication draft and clears draft fields.
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
    save();
  }

  void removeMedication(String label) {
    state = state.copyWith(
      medications: state.medications.where((m) => m.label != label).toList(),
    );
    save();
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
    save();
  }

  void removeFamilyRecord(String label) {
    state = state.copyWith(
      familyRecords:
          state.familyRecords.where((r) => r.label != label).toList(),
    );
    save();
  }
}

final NotifierProvider<MedicationsFamilyController, MedicationsFamilyState>
    medicationsFamilyProvider =
    NotifierProvider<MedicationsFamilyController, MedicationsFamilyState>(
  MedicationsFamilyController.new,
);
