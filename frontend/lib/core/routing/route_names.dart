/// Route paths and names for the MedOracle router.
abstract final class RouteNames {
  // --- Auth -------------------------------------------------------------------
  static const String auth = '/';

  // --- Home / Dashboard -------------------------------------------------------
  static const String dashboard = '/dashboard';
  static const String home = dashboard;

  // --- Intake (data entry) flow --------------------------------------------
  static const String intakeRoot = '/intake';
  static const String step1Clinical = '$intakeRoot/step-1';
  static const String step2Medications = '$intakeRoot/step-2';
  static const String step3Symptoms = '$intakeRoot/step-3';
  static const String step4Labs = '$intakeRoot/step-4';
  static const String step5Review = '$intakeRoot/step-5';

  // Backward-compatible route aliases
  static const String step2Clinical = step1Clinical;

  // --- Assessment (results) flow -------------------------------------------
  static const String resultsRoot = '/results';
  static const String resultsReports = '$resultsRoot/reports';
  static const String resultsTrajectory = '$resultsRoot/trajectory';
  static const String resultsReasoning = '$resultsRoot/reasoning';
  static const String resultsCareFinder = '$resultsRoot/care-finder';
  static const String resultsSimulate = '$resultsRoot/simulate';
}
