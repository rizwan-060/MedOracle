import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../repositories/laboratory_repository.dart';
import '../repositories/medical_history_repository.dart';
import '../repositories/patient_profile_repository.dart';
import '../repositories/symptoms_repository.dart';
import '../services/api_service.dart';

/// Single source of the patient profile repository for the whole app.
/// Backed by REST and connects to FastAPI backend with in-memory fallback.
final Provider<PatientProfileRepository> patientProfileRepositoryProvider =
    Provider<PatientProfileRepository>((Ref ref) {
  final ApiService apiService = ref.watch(apiServiceProvider);
  return RestPatientProfileRepository(apiService);
});

/// Backward-compatible alias for existing callers.
final Provider<PatientProfileRepository> intakeRepositoryProvider =
    patientProfileRepositoryProvider;

/// Medical and family history repository provider.
final Provider<MedicalHistoryRepository> medicalHistoryRepositoryProvider =
    Provider<MedicalHistoryRepository>((Ref ref) {
  final ApiService apiService = ref.watch(apiServiceProvider);
  return RestMedicalHistoryRepository(apiService);
});

/// Symptom reporting repository provider.
final Provider<SymptomsRepository> symptomsRepositoryProvider =
    Provider<SymptomsRepository>((Ref ref) {
  final ApiService apiService = ref.watch(apiServiceProvider);
  return RestSymptomsRepository(apiService);
});

/// Clinical laboratory & vitals repository provider.
final Provider<LaboratoryRepository> laboratoryRepositoryProvider =
    Provider<LaboratoryRepository>((Ref ref) {
  final ApiService apiService = ref.watch(apiServiceProvider);
  return RestLaboratoryRepository(apiService);
});
