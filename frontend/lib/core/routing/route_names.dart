/// Route paths and names for the MedOracle router.
abstract final class RouteNames {
  // --- Onboarding -------------------------------------------------------------
  static const String onboardingRoot = '/onboarding';
  static const String onboardingWelcome = '$onboardingRoot/welcome';
  static const String onboardingCareTeam = '$onboardingRoot/care-team';
  static const String onboardingProfile = '$onboardingRoot/profile';

  /// OB3 is the blood-type/you introduction hosted by [onboardingProfile].
  static const String onboardingBloodType = onboardingProfile;

  static const String onboardingBody = '$onboardingRoot/body';

  /// OB4 is the body-details step hosted by [onboardingBody].
  static const String onboardingBodyDetails = onboardingBody;

  static const String onboardingHabits = '$onboardingRoot/habits';
  static const String onboardingPath = '$onboardingRoot/path';

  // --- Auth -------------------------------------------------------------------
  static const String login = '/login';
  static const String signup = '/signup';

  /// Backward-compatible alias for the authentication entry point.
  static const String auth = login;

  // --- Home / Dashboard -------------------------------------------------------
  static const String dashboard = '/dashboard';
  static const String home = dashboard;

  // --- Intake (data entry) flow --------------------------------------------
  static const String intakeRoot = '/intake';
  static const String step1Clinical = '$intakeRoot/step-1';
  static const String step2Medications = '$intakeRoot/step-2';
  static const String step2ClinicalStatus = '/step_2_medication_and_family_history';
  static const String step2b = '/intake/step-2b';
  static const String step2bShort = '/step/2b';
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
