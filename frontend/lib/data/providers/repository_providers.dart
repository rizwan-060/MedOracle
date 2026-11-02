import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../repositories/intake_repository.dart';

/// Single source of the intake repository for the whole app.
///
/// Swap `MockIntakeRepository` for a REST-backed implementation when the
/// backend wiring session happens - no UI code has to change.
final Provider<IntakeRepository> intakeRepositoryProvider =
    Provider<IntakeRepository>((Ref ref) {
  return MockIntakeRepository();
});
