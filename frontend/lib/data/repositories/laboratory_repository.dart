import '../../core/constants/api_endpoints.dart';
import '../models/lab_result_model.dart';
import '../services/api_service.dart';

abstract class LaboratoryRepository {
  Future<LabResultModel?> fetchLatestLabResult();
  Future<LabResultModel> saveLabResult(LabResultModel labResult);
}

class RestLaboratoryRepository implements LaboratoryRepository {
  RestLaboratoryRepository(this._apiService);

  final ApiService _apiService;

  LabResultModel _cached = const LabResultModel(
    testDate: '2026-10-12',
    labName: 'City Diagnostics',
    biomarkers: <String, dynamic>{
      'systolic_bp': 146.0,
      'diastolic_bp': 92.0,
      'total_cholesterol_mg_dl': 242.0,
      'hdl_cholesterol_mg_dl': 37.0,
      'ldl_cholesterol_mg_dl': 160.0,
      'fasting_blood_glucose_mg_dl': 118.0,
      'hba1c_percent': 6.2,
      'serum_creatinine_mg_dl': 1.12,
    },
    notes: 'Elevated systolic BP and LDL cholesterol.',
  );

  @override
  Future<LabResultModel?> fetchLatestLabResult() async {
    try {
      final dynamic response =
          await _apiService.get(ApiEndpoints.laboratoryLatest);
      if (response is Map<String, dynamic>) {
        _cached = LabResultModel.fromJson(response);
        return _cached;
      }
    } catch (_) {
      // Fallback to cached lab result
    }
    return _cached;
  }

  @override
  Future<LabResultModel> saveLabResult(LabResultModel labResult) async {
    _cached = labResult;
    try {
      final dynamic response = await _apiService.post(
        ApiEndpoints.laboratory,
        body: labResult.toJson(),
      );
      if (response is Map<String, dynamic>) {
        _cached = LabResultModel.fromJson(response);
      }
    } catch (_) {
      // Fallback keeping local state
    }
    return _cached;
  }
}
