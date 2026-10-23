/// Domain models of the lifestyle simulation.
///
/// The simulation answers a single question: "what would my 1-year risk be
/// if I changed these four things?". The scoring is intentionally simple and
/// lives on the client so the sliders can respond instantly
/// (design: v8 Step 6C "Simulate Lifestyle Changes").
library;

import 'dart:math' as math;

/// The lifestyle changes the user is testing.
///
/// The defaults mirror the design reference: 5 kg of weight loss, a 10 mmHg
/// blood pressure drop, no smoking and no daily walk.
class LifestyleInputs {
  const LifestyleInputs({
    this.weightKg = defaultWeightKg,
    this.bloodPressureMmHg = defaultBloodPressureMmHg,
    this.quitSmoking = true,
    this.walkThirtyMinutesDaily = false,
  });

  /// Default weight reduction, in kilograms.
  static const int defaultWeightKg = 5;

  /// Default blood pressure reduction, in mmHg.
  static const int defaultBloodPressureMmHg = 10;

  /// Largest weight reduction the slider allows.
  static const int maxWeightKg = 15;

  /// Largest blood pressure reduction the slider allows.
  static const int maxBloodPressureMmHg = 20;

  /// The true minus sign (U+2212) used by the design reference.
  static const String minusSign = '\u2212';

  /// Weight reduction, in kilograms.
  final int weightKg;

  /// Blood pressure reduction, in mmHg.
  final int bloodPressureMmHg;

  /// Whether the user has quit smoking.
  final bool quitSmoking;

  /// Whether the user walks 30 minutes every day.
  final bool walkThirtyMinutesDaily;

  /// Read-out of the weight slider, e.g. `-5 kg`.
  String get weightLabel {
    return weightKg == 0 ? '0 kg' : '$minusSign$weightKg kg';
  }

  /// Read-out of the blood pressure slider, e.g. `-10 mmHg`.
  String get bloodPressureLabel {
    return bloodPressureMmHg == 0
        ? '0 mmHg'
        : '$minusSign$bloodPressureMmHg mmHg';
  }

  /// Returns a copy of these inputs with the given fields replaced.
  LifestyleInputs copyWith({
    int? weightKg,
    int? bloodPressureMmHg,
    bool? quitSmoking,
    bool? walkThirtyMinutesDaily,
  }) {
    return LifestyleInputs(
      weightKg: weightKg ?? this.weightKg,
      bloodPressureMmHg: bloodPressureMmHg ?? this.bloodPressureMmHg,
      quitSmoking: quitSmoking ?? this.quitSmoking,
      walkThirtyMinutesDaily:
          walkThirtyMinutesDaily ?? this.walkThirtyMinutesDaily,
    );
  }
}

/// The risk projection produced by a set of lifestyle changes.
///
/// Every change removes a fixed number of points from the baseline risk; the
/// projection can never drop below 1 point.
class RiskProjection {
  const RiskProjection({
    required this.baseline,
    required this.simulated,
    required this.delta,
  });

  /// The user's current 1-year risk, before any change.
  static const int baselineRisk = 29;

  /// Points removed per kilogram of weight loss (4 points across 15 kg).
  static const double weightPointsPerKg = 4 / 15;

  /// Points removed per mmHg of blood pressure drop (5 points across 20 mmHg).
  static const double bloodPressurePointsPerMmHg = 5 / 20;

  /// Points removed by quitting smoking.
  static const int quitSmokingPoints = 7;

  /// Points removed by walking 30 minutes a day.
  static const int walkThirtyMinutesDailyPoints = 3;

  /// Risk before the lifestyle changes, out of 100.
  final int baseline;

  /// Risk after the lifestyle changes, out of 100.
  final int simulated;

  /// Points removed by the lifestyle changes.
  final int delta;

  /// Whether the changes actually moved the risk.
  bool get hasDelta => delta > 0;

  /// Label of the delta pill, e.g. `11 points lower`.
  String get deltaLabel {
    if (delta <= 0) {
      return 'No change yet';
    }
    if (delta == 1) {
      return '1 point lower';
    }
    return '$delta points lower';
  }

  /// Projects [inputs] onto the baseline risk.
  static RiskProjection from(LifestyleInputs inputs) {
    final double removed =
        inputs.weightKg * weightPointsPerKg +
        inputs.bloodPressureMmHg * bloodPressurePointsPerMmHg +
        (inputs.quitSmoking ? quitSmokingPoints : 0) +
        (inputs.walkThirtyMinutesDaily ? walkThirtyMinutesDailyPoints : 0);

    final int simulated = math.max(1, (baselineRisk - removed).round());

    return RiskProjection(
      baseline: baselineRisk,
      simulated: simulated,
      delta: baselineRisk - simulated,
    );
  }
}

/// A lifestyle plan the user committed to with "Save Action Plan".
class SavedActionPlan {
  const SavedActionPlan({required this.inputs, required this.projection});

  /// The changes the user committed to.
  final LifestyleInputs inputs;

  /// The risk projection those changes produce.
  final RiskProjection projection;

  /// Headline of the confirmation shown on the dashboard.
  String get headline => 'Action plan saved \u00B7 ${projection.deltaLabel}';
}
