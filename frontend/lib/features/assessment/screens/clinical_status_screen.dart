import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../providers/clinical_status_provider.dart';
import '../widgets/add_pill_button.dart';
import '../widgets/combo_input_field.dart';
import '../widgets/dashed_add_button.dart';
import '../widgets/notes_text_area.dart';
import '../widgets/section_card.dart';
import '../widgets/selectable_chips.dart';
import '../widgets/assessment_header.dart';
import '../widgets/assessment_nav_buttons.dart';

/// Step 2A of the intake wizard — clinical history:
/// chronic conditions, past surgeries, allergies, and free-text notes.
class ClinicalStatusScreen extends ConsumerWidget {
  const ClinicalStatusScreen({super.key});

  static const String routePath = RouteNames.clinicalStatus;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ClinicalStatusState state = ref.watch(clinicalStatusProvider);
    final ClinicalStatusController controller =
        ref.read(clinicalStatusProvider.notifier);

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
            AssessmentHeader(
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
                      title: 'Chronic Conditions',
                      isActive: true,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          SelectableChips(
                            items: state.conditions,
                            onRemoved: controller.removeCondition,
                          ),
                          const SizedBox(height: 12),
                          ComboInputField(
                            hintText: 'Search conditions…',
                            onChanged: controller.setConditionQuery,
                            onSubmitted: (_) => controller.addCondition(),
                          ),
                          const SizedBox(height: 12),
                          DashedAddButton(
                            label: '+ Add Condition',
                            onTap: () => controller.addCondition(),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    SectionCard(
                      title: 'Past Surgeries',
                      trailing: AddPillButton(
                        label: '+ Add Surgery',
                        onTap: () {/* open surgery input */},
                      ),
                      child: SelectableChips(
                        items: state.surgeries,
                        onRemoved: controller.removeSurgery,
                      ),
                    ),
                    const SizedBox(height: 12),
                    SectionCard(
                      title: 'Allergies',
                      trailing: AddPillButton(
                        label: '+ Add Allergy',
                        onTap: () {/* open allergy input */},
                      ),
                      child: SelectableChips(
                        items: state.allergies,
                        onRemoved: controller.removeAllergy,
                      ),
                    ),
                    const SizedBox(height: 12),
                    SectionCard(
                      title: 'Clinical Notes',
                      child: NotesTextArea(
                        hintText: 'notes... Type any extra...',
                        onChanged: controller.setNotes,
                      ),
                    ),
                    const SizedBox(height: 24),
                    GradientNextButton(
                      label: 'Next: Medications & Family',
                      onTap: () =>
                          context.go(RouteNames.medicationsFamily),
                    ),
                    BackTextButton(
                      onTap: () => context.go(RouteNames.profile),
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
