import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Read-only profile facts summarized on the Review & Confirm step.
///
/// TODO: replace the default instance with a combiner over the existing
/// profile wizard provider (built in an earlier task) once its field names
/// are wired in — the Review screen only reads this shape.
class ReviewProfileSummary {
  const ReviewProfileSummary({
    this.age = '54 years',
    this.smokingStatus = 'Current smoker',
  });

  final String age;
  final String smokingStatus;
}

final reviewProfileProvider = Provider<ReviewProfileSummary>(
  (Ref ref) => const ReviewProfileSummary(),
);
