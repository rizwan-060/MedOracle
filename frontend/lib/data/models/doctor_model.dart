/// A specialist that the results flow can point the patient to.
///
/// Field names mirror the backend `doctors` schema so the mock repository can
/// be swapped for the live API without touching the UI.
class Doctor {
  const Doctor({
    required this.name,
    required this.specialty,
    required this.clinic,
    required this.distanceKm,
    required this.nextAvailable,
    this.experienceYears = 0,
  });

  /// Full name of the specialist.
  final String name;

  /// Specialty, e.g. `Cardiologist`.
  final String specialty;

  /// Clinic or hospital the specialist works at.
  final String clinic;

  /// Distance from the patient in kilometres.
  final double distanceKm;

  /// Earliest appointment slot, formatted for display.
  final String nextAvailable;

  /// Years of clinical experience.
  final int experienceYears;

  /// Distance formatted for display, e.g. `1.4 km away`.
  String get distanceLabel {
    final String value = distanceKm.toStringAsFixed(1);
    return '$value km away';
  }
}
