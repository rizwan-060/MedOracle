import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../data/models/patient_profile_model.dart';
import '../../profile/providers/profile_controller.dart';

/// Read-only profile facts summarized on the Review & Confirm step.
///
/// Dynamically reads from [profileControllerProvider] and reflects user inputs.
class ReviewProfileSummary {
  const ReviewProfileSummary({
    this.age = '54 years',
    this.smokingStatus = 'Current smoker',
  });

  final String age;
  final String smokingStatus;
}

final Provider<ReviewProfileSummary> reviewProfileProvider =
    Provider<ReviewProfileSummary>((Ref ref) {
  final ProfileState profileState = ref.watch(profileControllerProvider);
  final PatientProfile? profile = profileState.profile;

  if (profile != null) {
    final String smokingLabel = profile.smokingStatus.toLowerCase() == 'never'
        ? 'Non-smoker'
        : '${profile.smokingStatus} smoker';
    return ReviewProfileSummary(
      age: '${profile.age} years',
      smokingStatus: smokingLabel,
    );
  }

  return const ReviewProfileSummary();
});
