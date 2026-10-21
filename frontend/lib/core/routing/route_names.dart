/// Centralized route paths and names for the MedOracle application.
///
/// Single source of truth consumed by GoRouter configuration and all feature
/// navigation actions across the app.
abstract final class RouteNames {
  // --- Root & Entry ---
  static const String root = '/';

  // --- Authentication ---
  static const String authRoot = '/auth';
  static const String login = '$authRoot/login';
  static const String register = '$authRoot/register';

  // --- Patient Clinical Assessment Flow ---
  static const String patientProfile = '/patient-profile';
  static const String clinicalStatus = '/clinical-status';
  static const String medicationsFamily = '/medications-family';
  static const String symptoms = '/symptoms';
  static const String laboratoryVitals = '/laboratory-vitals';
  static const String assessmentReview = '/assessment-review';

  // --- Clinical Forecasting & Reasoning ---
  static const String assessmentReports = '/results/reports';
  static const String diseaseTrajectory = '/results/trajectory';
  static const String clinicalReasoning = '/results/reasoning';
  static const String counterfactualSimulator = '/results/simulate';

  // --- Domain Aliases ---
  static const String profile = patientProfile;
  static const String labsVitals = laboratoryVitals;
  static const String review = assessmentReview;
  static const String results = assessmentReports;
  static const String trajectory = diseaseTrajectory;
  static const String reasoning = clinicalReasoning;
  static const String simulate = counterfactualSimulator;

  // --- Clinical Dashboard & Specialists Directory ---
  static const String dashboard = '/dashboard';
  static const String doctorDirectory = '/doctors';
  static const String doctors = doctorDirectory;
}
