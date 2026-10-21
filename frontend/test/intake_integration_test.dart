import 'package:flutter_test/flutter_test.dart';
import 'package:medoracle/core/constants/api_endpoints.dart';
import 'package:medoracle/data/models/lab_result_model.dart';
import 'package:medoracle/data/models/medical_history_model.dart';
import 'package:medoracle/data/models/patient_profile_model.dart';
import 'package:medoracle/data/models/symptom_model.dart';
import 'package:medoracle/data/repositories/intake_repository.dart';
import 'package:medoracle/data/services/api_service.dart';

void main() {
  group('Backend API & Schema Integration Tests', () {
    test('ApiEndpoints defines valid routes matching FastAPI backend', () {
      expect(ApiEndpoints.baseUrl, contains('/api/v1'));
      expect(ApiEndpoints.patientProfile, equals('/patient/profile'));
      expect(ApiEndpoints.medicalHistory, equals('/medical-history/'));
      expect(ApiEndpoints.symptoms, equals('/symptoms/'));
      expect(ApiEndpoints.laboratory, equals('/laboratory/'));
      expect(ApiEndpoints.laboratoryLatest, equals('/laboratory/latest'));
    });

    test('PatientProfile serializes to backend snake_case format', () {
      final PatientProfile profile = PatientProfile(
        dateOfBirth: DateTime.utc(1980, 5, 20),
        gender: 'Male',
        bloodGroup: 'B+',
        heightCm: 175.5,
        weightKg: 78.0,
        waistCircumferenceCm: 90.0,
        smokingStatus: 'Current',
        activityLevel: 'Moderate',
      );

      final Map<String, dynamic> json = profile.toJson();
      expect(json['date_of_birth'], equals('1980-05-20'));
      expect(json['gender'], equals('male'));
      expect(json['blood_group'], equals('B+'));
      expect(json['smoking_status'], equals('current_smoker'));
      expect(json['activity_level'], equals('moderate'));
      expect(json['height_cm'], equals(175.5));
      expect(json['weight_kg'], equals(78.0));
      expect(json['waist_circumference_cm'], equals(90.0));
    });

    test('PatientProfile correctly parses backend API response payload', () {
      final Map<String, dynamic> backendPayload = <String, dynamic>{
        'date_of_birth': '1975-11-10',
        'gender': 'female',
        'blood_group': 'O+',
        'height_cm': 165.0,
        'weight_kg': 60.0,
        'waist_circumference_cm': 75.0,
        'smoking_status': 'never',
        'activity_level': 'low',
      };

      final PatientProfile profile = PatientProfile.fromJson(backendPayload);
      expect(profile.gender, equals('Female'));
      expect(profile.smokingStatus, equals('Never'));
      expect(profile.activityLevel, equals('Light'));
      expect(profile.dateOfBirth.year, equals(1975));
      expect(profile.dateOfBirth.month, equals(11));
      expect(profile.dateOfBirth.day, equals(10));
    });

    test('MedicalHistoryModel serializes and deserializes accurately', () {
      final MedicalHistoryModel history = MedicalHistoryModel(
        chronicConditions: const <String>['Hypertension'],
        pastSurgeries: const <String>['Appendectomy'],
        allergies: const <String>['Penicillin'],
        currentMedications: const <Map<String, dynamic>>[
          <String, dynamic>{'name': 'Lisinopril', 'dosage': '10mg', 'frequency': 'Daily'},
        ],
        familyHistory: const <Map<String, dynamic>>[
          <String, dynamic>{'relative': 'Father', 'condition': 'CAD', 'age_at_onset': 58},
        ],
        notes: 'Clinical intake verified.',
      );

      final Map<String, dynamic> json = history.toJson();
      expect(json['chronic_conditions'], contains('Hypertension'));
      expect(json['past_surgeries'], contains('Appendectomy'));
      expect(json['allergies'], contains('Penicillin'));
      expect(json['current_medications'], hasLength(1));
      expect(json['notes'], equals('Clinical intake verified.'));

      final MedicalHistoryModel roundtrip = MedicalHistoryModel.fromJson(json);
      expect(roundtrip.chronicConditions, equals(history.chronicConditions));
      expect(roundtrip.notes, equals(history.notes));
    });

    test('SymptomReportModel serializes with min_length protection', () {
      const SymptomReportModel shortTextReport = SymptomReportModel(
        reportedText: 'Pain',
        severitySelfRating: 8,
        durationDays: 4,
        bodyLocations: <String>['Chest'],
        triggers: <String>['Cold air'],
        structuredSymptoms: <String>['Angina'],
      );

      final Map<String, dynamic> json = shortTextReport.toJson();
      expect(json['reported_text'].toString().length, greaterThanOrEqualTo(5));
      expect(json['severity_self_rating'], equals(8));
      expect(json['duration_days'], equals(4));
    });

    test('LabResultModel serializes biomarkers dictionary matching schema', () {
      const LabResultModel lab = LabResultModel(
        testDate: '2026-10-15',
        labName: 'Central Lab',
        biomarkers: <String, dynamic>{
          'systolic_bp': 130.0,
          'diastolic_bp': 85.0,
          'total_cholesterol_mg_dl': 210.0,
          'fasting_blood_glucose_mg_dl': 105.0,
        },
      );

      final Map<String, dynamic> json = lab.toJson();
      expect(json['test_date'], equals('2026-10-15'));
      expect(json['lab_name'], equals('Central Lab'));
      expect(json['biomarkers']['systolic_bp'], equals(130.0));
      expect(json['biomarkers']['total_cholesterol_mg_dl'], equals(210.0));
    });

    test('RestIntakeRepository falls back gracefully on network errors', () async {
      final ApiService apiService = ApiService(baseUrl: 'http://invalid-host:9999/api/v1');
      final RestIntakeRepository repo = RestIntakeRepository(apiService);

      final PatientProfile profile = await repo.fetchProfile();
      expect(profile, isNotNull);
      expect(profile.gender, equals('Male'));
      expect(profile.bloodGroup, equals('A+'));
    });
  });
}
