/// Route paths and names for the MedOracle router.
abstract final class RouteNames {
  // --- Home ------------------------------------------------------------------
  static const String home = '/home';

  // --- Intake (data entry) flow --------------------------------------------
  static const String intakeRoot = '/intake';
  static const String step1Profile = '$intakeRoot/step-1';
  static const String step2Clinical = '$intakeRoot/step-2a';
  static const String step2Medications = '$intakeRoot/step-2b';
  static const String step3Symptoms = '$intakeRoot/step-3';
  static const String step4Labs = '$intakeRoot/step-4';
  static const String step5Review = '$intakeRoot/step-5';

  // --- Assessment (results) flow -------------------------------------------
  static const String resultsRoot = '/results';
  static const String resultsReports = '$resultsRoot/reports';
  static const String resultsTrajectory = '$resultsRoot/trajectory';
  static const String resultsReasoning = '$resultsRoot/reasoning';
  static const String resultsCareFinder = '$resultsRoot/care-finder';
  static const String resultsSimulate = '$resultsRoot/simulate';
}
