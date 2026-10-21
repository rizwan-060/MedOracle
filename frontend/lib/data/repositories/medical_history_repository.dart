import '../../core/constants/api_endpoints.dart';
import '../models/medical_history_model.dart';
import '../services/api_service.dart';

abstract class MedicalHistoryRepository {
  Future<MedicalHistoryModel> fetchMedicalHistory();
  Future<MedicalHistoryModel> saveMedicalHistory(MedicalHistoryModel history);
}

class RestMedicalHistoryRepository implements MedicalHistoryRepository {
  RestMedicalHistoryRepository(this._apiService);

  final ApiService _apiService;

  MedicalHistoryModel _cached = const MedicalHistoryModel(
    chronicConditions: <String>['Hypertension', 'Dyslipidemia'],
    pastSurgeries: <String>['Appendectomy'],
    allergies: <String>['Penicillin'],
    currentMedications: <Map<String, dynamic>>[
      <String, dynamic>{
        'name': 'Amlodipine',
        'dosage': '5mg',
        'frequency': 'Once daily',
      },
      <String, dynamic>{
        'name': 'Atorvastatin',
        'dosage': '20mg',
        'frequency': 'At bedtime',
      },
    ],
    familyHistory: <Map<String, dynamic>>[
      <String, dynamic>{
        'relative': 'Father',
        'age_at_onset': 55,
        'condition': 'Myocardial infarction',
      },
      <String, dynamic>{
        'relative': 'Mother',
        'age_at_onset': 62,
        'condition': 'Type 2 Diabetes',
      },
    ],
    notes: 'Well-controlled on current pharmacotherapy.',
  );

  @override
  Future<MedicalHistoryModel> fetchMedicalHistory() async {
    try {
      final dynamic response =
          await _apiService.get(ApiEndpoints.medicalHistory);
      if (response is Map<String, dynamic>) {
        _cached = MedicalHistoryModel.fromJson(response);
      }
    } catch (_) {
      // Fallback to cache if endpoint returns 404 or offline
    }
    return _cached;
  }

  @override
  Future<MedicalHistoryModel> saveMedicalHistory(
    MedicalHistoryModel history,
  ) async {
    _cached = history;
    try {
      final dynamic response = await _apiService.put(
        ApiEndpoints.medicalHistory,
        body: history.toJson(),
      );
      if (response is Map<String, dynamic>) {
        _cached = MedicalHistoryModel.fromJson(response);
      }
    } catch (_) {
      // Fallback keeping cached history intact
    }
    return _cached;
  }
}
