import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../../simulation/models/simulation_models.dart';
import '../../simulation/providers/simulation_providers.dart';
import '../models/dashboard_models.dart';
import '../providers/dashboard_providers.dart';
import '../widgets/dashboard_bottom_nav.dart';
import '../widgets/dashboard_header_bar.dart';
import '../widgets/dashboard_icons.dart';
import '../widgets/dashboard_metric_cards.dart';
import '../widgets/dashboard_recent_activity.dart';
import '../widgets/dashboard_section_header.dart';

/// Home dashboard - the hub of the MedOracle app.
///
/// The dashboard is where a user starts a new intake, reopens a previous
/// assessment and jumps back into the results flow. Every action is wired
/// through `go_router`:
///
/// ```text
/// /dashboard --Start New Assessment--> /intake/step-1   (Profile)
/// /dashboard --View Full Report------> /results/reports
/// /dashboard --Find Specialists------> /results/care-finder
/// /dashboard --Simulate Lifestyle----> /results/simulate
/// ```
class HomeDashboardScreen extends ConsumerWidget {
  const HomeDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final DashboardUser user = ref.watch(dashboardUserProvider);
    final DashboardRiskResult result = ref.watch(latestRiskResultProvider);
    final List<DashboardAssessment> assessments =
        ref.watch(recentAssessmentsProvider);
    final bool hasUnreadNotifications =
        ref.watch(dashboardNotificationBadgeProvider);

    // Confirms an action plan saved from the lifestyle simulation. The plan is
    // consumed straight away so the confirmation is only shown once.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!context.mounted) {
        return;
      }
      final SavedActionPlan? plan = ref.read(savedActionPlanProvider);
      if (plan == null) {
        return;
      }
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          SnackBar(
            content: Text(plan.headline),
            behavior: SnackBarBehavior.floating,
          ),
        );
      ref.read(savedActionPlanProvider.notifier).take();
    });

    return Scaffold(
      backgroundColor: AppColors.canvasBackground,
      body: Container(
        decoration: const BoxDecoration(gradient: AppColors.canvasGradient),
        child: Stack(
          children: <Widget>[
            Positioned.fill(
              child: SafeArea(
                top: true,
                bottom: false,
                child: SingleChildScrollView(
                  padding: const EdgeInsets.only(
                    left: 20,
                    right: 20,
                    bottom: 120,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: <Widget>[
                      DashboardHeaderBar(
                        greeting: user.greeting,
                        hasUnreadNotifications: hasUnreadNotifications,
                        onNotificationsTap: () => ref
                            .read(dashboardNotificationBadgeProvider.notifier)
                            .markAllRead(),
                      ),
                      DashboardHeroMetricCard(
                        result: result,
                        onViewReport: () => _openResults(context),
                      ),
                      const SizedBox(height: 24.0),
                      const DashboardSectionHeader(title: 'Quick actions'),
                      DashboardPrimaryActionCard(
                        icon: DashboardIconType.assessment,
                        title: 'Start New Assessment',
                        subtitle: 'Begin a new health check',
                        onTap: () => _startNewAssessment(context),
                      ),
                      const SizedBox(height: 16.0),
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: <Widget>[
                          Expanded(
                            child: DashboardCompactActionCard(
                              icon: DashboardIconType.lifestyle,
                              title: 'Simulate Lifestyle',
                              subtitle: 'See how habits lower risk',
                              onTap: () => _openSimulation(context),
                            ),
                          ),
                          const SizedBox(width: 16.0),
                          Expanded(
                            child: DashboardCompactActionCard(
                              icon: DashboardIconType.specialist,
                              title: 'Find Specialists',
                              subtitle: 'Match with the right doctor',
                              onTap: () => _openCareFinder(context),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 24.0),
                      DashboardSectionHeader(
                        title: 'Recent assessments',
                        actionLabel: 'See all',
                        onAction: () => _showUnavailable(
                          context,
                          'The full assessment history is not available yet.',
                        ),
                      ),
                      DashboardRecentActivity(
                        assessments: assessments,
                        onItemTap: (DashboardAssessment _) =>
                            _openResults(context),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: DashboardBottomNavBar(
                selected: DashboardDestination.home,
                onSelected: (DashboardDestination destination) =>
                    _onDestinationSelected(context, destination),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Primary call to action: begins a new intake at Step 1 (Profile).
  void _startNewAssessment(BuildContext context) {
    context.go(RouteNames.step1Profile);
  }

  /// Opens the results hub with the latest report.
  void _openResults(BuildContext context) {
    context.go(RouteNames.resultsReports);
  }

  /// Opens the care finder with the specialists near the user.
  void _openCareFinder(BuildContext context) {
    context.push(RouteNames.resultsCareFinder);
  }

  /// Opens the lifestyle simulation.
  void _openSimulation(BuildContext context) {
    context.push(RouteNames.resultsSimulate);
  }

  /// Routes a bottom navigation tap to the matching destination.
  void _onDestinationSelected(
    BuildContext context,
    DashboardDestination destination,
  ) {
    switch (destination) {
      case DashboardDestination.home:
        context.go(RouteNames.dashboard);
      case DashboardDestination.history:
        _showUnavailable(context, 'The assessment history is not available yet.');
      case DashboardDestination.doctors:
        _openCareFinder(context);
      case DashboardDestination.profile:
        _startNewAssessment(context);
    }
  }

  /// Shows a short notice for destinations that are not built yet.
  void _showUnavailable(BuildContext context, String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(message),
          behavior: SnackBarBehavior.floating,
        ),
      );
  }
}
