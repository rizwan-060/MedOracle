/// Model representing patient symptom reports submitted during intake.
///
/// Mirrors backend `SymptomReportCreate` and `SymptomReportResponse`.
class SymptomReportModel {
  const SymptomReportModel({
    required this.reportedText,
    this.severitySelfRating,
    this.durationDays,
    this.bodyLocations = const <String>[],
    this.triggers = const <String>[],
    this.structuredSymptoms = const <String>[],
    this.id,
    this.createdAt,
  });

  final String reportedText;
  final int? severitySelfRating;
  final int? durationDays;
  final List<String> bodyLocations;
  final List<String> triggers;
  final List<String> structuredSymptoms;
  final String? id;
  final DateTime? createdAt;

  Map<String, dynamic> toJson() => <String, dynamic>{
        'reported_text': reportedText.length >= 5
            ? reportedText
            : '$reportedText (reported during intake assessment)',
        if (severitySelfRating != null)
          'severity_self_rating': severitySelfRating,
        if (durationDays != null) 'duration_days': durationDays,
        'body_locations': bodyLocations,
        'triggers': triggers,
        'structured_symptoms': structuredSymptoms,
      };

  factory SymptomReportModel.fromJson(Map<String, dynamic> json) {
    return SymptomReportModel(
      reportedText: (json['reported_text'] as String?) ?? '',
      severitySelfRating: json['severity_self_rating'] as int?,
      durationDays: json['duration_days'] as int?,
      bodyLocations: (json['body_locations'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          const <String>[],
      triggers: (json['triggers'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          const <String>[],
      structuredSymptoms: (json['structured_symptoms'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          const <String>[],
      id: json['id'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String)
          : null,
    );
  }
}
