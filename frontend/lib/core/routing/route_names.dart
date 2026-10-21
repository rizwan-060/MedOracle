/// Centralized route paths and names for the MedOracle application.
///
/// Single source of truth consumed by GoRouter configuration and all feature
/// navigation actions across the app.
abstract final class RouteNames {
  // --- Root & Entry ---
  static const String root = '/';

  // --- Authentication Flow ---
  static const String authRoot = '/auth';
  static const String login = '$authRoot/login';
  static const String register = '$authRoot/register';

  // --- Intake Assessment Wizard Flow ---
  static const String intakeRoot = '/intake';
  static const String step1Profile = '$intakeRoot/step-1';
  static const String step2Clinical = '$intakeRoot/step-2a';
  static const String step2Medications = '$intakeRoot/step-2b';
  static const String step3Symptoms = '$intakeRoot/step-3';
  static const String step4Labs = '$intakeRoot/step-4';
  static const String step5Review = '$intakeRoot/step-5';

  // Canonical alias identifiers for intake wizard steps
  static const String profile = step1Profile;
  static const String clinicalStatus = step2Clinical;
  static const String medicationsFamily = step2Medications;
  static const String symptoms = step3Symptoms;
  static const String labsVitals = step4Labs;
  static const String review = step5Review;

  // --- Assessment & Forecasting Flow ---
  static const String resultsRoot = '/results';
  static const String resultsReports = '$resultsRoot/reports';
  static const String resultsTrajectory = '$resultsRoot/trajectory';
  static const String resultsReasoning = '$resultsRoot/reasoning';
  static const String resultsSimulate = '$resultsRoot/simulate';

  // Canonical alias identifiers for results and reasoning
  static const String results = resultsReports;
  static const String trajectory = resultsTrajectory;
  static const String reasoning = resultsReasoning;
  static const String simulate = resultsSimulate;

  // --- Dashboard & Specialists Flow ---
  static const String dashboard = '/dashboard';
  static const String doctors = '/doctors';
}
