import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../models/simulation_models.dart';
import '../providers/simulation_providers.dart';
import '../widgets/simulated_risk_bar.dart';
import '../widgets/simulation_band.dart';
import '../widgets/simulation_baseline_card.dart';
import '../widgets/simulation_controls_card.dart';

/// Screen 6D - Simulate Lifestyle Changes.
///
/// Lets the user play with four lifestyle changes and see how far the
/// projected 1-year risk moves. The projection is computed on the client so
/// every control reacts immediately.
class SimulateLifestyleScreen extends ConsumerWidget {
  const SimulateLifestyleScreen({
    super.key,
    this.onClose,
    this.onSaveActionPlan,
  });

  /// Leaves the simulation (wired by the router).
  final VoidCallback? onClose;

  /// Called after the action plan has been stored.
  final VoidCallback? onSaveActionPlan;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final LifestyleInputs inputs = ref.watch(lifestyleInputsProvider);
    final RiskProjection projection = ref.watch(riskProjectionProvider);
    final LifestyleInputsController controller = ref.read(
      lifestyleInputsProvider.notifier,
    );

    return Scaffold(
      backgroundColor: AppColors.canvasBackground,
      body: Container(
        decoration: const BoxDecoration(gradient: AppColors.canvasGradient),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(20, 0, 20, 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                SimulationBand(
                  title: 'Simulate Lifestyle Changes',
                  subtitle:
                      'Adjust the controls below to see how specific '
                      'actions lower your future risk.',
                  onClose: onClose,
                ),
                const SizedBox(height: 16),
                SimulationBaselineCard(
                  label: 'Current 1-Year Risk',
                  value: '${projection.baseline}',
                  unit: 'out of 100',
                ),
                SimulationControlsCard(
                  weightKg: inputs.weightKg,
                  bloodPressureMmHg: inputs.bloodPressureMmHg,
                  quitSmoking: inputs.quitSmoking,
                  walkThirtyMinutesDaily:
                      inputs.walkThirtyMinutesDaily,
                  onWeightChanged: controller.setWeightKg,
                  onBloodPressureChanged: controller.setBloodPressureMmHg,
                  onQuitSmokingToggled: controller.setQuitSmoking,
                  onWalkToggled: controller.setWalkThirtyMinutesDaily,
                ),
                const SizedBox(height: 20),
                SimulatedRiskBar(
                  simulatedRisk: projection.simulated,
                  deltaLabel: projection.deltaLabel,
                  hasDelta: projection.hasDelta,
                  onSave: () => _saveActionPlan(context, ref),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Stores the action plan and returns to the dashboard.
  void _saveActionPlan(BuildContext context, WidgetRef ref) {
    ref
        .read(savedActionPlanProvider.notifier)
        .save(
          SavedActionPlan(
            inputs: ref.read(lifestyleInputsProvider),
            projection: ref.read(riskProjectionProvider),
          ),
        );

    final VoidCallback? onSaveActionPlan = this.onSaveActionPlan;
    if (onSaveActionPlan != null) {
      onSaveActionPlan();
      return;
    }
    context.go(RouteNames.dashboard);
  }
}
