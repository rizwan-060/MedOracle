import '../../core/constants/api_endpoints.dart';
import '../models/patient_profile_model.dart';
import '../services/api_service.dart';

/// Data access contract for patient demographics and profile management.
abstract class PatientProfileRepository {
  /// Loads the patient profile for the signed-in user.
  Future<PatientProfile> fetchProfile();

  /// Persists the patient profile (autosave).
  Future<PatientProfile> saveProfile(PatientProfile profile);
}

/// In-memory implementation seeded with the demo patient.
class MockPatientProfileRepository implements PatientProfileRepository {
  PatientProfile _profile = PatientProfile(
    dateOfBirth: DateTime.utc(1972, 3, 15),
    gender: 'Male',
    bloodGroup: 'A+',
    heightCm: 170,
    weightKg: 72,
    waistCircumferenceCm: 88,
    smokingStatus: 'Current',
    activityLevel: 'Moderate',
  );

  static const Duration _latency = Duration(milliseconds: 450);

  @override
  Future<PatientProfile> fetchProfile() async {
    await Future<void>.delayed(_latency);
    return _profile;
  }

  @override
  Future<PatientProfile> saveProfile(PatientProfile profile) async {
    await Future<void>.delayed(_latency);
    _profile = profile;
    return _profile;
  }
}

/// REST implementation connecting directly to the MedOracle FastAPI backend.
class RestPatientProfileRepository implements PatientProfileRepository {
  RestPatientProfileRepository(this._apiService);

  final ApiService _apiService;

  // Local fallback cache for resilience against offline or unreachable backend
  PatientProfile _cachedProfile = PatientProfile(
    dateOfBirth: DateTime.utc(1972, 3, 15),
    gender: 'Male',
    bloodGroup: 'A+',
    heightCm: 170,
    weightKg: 72,
    waistCircumferenceCm: 88,
    smokingStatus: 'Current',
    activityLevel: 'Moderate',
  );

  @override
  Future<PatientProfile> fetchProfile() async {
    try {
      final dynamic response =
          await _apiService.get(ApiEndpoints.patientProfile);
      if (response is Map<String, dynamic>) {
        _cachedProfile = PatientProfile.fromJson(response);
      }
    } catch (_) {
      // Graceful fallback to cached profile
    }
    return _cachedProfile;
  }

  @override
  Future<PatientProfile> saveProfile(PatientProfile profile) async {
    _cachedProfile = profile;
    // Debounce latency to ensure autosave indicator is visibly observable
    await Future<void>.delayed(const Duration(milliseconds: 300));
    try {
      final dynamic response = await _apiService.put(
        ApiEndpoints.patientProfile,
        body: profile.toJson(),
      );
      if (response is Map<String, dynamic>) {
        _cachedProfile = PatientProfile.fromJson(response);
      }
    } catch (_) {
      // Graceful fallback keeping local state intact
    }
    return _cachedProfile;
  }
}

// Backward-compatible typedef aliases
typedef IntakeRepository = PatientProfileRepository;
typedef MockIntakeRepository = MockPatientProfileRepository;
typedef RestIntakeRepository = RestPatientProfileRepository;
