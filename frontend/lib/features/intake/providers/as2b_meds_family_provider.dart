import 'package:flutter_riverpod/flutter_riverpod.dart';

enum As2bHistoryTab { family, medication }

/// Immutable state for the AS2B medications and family-history reference screen.
class As2bMedsFamilyState {
  const As2bMedsFamilyState({
    this.medications = const <String>[
      'Amlodipine (5mg, Once Daily)',
      'Metformin (500mg, Twice Daily)',
      'Atorvastatin (20mg, At Night)',
    ],
    this.family = const <String>[
      'Father (Heart Attack, 52 yrs)',
      'Mother (Type 2 Diabetes, 61 yrs)',
    ],
    this.medicationsExpanded = false,
    this.familyExpanded = false,
    this.drawerOpen = true,
    this.activeTab = As2bHistoryTab.family,
    this.relative = 'Father',
    this.age = 52,
    this.condition = 'Myocardial infarction',
    this.medicine = '',
    this.frequency = 'Once Daily',
    this.dose = 5,
  });

  final List<String> medications;
  final List<String> family;
  final bool medicationsExpanded;
  final bool familyExpanded;
  final bool drawerOpen;
  final As2bHistoryTab activeTab;
  final String relative;
  final int age;
  final String condition;
  final String medicine;
  final String frequency;
  final int dose;

  As2bMedsFamilyState copyWith({
    List<String>? medications,
    List<String>? family,
    bool? medicationsExpanded,
    bool? familyExpanded,
    bool? drawerOpen,
    As2bHistoryTab? activeTab,
    String? relative,
    int? age,
    String? condition,
    String? medicine,
    String? frequency,
    int? dose,
  }) {
    return As2bMedsFamilyState(
      medications: medications ?? this.medications,
      family: family ?? this.family,
      medicationsExpanded: medicationsExpanded ?? this.medicationsExpanded,
      familyExpanded: familyExpanded ?? this.familyExpanded,
      drawerOpen: drawerOpen ?? this.drawerOpen,
      activeTab: activeTab ?? this.activeTab,
      relative: relative ?? this.relative,
      age: age ?? this.age,
      condition: condition ?? this.condition,
      medicine: medicine ?? this.medicine,
      frequency: frequency ?? this.frequency,
      dose: dose ?? this.dose,
    );
  }
}

class As2bMedsFamilyController extends Notifier<As2bMedsFamilyState> {
  @override
  As2bMedsFamilyState build() => const As2bMedsFamilyState();

  void toggleMedicationsExpanded() => state = state.copyWith(
        medicationsExpanded: !state.medicationsExpanded,
      );

  void toggleFamilyExpanded() => state = state.copyWith(
        familyExpanded: !state.familyExpanded,
      );

  void toggleDrawer() => state = state.copyWith(drawerOpen: !state.drawerOpen);

  void setTab(As2bHistoryTab tab) => state = state.copyWith(activeTab: tab);

  void setRelative(String value) => state = state.copyWith(relative: value);

  void setAge(int value) => state = state.copyWith(
        age: value < 0 ? 0 : (value > 120 ? 120 : value),
      );

  void setCondition(String value) => state = state.copyWith(condition: value);

  void setMedicine(String value) => state = state.copyWith(medicine: value);

  void setFrequency(String value) => state = state.copyWith(frequency: value);

  void setDose(int value) => state = state.copyWith(
        dose: value < 5 ? 5 : (value > 2000 ? 2000 : value),
      );

  void removeMedication(int index) {
    final List<String> updated = List<String>.from(state.medications)
      ..removeAt(index);
    state = state.copyWith(medications: updated);
  }

  void removeFamily(int index) {
    final List<String> updated = List<String>.from(state.family)..removeAt(index);
    state = state.copyWith(family: updated);
  }

  void saveRecord() {
    if (state.activeTab == As2bHistoryTab.family) {
      final String condition = state.condition.trim();
      if (condition.isEmpty) return;
      final String record = '${state.relative} ($condition, ${state.age} yrs)';
      state = state.copyWith(family: <String>[...state.family, record]);
      return;
    }

    final String name = state.medicine.trim();
    if (name.isEmpty) return;
    final String record = '$name (${state.dose}mg, ${state.frequency})';
    state = state.copyWith(medications: <String>[...state.medications, record]);
  }
}

final as2bMedsFamilyProvider =
    NotifierProvider<As2bMedsFamilyController, As2bMedsFamilyState>(
  As2bMedsFamilyController.new,
);
