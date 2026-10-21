/// Model representing laboratory biomarker test reports.
///
/// Mirrors backend `LabResultCreate` and `LabResultResponse`.
class LabResultModel {
  const LabResultModel({
    required this.testDate,
    required this.biomarkers,
    this.labName,
    this.notes,
    this.id,
    this.createdAt,
  });

  final String testDate;
  final Map<String, dynamic> biomarkers;
  final String? labName;
  final String? notes;
  final String? id;
  final DateTime? createdAt;

  Map<String, dynamic> toJson() => <String, dynamic>{
        'test_date': testDate,
        if (labName != null && labName!.isNotEmpty) 'lab_name': labName,
        'biomarkers': biomarkers,
        if (notes != null && notes!.isNotEmpty) 'notes': notes,
      };

  factory LabResultModel.fromJson(Map<String, dynamic> json) {
    return LabResultModel(
      testDate: (json['test_date'] as String?) ??
          DateTime.now().toIso8601String().split('T').first,
      labName: json['lab_name'] as String?,
      biomarkers: (json['biomarkers'] as Map<String, dynamic>?) ??
          const <String, dynamic>{},
      notes: json['notes'] as String?,
      id: json['id'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String)
          : null,
    );
  }
}
