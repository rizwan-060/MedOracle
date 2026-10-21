import '../../core/constants/api_endpoints.dart';
import '../models/symptom_model.dart';
import '../services/api_service.dart';

abstract class SymptomsRepository {
  Future<SymptomReportModel> submitSymptoms(SymptomReportModel report);
  Future<List<SymptomReportModel>> fetchSymptoms();
}

class RestSymptomsRepository implements SymptomsRepository {
  RestSymptomsRepository(this._apiService);

  final ApiService _apiService;

  final List<SymptomReportModel> _cachedReports = <SymptomReportModel>[
    const SymptomReportModel(
      reportedText:
          'Chest tightness when climbing stairs, easing after a few minutes of rest.',
      severitySelfRating: 7,
      durationDays: 3,
      bodyLocations: <String>['Chest'],
      triggers: <String>['Physical Exertion'],
      structuredSymptoms: <String>['Chest Pain', 'Shortness of Breath'],
    ),
  ];

  @override
  Future<SymptomReportModel> submitSymptoms(SymptomReportModel report) async {
    _cachedReports.insert(0, report);
    try {
      final dynamic response = await _apiService.post(
        ApiEndpoints.symptoms,
        body: report.toJson(),
      );
      if (response is Map<String, dynamic>) {
        return SymptomReportModel.fromJson(response);
      }
    } catch (_) {
      // Fallback keeping local state
    }
    return report;
  }

  @override
  Future<List<SymptomReportModel>> fetchSymptoms() async {
    try {
      final dynamic response = await _apiService.get(ApiEndpoints.symptoms);
      if (response is List) {
        return response
            .map((e) => SymptomReportModel.fromJson(e as Map<String, dynamic>))
            .toList();
      }
    } catch (_) {
      // Fallback to cached reports
    }
    return _cachedReports;
  }
}
