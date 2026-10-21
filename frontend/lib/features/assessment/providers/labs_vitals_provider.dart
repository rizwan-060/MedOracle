import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../data/models/lab_result_model.dart';
import '../../../data/providers/repository_providers.dart';

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
    this.testDate = '2026-10-12',
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
  LabsVitalsState build() {
    Future<void>.microtask(_load);
    return const LabsVitalsState();
  }

  Future<void> _load() async {
    try {
      final LabResultModel? lab =
          await ref.read(laboratoryRepositoryProvider).fetchLatestLabResult();
      if (lab != null) {
        final Map<String, dynamic> b = lab.biomarkers;
        state = state.copyWith(
          testDate: lab.testDate,
          labName: lab.labName ?? state.labName,
          pathologistNotes: lab.notes ?? state.pathologistNotes,
          systolicBp: b['systolic_bp']?.toString() ?? state.systolicBp,
          diastolicBp: b['diastolic_bp']?.toString() ?? state.diastolicBp,
          totalCholesterol:
              b['total_cholesterol_mg_dl']?.toString() ?? state.totalCholesterol,
          hdl: b['hdl_cholesterol_mg_dl']?.toString() ?? state.hdl,
          ldl: b['ldl_cholesterol_mg_dl']?.toString() ?? state.ldl,
          fastingGlucose: b['fasting_blood_glucose_mg_dl']?.toString() ??
              state.fastingGlucose,
          hba1c: b['hba1c_percent']?.toString() ?? state.hba1c,
          creatinine:
              b['serum_creatinine_mg_dl']?.toString() ?? state.creatinine,
        );
      }
    } catch (_) {
      // Retain defaults on network error
    }
  }

  Future<void> save() async {
    try {
      final Map<String, dynamic> biomarkers = <String, dynamic>{
        if (double.tryParse(state.systolicBp) != null)
          'systolic_bp': double.parse(state.systolicBp),
        if (double.tryParse(state.diastolicBp) != null)
          'diastolic_bp': double.parse(state.diastolicBp),
        if (double.tryParse(state.totalCholesterol) != null)
          'total_cholesterol_mg_dl': double.parse(state.totalCholesterol),
        if (double.tryParse(state.hdl) != null)
          'hdl_cholesterol_mg_dl': double.parse(state.hdl),
        if (double.tryParse(state.ldl) != null)
          'ldl_cholesterol_mg_dl': double.parse(state.ldl),
        if (double.tryParse(state.fastingGlucose) != null)
          'fasting_blood_glucose_mg_dl': double.parse(state.fastingGlucose),
        if (double.tryParse(state.hba1c) != null)
          'hba1c_percent': double.parse(state.hba1c),
        if (double.tryParse(state.creatinine) != null)
          'serum_creatinine_mg_dl': double.parse(state.creatinine),
      };

      String formattedDate = state.testDate.trim();
      if (!formattedDate.contains('-')) {
        formattedDate = DateTime.now().toIso8601String().split('T').first;
      }

      final LabResultModel model = LabResultModel(
        testDate: formattedDate,
        labName: state.labName,
        biomarkers: biomarkers,
        notes: state.pathologistNotes,
      );
      await ref.read(laboratoryRepositoryProvider).saveLabResult(model);
    } catch (_) {
      // Retain state on network error
    }
  }

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
  void setSystolicBp(String value) {
    state = state.copyWith(systolicBp: value);
    save();
  }

  void setDiastolicBp(String value) {
    state = state.copyWith(diastolicBp: value);
    save();
  }

  void setTotalCholesterol(String value) {
    state = state.copyWith(totalCholesterol: value);
    save();
  }

  void setHdl(String value) {
    state = state.copyWith(hdl: value);
    save();
  }

  void setLdl(String value) {
    state = state.copyWith(ldl: value);
    save();
  }

  void setHba1c(String value) {
    state = state.copyWith(hba1c: value);
    save();
  }

  void setFastingGlucose(String value) {
    state = state.copyWith(fastingGlucose: value);
    save();
  }

  void setCreatinine(String value) {
    state = state.copyWith(creatinine: value);
    save();
  }

  void setTestDate(String value) {
    state = state.copyWith(testDate: value);
    save();
  }

  void setLabName(String value) {
    state = state.copyWith(labName: value);
    save();
  }

  void setPathologistNotes(String value) {
    state = state.copyWith(pathologistNotes: value);
    save();
  }
}

final NotifierProvider<LabsVitalsController, LabsVitalsState>
    labsVitalsProvider =
    NotifierProvider<LabsVitalsController, LabsVitalsState>(
  LabsVitalsController.new,
);
