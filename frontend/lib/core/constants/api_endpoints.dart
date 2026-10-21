/// API endpoint constants for MedOracle backend services.
class ApiEndpoints {
  const ApiEndpoints._();

  /// Base API URL. Can be overridden via `--dart-define=MEDORACLE_API_URL=...`.
  /// Defaults to standard local FastAPI development server at localhost:8000.
  static const String baseUrl = String.fromEnvironment(
    'MEDORACLE_API_URL',
    defaultValue: 'http://127.0.0.1:8000/api/v1',
  );

  // Authentication
  static const String login = '/auth/login';
  static const String register = '/auth/register';
  static const String currentUser = '/auth/me';

  // Step 1: Patient Profile
  static const String patientProfile = '/patient/profile';

  // Step 2: Medical & Family History
  static const String medicalHistory = '/medical-history/';

  // Step 3: Symptoms Reporting
  static const String symptoms = '/symptoms/';

  // Step 4: Laboratory Biomarkers & Vitals
  static const String laboratory = '/laboratory/';
  static const String laboratoryLatest = '/laboratory/latest';

  // Quantitative Clinical Risk Models
  static const String riskCardiovascular = '/risk/cardiovascular';
  static const String riskDiabetes = '/risk/diabetes';
  static const String riskKidney = '/risk/kidney';
}
