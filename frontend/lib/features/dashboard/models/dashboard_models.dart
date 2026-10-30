/// Domain models rendered by the Home Dashboard.
///
/// The dashboard is the app's hub: it shows who is signed in, the latest risk
/// result and the assessments the user ran recently.
library;

/// Urgency band of the latest risk result.
enum DashboardRiskUrgency { low, moderate, high }

/// Lifecycle of a single "Recent assessments" entry.
enum DashboardAssessmentStatus { completed, inProgress }

/// Destinations exposed by the dashboard bottom navigation bar.
enum DashboardDestination { home, history, doctors, profile }

/// The signed-in user shown in the dashboard header.
class DashboardUser {
  const DashboardUser({required this.firstName});

  /// Name used by the `Hello, <name>` greeting.
  final String firstName;

  /// Greeting rendered next to the avatar.
  String get greeting => 'Hello, $firstName';
}

/// The most recent risk result, rendered by the hero metric card.
class DashboardRiskResult {
  const DashboardRiskResult({
    required this.score,
    required this.condition,
    required this.urgency,
  });

  /// Risk score between 0 and 100.
  final int score;

  /// Condition the score belongs to.
  final String condition;

  /// Urgency band of the score.
  final DashboardRiskUrgency urgency;

  /// Human readable urgency label.
  String get urgencyLabel {
    return switch (urgency) {
      DashboardRiskUrgency.low => 'Low urgency',
      DashboardRiskUrgency.moderate => 'Medium urgency',
      DashboardRiskUrgency.high => 'High urgency',
    };
  }
}

/// A single entry of the "Recent assessments" list.
class DashboardAssessment {
  const DashboardAssessment({
    required this.title,
    required this.date,
    required this.status,
  });

  /// Name of the assessment.
  final String title;

  /// Day the assessment was run.
  final DateTime date;

  /// Lifecycle of the assessment.
  final DashboardAssessmentStatus status;
}
