import '../models/patient_profile_model.dart';

/// Data access contract for the intake (data-entry) flow.
///
/// The UI depends only on this interface; the mock implementation backs the
/// screens during development and a REST implementation can be dropped in
/// later without any widget changes.
abstract class IntakeRepository {
  /// Loads the patient profile for the signed-in user.
  Future<PatientProfile> fetchProfile();

  /// Persists the patient profile (autosave).
  Future<PatientProfile> saveProfile(PatientProfile profile);
}

/// In-memory implementation seeded with the demo patient from the
/// MedOracle v3.1 intake-flow design reference.
class MockIntakeRepository implements IntakeRepository {
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

  /// Simulated network latency so autosave states are observable.
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
