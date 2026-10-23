import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/simulation_models.dart';

/// The lifestyle changes currently being simulated.
///
/// The defaults come straight from the design reference (5 kg, 10 mmHg, no
/// smoking, no daily walk) so the screen opens on the documented scenario.
final lifestyleInputsProvider =
    NotifierProvider<LifestyleInputsController, LifestyleInputs>(
      LifestyleInputsController.new,
    );

/// Controller of [lifestyleInputsProvider].
class LifestyleInputsController extends Notifier<LifestyleInputs> {
  @override
  LifestyleInputs build() => const LifestyleInputs();

  /// Sets the weight reduction, clamped to the slider range.
  void setWeightKg(int value) {
    state = state.copyWith(
      weightKg: value.clamp(0, LifestyleInputs.maxWeightKg),
    );
  }

  /// Sets the blood pressure reduction, clamped to the slider range.
  void setBloodPressureMmHg(int value) {
    state = state.copyWith(
      bloodPressureMmHg: value.clamp(0, LifestyleInputs.maxBloodPressureMmHg),
    );
  }

  /// Sets the "quit smoking" switch.
  void setQuitSmoking(bool value) {
    state = state.copyWith(quitSmoking: value);
  }

  /// Sets the "walk 30 mins daily" switch.
  void setWalkThirtyMinutesDaily(bool value) {
    state = state.copyWith(walkThirtyMinutesDaily: value);
  }
}

/// The risk projection of the current [lifestyleInputsProvider] value.
final riskProjectionProvider = Provider<RiskProjection>((Ref ref) {
  return RiskProjection.from(ref.watch(lifestyleInputsProvider));
});

/// The action plan the user last saved.
///
/// The dashboard consumes the plan once to confirm the save, then clears it.
final savedActionPlanProvider =
    NotifierProvider<SavedActionPlanController, SavedActionPlan?>(
      SavedActionPlanController.new,
    );

/// Controller of [savedActionPlanProvider].
class SavedActionPlanController extends Notifier<SavedActionPlan?> {
  @override
  SavedActionPlan? build() => null;

  /// Stores [plan] as the user's committed action plan.
  void save(SavedActionPlan plan) => state = plan;

  /// Returns the pending plan and clears it so it is only surfaced once.
  SavedActionPlan? take() {
    final SavedActionPlan? plan = state;
    state = null;
    return plan;
  }
}
