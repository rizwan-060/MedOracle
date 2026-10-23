import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_colors.dart';
import '../intake_routes.dart';
import '../providers/labs_vitals_provider.dart';
import '../widgets/field_label.dart';
import '../widgets/intake_text_field.dart';
import '../widgets/notes_text_area.dart';
import '../widgets/section_card.dart';
import '../widgets/two_column_row.dart';
import '../widgets/wizard_header.dart';
import '../widgets/wizard_next_back_buttons.dart';

/// Step 4 of the intake wizard — general vitals and recent lab results.
class LabsVitalsScreen extends ConsumerWidget {
  const LabsVitalsScreen({super.key});

  static const String routePath = IntakeRoutes.labsVitals;

  /// Labeled numeric input with a unit suffix (design's `.l` + `.in` + `.u`).
  Widget _unitField({
    required String label,
    required String unit,
    required String value,
    required ValueChanged<String> onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        FieldLabel(label),
        const SizedBox(height: 4),
        IntakeTextField(
          value: value,
          suffixText: unit,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          onChanged: onChanged,
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final LabsVitalsState state = ref.watch(labsVitalsProvider);
    final LabsVitalsController controller =
        ref.read(labsVitalsProvider.notifier);

    return Scaffold(
      backgroundColor: AppColors.canvasBackground,
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              AppColors.dustyTaupe,
              AppColors.canvasBackground,
            ],
            stops: [0, 0.35],
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            WizardHeader(
              currentStep: 4,
              totalSteps: 5,
              onSaveExit: () => context.go(IntakeRoutes.dashboard),
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 12, 20, 18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    SectionCard(
                      title: LabsSection.generalVitals.title,
                      isActive:
                          state.openSection == LabsSection.generalVitals,
                      isExpanded:
                          state.openSection == LabsSection.generalVitals,
                      onToggle: () =>
                          controller.toggleSection(LabsSection.generalVitals),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          TwoColumnRow(
                            left: _unitField(
                              label: 'Height',
                              unit: 'cm',
                              value: state.heightCm,
                              onChanged: controller.setHeight,
                            ),
                            right: _unitField(
                              label: 'Weight',
                              unit: 'kg',
                              value: state.weightKg,
                              onChanged: controller.setWeight,
                            ),
                          ),
                          const SizedBox(height: 12),
                          _unitField(
                            label: 'Waist Circumference',
                            unit: 'cm',
                            value: state.waistCm,
                            onChanged: controller.setWaist,
                          ),
                          const SizedBox(height: 12),
                          TwoColumnRow(
                            left: _unitField(
                              label: 'Systolic BP',
                              unit: 'mmHg',
                              value: state.systolicBp,
                              onChanged: controller.setSystolicBp,
                            ),
                            right: _unitField(
                              label: 'Diastolic BP',
                              unit: 'mmHg',
                              value: state.diastolicBp,
                              onChanged: controller.setDiastolicBp,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    SectionCard(
                      title: LabsSection.lipidPanel.title,
                      isExpanded: state.openSection == LabsSection.lipidPanel,
                      onToggle: () =>
                          controller.toggleSection(LabsSection.lipidPanel),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          _unitField(
                            label: 'Total Cholesterol',
                            unit: 'mg/dL',
                            value: state.totalCholesterol,
                            onChanged: controller.setTotalCholesterol,
                          ),
                          const SizedBox(height: 12),
                          _unitField(
                            label: 'HDL',
                            unit: 'mg/dL',
                            value: state.hdl,
                            onChanged: controller.setHdl,
                          ),
                          const SizedBox(height: 12),
                          _unitField(
                            label: 'LDL',
                            unit: 'mg/dL',
                            value: state.ldl,
                            onChanged: controller.setLdl,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    SectionCard(
                      title: LabsSection.glycemicRenal.title,
                      isExpanded:
                          state.openSection == LabsSection.glycemicRenal,
                      onToggle: () =>
                          controller.toggleSection(LabsSection.glycemicRenal),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          _unitField(
                            label: 'HbA1c',
                            unit: '%',
                            value: state.hba1c,
                            onChanged: controller.setHba1c,
                          ),
                          const SizedBox(height: 12),
                          _unitField(
                            label: 'Fasting Blood Glucose',
                            unit: 'mg/dL',
                            value: state.fastingGlucose,
                            onChanged: controller.setFastingGlucose,
                          ),
                          const SizedBox(height: 12),
                          _unitField(
                            label: 'Serum Creatinine',
                            unit: 'mg/dL',
                            value: state.creatinine,
                            onChanged: controller.setCreatinine,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    SectionCard(
                      title: LabsSection.labDetails.title,
                      isExpanded: state.openSection == LabsSection.labDetails,
                      onToggle: () =>
                          controller.toggleSection(LabsSection.labDetails),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          FieldLabel('Test Date'),
                          const SizedBox(height: 4),
                          IntakeTextField(
                            value: state.testDate,
                            hintText: 'e.g. 12 Oct 2026',
                            onChanged: controller.setTestDate,
                          ),
                          const SizedBox(height: 12),
                          FieldLabel('Lab Name'),
                          const SizedBox(height: 4),
                          IntakeTextField(
                            value: state.labName,
                            hintText: 'e.g. City Diagnostics',
                            onChanged: controller.setLabName,
                          ),
                          const SizedBox(height: 12),
                          const FieldLabel('Pathologist Notes'),
                          const SizedBox(height: 4),
                          NotesTextArea(
                            hintText: 'notes... Type any extra...',
                            onChanged: controller.setPathologistNotes,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),
                    GradientNextButton(
                      label: 'Next: Review & Confirm',
                      onTap: () => context.go(IntakeRoutes.review),
                    ),
                    BackTextButton(
                      onTap: () => context.go(IntakeRoutes.symptoms),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
