import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:material_ui/material_ui.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../providers/as2b_meds_family_provider.dart';
import '../widgets/assessment_chrome.dart';
import '../widgets/medications_family_drawer.dart';
import '../widgets/medications_family_pile.dart';

/// AS2B — medications and family history.
///
/// The reference screen has no footer; the add-history drawer is anchored at
/// the bottom and starts open on the Family Record tab.
class Step2BMedicationsAndFamilyHistoryScreen extends ConsumerWidget {
  const Step2BMedicationsAndFamilyHistoryScreen({super.key});

  static const String routePath = RouteNames.step2b;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final As2bMedsFamilyState state = ref.watch(as2bMedsFamilyProvider);
    final As2bMedsFamilyController controller =
        ref.read(as2bMedsFamilyProvider.notifier);
    final double bottomInset =
        (state.drawerOpen
                ? MedicationsFamilyDrawer.openHeight
                : MedicationsFamilyDrawer.closedHeight) +
            24;

    return Scaffold(
      resizeToAvoidBottomInset: false,
      backgroundColor: AppColors.canvasBackground,
      body: Stack(
        children: <Widget>[
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: AssessmentHeader(
              title: 'Medications & family',
              filledSteps: 2,
              onBack: () => context.go(RouteNames.step2ClinicalStatus),
            ),
          ),
          Positioned(
            top: 207,
            left: 0,
            right: 0,
            bottom: 0,
            child: SingleChildScrollView(
              padding: EdgeInsets.fromLTRB(20, 24, 20, bottomInset),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: <Widget>[
                  MedicationsFamilySection(
                    title: 'Current Medications',
                    items: state.medications,
                    countLabel: '${state.medications.length} Medications',
                    expanded: state.medicationsExpanded,
                    onToggle: controller.toggleMedicationsExpanded,
                    onRemove: controller.removeMedication,
                  ),
                  const SizedBox(height: 40),
                  MedicationsFamilySection(
                    title: 'Family History',
                    items: state.family,
                    countLabel: '${state.family.length} Records',
                    expanded: state.familyExpanded,
                    onToggle: controller.toggleFamilyExpanded,
                    onRemove: controller.removeFamily,
                  ),
                ],
              ),
            ),
          ),
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: MedicationsFamilyDrawer(),
          ),
        ],
      ),
    );
  }
}