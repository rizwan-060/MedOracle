/// Patient profile captured by Step 1 of the intake flow.
///
/// Field names and JSON keys mirror the backend `patient_profiles` schema so
/// the mock repository can be swapped for the live API without touching UI.
class PatientProfile {
  const PatientProfile({
    required this.dateOfBirth,
    required this.gender,
    required this.bloodGroup,
    required this.heightCm,
    required this.weightKg,
    required this.waistCircumferenceCm,
    required this.smokingStatus,
    required this.activityLevel,
  });

  final DateTime dateOfBirth;
  final String gender;
  final String bloodGroup;
  final double heightCm;
  final double weightKg;
  final double waistCircumferenceCm;
  final String smokingStatus;
  final String activityLevel;

  // ---------------------------------------------------------------------------
  // Option lists (step 1 select controls)
  // ---------------------------------------------------------------------------

  static const List<String> genderOptions = <String>['Male', 'Female', 'Other'];

  static const List<String> bloodGroupOptions = <String>[
    'A+',
    'A-',
    'B+',
    'B-',
    'AB+',
    'AB-',
    'O+',
    'O-',
  ];

  static const List<String> smokingStatusOptions = <String>[
    'Never',
    'Former',
    'Current',
  ];

  static const List<String> activityLevelOptions = <String>[
    'Sedentary',
    'Light',
    'Moderate',
    'Active',
    'Very Active',
  ];

  // ---------------------------------------------------------------------------
  // Derived values
  // ---------------------------------------------------------------------------

  /// Age in whole years, derived from the date of birth.
  int get age {
    final DateTime today = DateTime.now();
    int age = today.year - dateOfBirth.year;
    if (today.month < dateOfBirth.month ||
        (today.month == dateOfBirth.month && today.day < dateOfBirth.day)) {
      age -= 1;
    }
    return age;
  }

  /// Body-mass index derived from height and weight.
  double get bmi {
    final double metres = heightCm / 100;
    if (metres <= 0) {
      return 0;
    }
    return weightKg / (metres * metres);
  }

  /// Date of birth rendered like the reference (`15 Mar 1972`).
  String get formattedDateOfBirth {
    const List<String> months = <String>[
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ];
    return '${dateOfBirth.day} ${months[dateOfBirth.month - 1]} '
        '${dateOfBirth.year}';
  }

  // ---------------------------------------------------------------------------
  // Equality / copying
  // ---------------------------------------------------------------------------

  PatientProfile copyWith({
    DateTime? dateOfBirth,
    String? gender,
    String? bloodGroup,
    double? heightCm,
    double? weightKg,
    double? waistCircumferenceCm,
    String? smokingStatus,
    String? activityLevel,
  }) {
    return PatientProfile(
      dateOfBirth: dateOfBirth ?? this.dateOfBirth,
      gender: gender ?? this.gender,
      bloodGroup: bloodGroup ?? this.bloodGroup,
      heightCm: heightCm ?? this.heightCm,
      weightKg: weightKg ?? this.weightKg,
      waistCircumferenceCm:
          waistCircumferenceCm ?? this.waistCircumferenceCm,
      smokingStatus: smokingStatus ?? this.smokingStatus,
      activityLevel: activityLevel ?? this.activityLevel,
    );
  }

  Map<String, dynamic> toJson() => <String, dynamic>{
        'date_of_birth': dateOfBirth.toIso8601String(),
        'gender': gender,
        'blood_group': bloodGroup,
        'height_cm': heightCm,
        'weight_kg': weightKg,
        'waist_circumference_cm': waistCircumferenceCm,
        'smoking_status': smokingStatus,
        'activity_level': activityLevel,
      };

  factory PatientProfile.fromJson(Map<String, dynamic> json) {
    return PatientProfile(
      dateOfBirth: DateTime.parse(json['date_of_birth'] as String),
      gender: json['gender'] as String,
      bloodGroup: json['blood_group'] as String,
      heightCm: (json['height_cm'] as num).toDouble(),
      weightKg: (json['weight_kg'] as num).toDouble(),
      waistCircumferenceCm:
          (json['waist_circumference_cm'] as num).toDouble(),
      smokingStatus: json['smoking_status'] as String,
      activityLevel: json['activity_level'] as String,
    );
  }

  @override
  bool operator ==(Object other) =>
      other is PatientProfile &&
      other.dateOfBirth == dateOfBirth &&
      other.gender == gender &&
      other.bloodGroup == bloodGroup &&
      other.heightCm == heightCm &&
      other.weightKg == weightKg &&
      other.waistCircumferenceCm == waistCircumferenceCm &&
      other.smokingStatus == smokingStatus &&
      other.activityLevel == activityLevel;

  @override
  int get hashCode => Object.hash(
        dateOfBirth,
        gender,
        bloodGroup,
        heightCm,
        weightKg,
        waistCircumferenceCm,
        smokingStatus,
        activityLevel,
      );
}
