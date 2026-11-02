import 'package:flutter_riverpod/flutter_riverpod.dart';

/// The four collapsible sections of the Labs & Vitals step.
enum LabsSection {
  generalVitals('General Vitals'),
  lipidPanel('Lipid Panel'),
  glycemicRenal('Glycemic & Renal'),
  labDetails('Lab Details');

  const LabsSection(this.title);

  final String title;
}

/// Immutable form state for the "Labs & Vitals" wizard step.
class LabsVitalsState {
  const LabsVitalsState({
    this.heightCm = '170',
    this.weightKg = '72',
    this.waistCm = '88',
    this.systolicBp = '146',
    this.diastolicBp = '92',
    this.totalCholesterol = '242',
    this.hdl = '37',
    this.ldl = '160',
    this.hba1c = '6.2',
    this.fastingGlucose = '118',
    this.creatinine = '1.12',
    this.testDate = '12 Oct 2026',
    this.labName = 'City Diagnostics',
    this.pathologistNotes = '',
    this.openSection = LabsSection.generalVitals,
  });

  // General Vitals
  final String heightCm;
  final String weightKg;
  final String waistCm;
  final String systolicBp;
  final String diastolicBp;

  // Lipid Panel
  final String totalCholesterol;
  final String hdl;
  final String ldl;

  // Glycemic & Renal
  final String hba1c;
  final String fastingGlucose;
  final String creatinine;

  // Lab Details
  final String testDate;
  final String labName;
  final String pathologistNotes;

  /// Accordion state — only one section open at a time.
  final LabsSection? openSection;

  LabsVitalsState copyWith({
    String? heightCm,
    String? weightKg,
    String? waistCm,
    String? systolicBp,
    String? diastolicBp,
    String? totalCholesterol,
    String? hdl,
    String? ldl,
    String? hba1c,
    String? fastingGlucose,
    String? creatinine,
    String? testDate,
    String? labName,
    String? pathologistNotes,
    LabsSection? openSection,
    bool clearOpenSection = false,
  }) {
    return LabsVitalsState(
      heightCm: heightCm ?? this.heightCm,
      weightKg: weightKg ?? this.weightKg,
      waistCm: waistCm ?? this.waistCm,
      systolicBp: systolicBp ?? this.systolicBp,
      diastolicBp: diastolicBp ?? this.diastolicBp,
      totalCholesterol: totalCholesterol ?? this.totalCholesterol,
      hdl: hdl ?? this.hdl,
      ldl: ldl ?? this.ldl,
      hba1c: hba1c ?? this.hba1c,
      fastingGlucose: fastingGlucose ?? this.fastingGlucose,
      creatinine: creatinine ?? this.creatinine,
      testDate: testDate ?? this.testDate,
      labName: labName ?? this.labName,
      pathologistNotes: pathologistNotes ?? this.pathologistNotes,
      openSection: clearOpenSection
          ? null
          : (openSection ?? this.openSection),
    );
  }
}

class LabsVitalsController extends Notifier<LabsVitalsState> {
  @override
  LabsVitalsState build() => const LabsVitalsState();

  /// Toggles the accordion: tapping the open section closes it, tapping a
  /// closed one opens it exclusively.
  void toggleSection(LabsSection section) {
    state = state.copyWith(
      clearOpenSection: state.openSection == section,
      openSection: state.openSection == section ? null : section,
    );
  }

  void setHeight(String value) => state = state.copyWith(heightCm: value);
  void setWeight(String value) => state = state.copyWith(weightKg: value);
  void setWaist(String value) => state = state.copyWith(waistCm: value);
  void setSystolicBp(String value) => state = state.copyWith(systolicBp: value);
  void setDiastolicBp(String value) =>
      state = state.copyWith(diastolicBp: value);

  void setTotalCholesterol(String value) =>
      state = state.copyWith(totalCholesterol: value);
  void setHdl(String value) => state = state.copyWith(hdl: value);
  void setLdl(String value) => state = state.copyWith(ldl: value);

  void setHba1c(String value) => state = state.copyWith(hba1c: value);
  void setFastingGlucose(String value) =>
      state = state.copyWith(fastingGlucose: value);
  void setCreatinine(String value) => state = state.copyWith(creatinine: value);

  void setTestDate(String value) => state = state.copyWith(testDate: value);
  void setLabName(String value) => state = state.copyWith(labName: value);
  void setPathologistNotes(String value) =>
      state = state.copyWith(pathologistNotes: value);
}

final labsVitalsProvider =
    NotifierProvider<LabsVitalsController, LabsVitalsState>(
  LabsVitalsController.new,
);
