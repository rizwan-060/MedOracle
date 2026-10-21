/// Structured model representing longitudinal medical and family history.
///
/// Mirrors the backend Pydantic schema `MedicalHistoryResponse` & `MedicalHistoryUpdate`.
class MedicalHistoryModel {
  const MedicalHistoryModel({
    this.chronicConditions = const <String>[],
    this.pastSurgeries = const <String>[],
    this.allergies = const <String>[],
    this.currentMedications = const <Map<String, dynamic>>[],
    this.familyHistory = const <Map<String, dynamic>>[],
    this.notes,
  });

  final List<String> chronicConditions;
  final List<String> pastSurgeries;
  final List<String> allergies;
  final List<Map<String, dynamic>> currentMedications;
  final List<Map<String, dynamic>> familyHistory;
  final String? notes;

  Map<String, dynamic> toJson() => <String, dynamic>{
        'chronic_conditions': chronicConditions,
        'past_surgeries': pastSurgeries,
        'allergies': allergies,
        'current_medications': currentMedications,
        'family_history': familyHistory,
        if (notes != null && notes!.isNotEmpty) 'notes': notes,
      };

  factory MedicalHistoryModel.fromJson(Map<String, dynamic> json) {
    return MedicalHistoryModel(
      chronicConditions: (json['chronic_conditions'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          const <String>[],
      pastSurgeries: (json['past_surgeries'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          const <String>[],
      allergies: (json['allergies'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          const <String>[],
      currentMedications: (json['current_medications'] as List<dynamic>?)
              ?.map((e) => Map<String, dynamic>.from(e as Map))
              .toList() ??
          const <Map<String, dynamic>>[],
      familyHistory: (json['family_history'] as List<dynamic>?)
              ?.map((e) => Map<String, dynamic>.from(e as Map))
              .toList() ??
          const <Map<String, dynamic>>[],
      notes: json['notes'] as String?,
    );
  }
}
