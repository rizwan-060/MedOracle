import 'package:flutter/material.dart';
import 'package:medoracle/core/theme/app_colors.dart';
import 'package:medoracle/core/theme/app_text_styles.dart';
import 'package:medoracle/core/widgets/disclaimer_text.dart';
import 'package:medoracle/core/widgets/glass_pill_button.dart';
import 'package:medoracle/core/widgets/gradient_cta_button.dart';
import 'package:medoracle/data/models/doctor_model.dart';
import 'package:medoracle/features/doctors/widgets/doctor_card.dart';

// Added import for the AssessmentHeader
import 'package:medoracle/features/assessment/widgets/assessment_header.dart';

/// Care finder - specialist recommendations matching the assessment.
///
/// Lists the specialists that match the result and lets the patient book the
/// next appointment.
class DoctorRecommendationScreen extends StatelessWidget {
  const DoctorRecommendationScreen({
    super.key,
    this.onBack,
    this.backLabel = 'Back',
    this.onSelectDoctor,
    this.doctors = demoDoctors,
  });

  /// Leaves the care finder.
  final VoidCallback? onBack;

  /// Label shown on the footer back pill.
  final String backLabel;

  /// Invoked when a specialist is picked.
  final ValueChanged<Doctor>? onSelectDoctor;

  /// Specialists to show.
  final List<Doctor> doctors;

  /// Placeholder list used until the care API is wired up.
  static const List<Doctor> demoDoctors = <Doctor>[
    Doctor(
      name: 'Dr. Amara Osei',
      specialty: 'Cardiologist',
      clinic: 'Northgate Heart Centre',
      distanceKm: 1.4,
      nextAvailable: 'Tomorrow, 09:20',
      experienceYears: 12,
    ),
    Doctor(
      name: 'Dr. Ravi Menon',
      specialty: 'Cardiologist',
      clinic: 'Riverside Cardiology',
      distanceKm: 3.8,
      nextAvailable: 'Thu, 14:40',
      experienceYears: 8,
    ),
    Doctor(
      name: 'Dr. Sofia Lindqvist',
      specialty: 'Preventive cardiology',
      clinic: 'St. Anne Medical Group',
      distanceKm: 5.2,
      nextAvailable: 'Mon, 11:05',
      experienceYears: 15,
    ),
  ];

  void _placeholder(BuildContext context, String destination) {
    debugPrint(
      '[MedOracle] TODO: route to "$destination" from '
      'DoctorRecommendationScreen.',
    );
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('TODO: route to $destination')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.refCanvasBottom,
      body: DecoratedBox(
        decoration: const BoxDecoration(gradient: AppColors.canvasGradient),
        child: SafeArea(
          bottom: false,
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(0, 0, 0, 28),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                AssessmentHeader(
                  onClose: onBack ?? () => _placeholder(context, 'close'),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: <Widget>[
                      const SizedBox(height: 18),
                      const Text('CARE NEAR YOU', style: AppTextStyles.eyebrow),
                      const SizedBox(height: 8),
                      const Text(
                        'Cardiologists near you',
                        style: AppTextStyles.resultsHeadline,
                      ),
                      const SizedBox(height: 10),
                      const Text(
                        'Specialists who can review your result and set up the next '
                        'steps with you.',
                        style: AppTextStyles.resultsBody,
                      ),
                      const SizedBox(height: 22),
                      for (int index = 0; index < doctors.length; index++) ...<Widget>[
                        if (index > 0) const SizedBox(height: 12),
                        DoctorCard(
                          doctor: doctors[index],
                          onTap: () => onSelectDoctor?.call(doctors[index]),
                        ),
                      ],
                      const SizedBox(height: 24),
                      const DisclaimerText(),
                      const SizedBox(height: 16),
                      GradientCtaButton(
                        label: 'Book the earliest slot',
                        onPressed: () => _placeholder(context, 'booking'),
                      ),
                      const SizedBox(height: 10),
                      GlassPillButton.footer(
                        label: backLabel,
                        onTap: onBack ?? () => _placeholder(context, 'back'),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}