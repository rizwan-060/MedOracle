import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/dashboard_models.dart';

/// The signed-in user.
///
/// Swap this provider for the real auth/session provider once the backend
/// session is wired up - the dashboard only reads [DashboardUser.firstName].
final dashboardUserProvider = Provider<DashboardUser>(
  (Ref ref) => const DashboardUser(firstName: 'Hafsa'),
);

/// The latest risk result shown in the hero metric card.
///
/// Replace the body with a read of the persisted assessment history so the
/// card reflects the most recent run instead of a seeded value.
final latestRiskResultProvider = Provider<DashboardRiskResult>(
  (Ref ref) => const DashboardRiskResult(
    score: 24,
    condition: 'Coronary Artery Disease Risk',
    urgency: DashboardRiskUrgency.high,
  ),
);

/// Assessments the user ran recently, newest first.
final recentAssessmentsProvider = Provider<List<DashboardAssessment>>(
  (Ref ref) => <DashboardAssessment>[
    DashboardAssessment(
      title: 'Type 2 Diabetes Check',
      date: DateTime(2026, 10, 15),
      status: DashboardAssessmentStatus.completed,
    ),
    DashboardAssessment(
      title: 'General Wellness',
      date: DateTime(2026, 9, 22),
      status: DashboardAssessmentStatus.completed,
    ),
  ],
);

/// Unread flag backing the notification bell badge.
///
/// Tapping the bell marks every notification as read.
class DashboardNotificationBadge extends Notifier<bool> {
  @override
  bool build() => true;

  /// Clears the unread badge.
  void markAllRead() => state = false;
}

/// Provider of the [DashboardNotificationBadge] notifier.
final dashboardNotificationBadgeProvider =
    NotifierProvider<DashboardNotificationBadge, bool>(
      DashboardNotificationBadge.new,
    );
