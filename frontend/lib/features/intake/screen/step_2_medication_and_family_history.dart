import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:material_ui/material_ui.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../providers/clinical_status_provider.dart';
import '../widgets/assessment_chrome.dart';
import '../widgets/clinical_status_done_view.dart';
import '../widgets/clinical_status_search_card.dart';
import '../widgets/clinical_status_sheets.dart';

/// AS2A — clinical status.
///
/// Renders the exact empty, adding and done states described by the intake
/// design reference, including the surgery/allergy/notes bottom sheets.
class Step2MedicationAndFamilyHistoryScreen extends ConsumerStatefulWidget {
  const Step2MedicationAndFamilyHistoryScreen({super.key});

  static const String routePath = RouteNames.step2ClinicalStatus;

  @override
  ConsumerState<Step2MedicationAndFamilyHistoryScreen> createState() =>
      _Step2MedicationAndFamilyHistoryScreenState();
}

class _Step2MedicationAndFamilyHistoryScreenState
    extends ConsumerState<Step2MedicationAndFamilyHistoryScreen> {
  final TextEditingController _searchController = TextEditingController();
  final FocusNode _searchFocus = FocusNode();

  bool _suggestionsVisible = false;
  bool _accordionExpanded = true;

  @override
  void dispose() {
    _searchController.dispose();
    _searchFocus.dispose();
    super.dispose();
  }

  void _showSuggestions() {
    if (!_suggestionsVisible) setState(() => _suggestionsVisible = true);
  }

  void _addCondition(String name) {
    ref.read(clinicalStatusProvider.notifier).addCondition(name);
    _searchController.clear();
    setState(() => _suggestionsVisible = false);
  }

  void _removeCondition(String name) {
    ref.read(clinicalStatusProvider.notifier).removeCondition(name);
    setState(() => _suggestionsVisible = false);
  }

  void _finishAdding() {
    _searchFocus.unfocus();
    setState(() {
      _suggestionsVisible = false;
      _accordionExpanded = true;
    });
    ref.read(clinicalStatusProvider.notifier).completeAdding();
  }

  void _noConditions() {
    _searchFocus.unfocus();
    setState(() {
      _suggestionsVisible = false;
      _accordionExpanded = true;
    });
    ref.read(clinicalStatusProvider.notifier).clearConditions();
  }

  void _editConditions() {
    ref.read(clinicalStatusProvider.notifier).editConditions();
  }

  void _toggleAccordion() {
    setState(() => _accordionExpanded = !_accordionExpanded);
  }

  Future<void> _openSheet(ClinicalStatusSheetKind kind) async {
    _searchFocus.unfocus();
    await showClinicalStatusSheet(context: context, kind: kind);
  }

  @override
  Widget build(BuildContext context) {
    final ClinicalStatusState state = ref.watch(clinicalStatusProvider);
    final bool ctaEnabled =
        state.conditions.isNotEmpty || state.phase == ClinicalStatusPhase.done;

    return AssessmentShell(
      title: 'Clinical status',
      filledSteps: 2,
      ctaLabel: 'Continue to medications',
      ctaEnabled: ctaEnabled,
      ctaColor: AppColors.terraCotta,
      onBack: () => context.go(RouteNames.onboardingPath),
      onContinue: () => context.go(RouteNames.step2b),
      child: switch (state.phase) {
        ClinicalStatusPhase.empty => ClinicalStatusSearchCard.empty(
            controller: _searchController,
            focusNode: _searchFocus,
            suggestionsVisible: _suggestionsVisible,
            onSearchTap: _showSuggestions,
            onQueryChanged: (String value) {
              ref.read(clinicalStatusProvider.notifier).setConditionQuery(value);
              _showSuggestions();
            },
            onSuggestion: _addCondition,
            onDoneAdding: _finishAdding,
            onNoConditions: _noConditions,
          ),
        ClinicalStatusPhase.adding => ClinicalStatusSearchCard.adding(
            controller: _searchController,
            focusNode: _searchFocus,
            conditions: state.conditions,
            onSearchTap: _showSuggestions,
            onQueryChanged: (String value) {
              ref.read(clinicalStatusProvider.notifier).setConditionQuery(value);
              _showSuggestions();
            },
            onSuggestion: _addCondition,
            onRemoveCondition: _removeCondition,
            onDoneAdding: _finishAdding,
          ),
        ClinicalStatusPhase.done => ClinicalStatusDoneView(
            conditions: state.conditions,
            surgeries: state.surgeries,
            allergies: state.allergies,
            expanded: _accordionExpanded,
            onToggle: _toggleAccordion,
            onEdit: _editConditions,
            onSurgeryTap: () => _openSheet(ClinicalStatusSheetKind.surgery),
            onAllergyTap: () => _openSheet(ClinicalStatusSheetKind.allergy),
            onNotesTap: () => _openSheet(ClinicalStatusSheetKind.notes),
          ),
      },
    );
  }
}
