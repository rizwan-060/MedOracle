import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../data/models/patient_profile_model.dart';
import '../../../data/providers/repository_providers.dart';

/// State of the Step 1 (Profile) screen.
class ProfileState {
  const ProfileState({
    this.profile,
    this.isSaving = false,
    this.lastSavedAt,
    this.error,
  });

  /// Loaded profile, or `null` while the initial fetch is in flight.
  final PatientProfile? profile;

  /// True while an autosave round-trip is running.
  final bool isSaving;

  /// Timestamp of the last successful save (drives the "Autosaved" badge).
  final DateTime? lastSavedAt;

  /// Message of the most recent failure, if any.
  final String? error;

  bool get isLoading => profile == null && error == null;

  ProfileState copyWith({
    PatientProfile? profile,
    bool? isSaving,
    DateTime? lastSavedAt,
    String? error,
    bool clearError = false,
  }) {
    return ProfileState(
      profile: profile ?? this.profile,
      isSaving: isSaving ?? this.isSaving,
      lastSavedAt: lastSavedAt ?? this.lastSavedAt,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

/// Controller backing the Step 1 screen: loads the profile and autosaves
/// every edit made by the user.
class ProfileController extends Notifier<ProfileState> {
  @override
  ProfileState build() {
    Future<void>.microtask(_load);
    return const ProfileState();
  }

  Future<void> _load() async {
    try {
      final PatientProfile profile =
          await ref.read(patientProfileRepositoryProvider).fetchProfile();
      state = state.copyWith(profile: profile, clearError: true);
    } on Object catch (error) {
      state = state.copyWith(error: error.toString());
    }
  }

  /// Updates a single field and schedules an autosave.
  Future<void> update(PatientProfile Function(PatientProfile) mutate) async {
    final PatientProfile? current = state.profile;
    if (current == null) {
      return;
    }

    final PatientProfile next = mutate(current);
    if (next == current) {
      return;
    }

    state = state.copyWith(profile: next, isSaving: true, clearError: true);

    try {
      final PatientProfile saved =
          await ref.read(patientProfileRepositoryProvider).saveProfile(next);
      state = state.copyWith(
        profile: saved,
        isSaving: false,
        lastSavedAt: DateTime.now(),
      );
    } on Object catch (error) {
      state = state.copyWith(isSaving: false, error: error.toString());
    }
  }
}

/// Provider for the Step 1 profile state.
///
/// Kept at file scope and screen-scoped through the screen's own
/// [ProviderScope] override so re-entering the step reloads fresh data.
final NotifierProvider<ProfileController, ProfileState>
    profileControllerProvider =
    NotifierProvider<ProfileController, ProfileState>(ProfileController.new);
