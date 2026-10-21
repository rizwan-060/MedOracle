import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../providers/medications_family_provider.dart';
import '../widgets/dashed_add_button.dart';
import '../widgets/field_label.dart';
import '../widgets/intake_text_field.dart';
import '../widgets/option_picker_sheet.dart';
import '../widgets/section_card.dart';
import '../widgets/selectable_chips.dart';
import '../widgets/two_column_row.dart';
import '../widgets/wizard_header.dart';
import '../widgets/wizard_next_back_buttons.dart';

/// Step 2B of the intake wizard — current medications and family history.
class MedicationsFamilyScreen extends ConsumerWidget {
  const MedicationsFamilyScreen({super.key});

  static const String routePath = RouteNames.medicationsFamily;

  static const List<String> _frequencies = <String>[
    'Once Daily',
    'Twice Daily',
    'Three Times Daily',
    'Weekly',
    'As Needed',
  ];

  static const List<String> _relatives = <String>[
    'Father',
    'Mother',
    'Brother',
    'Sister',
    'Son',
    'Daughter',
    'Grandparent',
    'Other',
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final MedicationsFamilyState state =
        ref.watch(medicationsFamilyProvider);
    final MedicationsFamilyController controller =
        ref.read(medicationsFamilyProvider.notifier);

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
              currentStep: 2,
              totalSteps: 5,
              onSaveExit: () {/* persist + leave wizard */},
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 12, 20, 18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    SectionCard(
                      title: 'Current Medications',
                      isActive: true,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          if (state.medications.isNotEmpty) ...[
                            SelectableChips(
                              items: state.medications
                                  .map((m) => m.label)
                                  .toList(),
                              onRemoved: controller.removeMedication,
                            ),
                            const SizedBox(height: 12),
                          ],
                          const FieldLabel('Medication Name'),
                          const SizedBox(height: 4),
                          IntakeTextField(
                            hintText: 'e.g. Amlodipine',
                            onChanged: controller.setMedNameDraft,
                          ),
                          const SizedBox(height: 12),
                          const FieldLabel('Dosage'),
                          const SizedBox(height: 4),
                          IntakeTextField(
                            hintText: 'e.g. 5mg',
                            onChanged: controller.setDosageDraft,
                          ),
                          const SizedBox(height: 12),
                          const FieldLabel('Frequency'),
                          const SizedBox(height: 4),
                          IntakeTextField(
                            hintText: 'Select frequency',
                            readOnly: true,
                            showChevron: true,
                            value: state.frequencyDraft,
                            onTap: () async {
                              final String? picked =
                                  await showOptionPickerSheet(
                                context,
                                title: 'Frequency',
                                options: _frequencies,
                              );
                              if (picked != null) {
                                controller.setFrequencyDraft(picked);
                              }
                            },
                          ),
                          const SizedBox(height: 12),
                          DashedAddButton(
                            label: '+ Add Medication',
                            onTap: controller.addMedication,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    SectionCard(
                      title: 'Family History',
                      isExpanded: state.familyExpanded,
                      onToggle: controller.toggleFamilyExpanded,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          if (state.familyRecords.isNotEmpty) ...[
                            SelectableChips(
                              items: state.familyRecords
                                  .map((r) => r.label)
                                  .toList(),
                              onRemoved: controller.removeFamilyRecord,
                            ),
                            const SizedBox(height: 12),
                          ],
                          TwoColumnRow(
                            left: Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                const FieldLabel('Relative'),
                                const SizedBox(height: 4),
                                IntakeTextField(
                                  hintText: 'Select',
                                  readOnly: true,
                                  showChevron: true,
                                  value: state.relativeDraft,
                                  onTap: () async {
                                    final String? picked =
                                        await showOptionPickerSheet(
                                      context,
                                      title: 'Relative',
                                      options: _relatives,
                                    );
                                    if (picked != null) {
                                      controller.setRelativeDraft(picked);
                                    }
                                  },
                                ),
                              ],
                            ),
                            right: Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                const FieldLabel('Age at Diagnosis'),
                                const SizedBox(height: 4),
                                IntakeTextField(
                                  hintText: 'e.g. 52',
                                  keyboardType: TextInputType.number,
                                  onChanged: controller.setAgeDraft,
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 12),
                          const FieldLabel('Condition'),
                          const SizedBox(height: 4),
                          IntakeTextField(
                            hintText: 'e.g. Myocardial infarction',
                            onChanged: controller.setConditionDraft,
                          ),
                          const SizedBox(height: 12),
                          DashedAddButton(
                            label: '+ Add Family Record',
                            onTap: controller.addFamilyRecord,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),
                    GradientNextButton(
                      label: 'Save & Continue',
                      onTap: () => context.go(RouteNames.symptoms),
                    ),
                    BackTextButton(
                      onTap: () => context.go(RouteNames.clinicalStatus),
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
