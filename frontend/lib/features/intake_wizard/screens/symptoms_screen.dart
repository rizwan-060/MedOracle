import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../providers/symptoms_provider.dart';
import '../widgets/combo_input_field.dart';
import '../widgets/dashed_add_button.dart';
import '../widgets/intake_text_field.dart';
import '../widgets/notes_text_area.dart';
import '../widgets/option_picker_sheet.dart';
import '../widgets/section_card.dart';
import '../widgets/selectable_chips.dart';
import '../widgets/severity_slider.dart';
import '../widgets/wizard_header.dart';
import '../widgets/wizard_next_back_buttons.dart';

/// Step 3 of the intake wizard — symptom capture: what the patient feels,
/// where, what triggers it, how severe, for how long, plus free notes.
class SymptomsScreen extends ConsumerStatefulWidget {
  const SymptomsScreen({super.key});

  static const String routePath = RouteNames.symptoms;

  @override
  ConsumerState<SymptomsScreen> createState() => _SymptomsScreenState();
}

class _SymptomsScreenState extends ConsumerState<SymptomsScreen> {
  final TextEditingController _symptomQueryController =
      TextEditingController();

  @override
  void dispose() {
    _symptomQueryController.dispose();
    super.dispose();
  }

  void _commitSymptom(SymptomsController controller) {
    controller.addSymptom(_symptomQueryController.text);
    _symptomQueryController.clear();
  }

  @override
  Widget build(BuildContext context) {
    final SymptomsState state = ref.watch(symptomsProvider);
    final SymptomsController controller = ref.read(symptomsProvider.notifier);

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
              currentStep: 3,
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
                      title: SymptomsSection.symptoms.title,
                      isActive:
                          state.openSection == SymptomsSection.symptoms,
                      isExpanded:
                          state.openSection == SymptomsSection.symptoms,
                      onToggle: () =>
                          controller.toggleSection(SymptomsSection.symptoms),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          SelectableChips(
                            items: state.symptoms,
                            onRemoved: controller.removeSymptom,
                          ),
                          const SizedBox(height: 12),
                          ComboInputField(
                            controller: _symptomQueryController,
                            hintText: 'Search symptoms...',
                            onSubmitted: (_) => _commitSymptom(controller),
                          ),
                          const SizedBox(height: 12),
                          DashedAddButton(
                            label: '+ Add Symptom',
                            onTap: () => _commitSymptom(controller),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    SectionCard(
                      title: SymptomsSection.bodyLocation.title,
                      isExpanded:
                          state.openSection == SymptomsSection.bodyLocation,
                      onToggle: () => controller
                          .toggleSection(SymptomsSection.bodyLocation),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          SelectableChips(
                            items: state.bodyLocations,
                            onRemoved: controller.removeBodyLocation,
                          ),
                          const SizedBox(height: 12),
                          DashedAddButton(
                            label: '+ Add Location',
                            onTap: () async {
                              final String? picked =
                                  await showOptionPickerSheet(
                                context,
                                title: 'Body Location',
                                options: const [
                                  'Chest',
                                  'Left Arm',
                                  'Right Arm',
                                  'Jaw',
                                  'Neck',
                                  'Back',
                                  'Abdomen',
                                  'Legs',
                                  'Head',
                                ],
                              );
                              if (picked != null) {
                                controller.addBodyLocation(picked);
                              }
                            },
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    SectionCard(
                      title: SymptomsSection.triggers.title,
                      isExpanded: state.openSection == SymptomsSection.triggers,
                      onToggle: () =>
                          controller.toggleSection(SymptomsSection.triggers),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          SelectableChips(
                            items: state.triggers,
                            onRemoved: controller.removeTrigger,
                          ),
                          const SizedBox(height: 12),
                          DashedAddButton(
                            label: '+ Add Trigger',
                            onTap: () async {
                              final String? picked =
                                  await showOptionPickerSheet(
                                context,
                                title: 'Trigger',
                                options: const [
                                  'Physical Exertion',
                                  'Stress',
                                  'Cold Air',
                                  'Heavy Meals',
                                  'Poor Sleep',
                                  'Alcohol',
                                  'Medication',
                                ],
                              );
                              if (picked != null) {
                                controller.addTrigger(picked);
                              }
                            },
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    SectionCard(
                      title: SymptomsSection.severityRating.title,
                      isExpanded:
                          state.openSection == SymptomsSection.severityRating,
                      onToggle: () => controller
                          .toggleSection(SymptomsSection.severityRating),
                      child: SeveritySlider(
                        value: state.severity,
                        onChanged: controller.setSeverity,
                      ),
                    ),
                    const SizedBox(height: 12),
                    SectionCard(
                      title: SymptomsSection.duration.title,
                      isExpanded: state.openSection == SymptomsSection.duration,
                      onToggle: () =>
                          controller.toggleSection(SymptomsSection.duration),
                      child: IntakeTextField(
                        hintText: 'e.g. 3',
                        suffixText: 'days',
                        keyboardType: TextInputType.number,
                        onChanged: controller.setDurationValue,
                      ),
                    ),
                    const SizedBox(height: 12),
                    SectionCard(
                      title: SymptomsSection.contextualNotes.title,
                      isActive:
                          state.openSection == SymptomsSection.contextualNotes,
                      isExpanded:
                          state.openSection == SymptomsSection.contextualNotes,
                      onToggle: () => controller
                          .toggleSection(SymptomsSection.contextualNotes),
                      child: NotesTextArea(
                        height: 96,
                        hintText: 'Describe when it happens, what helps…',
                        onChanged: controller.setNotes,
                      ),
                    ),
                    const SizedBox(height: 24),
                    GradientNextButton(
                      label: 'Next: Labs & Vitals',
                      onTap: () => context.go(RouteNames.labsVitals),
                    ),
                    BackTextButton(
                      onTap: () => context.go(RouteNames.medicationsFamily),
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
