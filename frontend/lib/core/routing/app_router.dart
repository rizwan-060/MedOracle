import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../features/assessment/screens/assessment_main_finding_screen.dart';
import '../../features/auth/screens/auth_screen.dart';
import '../../features/dashboard/screens/home_dashboard_screen.dart';
import '../../features/doctors/screens/doctor_recommendation_screen.dart';
import '../../features/intake_wizard/screens/clinical_status_screen.dart';
import '../../features/intake_wizard/screens/first_assessment_screen.dart';
import '../../features/intake_wizard/screens/labs_vitals_screen.dart';
import '../../features/intake_wizard/screens/medications_family_screen.dart';
import '../../features/intake_wizard/screens/review_confirm_screen.dart';
import '../../features/intake_wizard/screens/risk_trajectory_screen.dart';
import '../../features/intake_wizard/screens/symptoms_screen.dart';
import '../../features/profile/screens/profile_screen.dart';
import '../../features/simulation/screens/simulate_lifestyle_screen.dart';
import 'route_names.dart';

/// Application router.
///
/// Authentication is the entry point at `'/'`, routing forward to `/dashboard`.
///
/// Intake wizard:
/// ```text
/// /dashboard         --Start New Assessment-->  /intake/step-1
/// /intake/step-1     --Next-->                 /intake/step-2a
/// /intake/step-2a    --Next-->                 /intake/step-2b
/// /intake/step-2b    --Next-->                 /intake/step-3
/// /intake/step-3     --Next-->                 /intake/step-4
/// /intake/step-4     --Next-->                 /intake/step-5
/// /intake/step-5     --Submit Assessment-->    /results/reports
/// ```
///
/// Results & exploration:
/// ```text
/// /results/reports   --View trajectory-->      /results/trajectory
/// /results/reports   --AI Reasoning-->         /results/reasoning
/// /results/reports   --Done / Close-->         /dashboard
/// /results/reasoning --Back to results-->      /results/reports
/// /results/reasoning --View trajectory-->      /results/trajectory
/// /results/trajectory--Back to results-->      /results/reports
/// /results/care-finder--Back-->                /results/reports or /dashboard
/// /results/simulate  --Close / Save-->         /dashboard
/// ```
GoRouter createAppRouter() {
  return GoRouter(
    initialLocation: RouteNames.auth,
    routes: <RouteBase>[
      // --- Auth -------------------------------------------------------------
      GoRoute(
        path: RouteNames.auth,
        builder: (BuildContext context, GoRouterState state) =>
            const AuthScreen(),
      ),

      // --- Home Dashboard ---------------------------------------------------
      GoRoute(
        path: RouteNames.dashboard,
        builder: (BuildContext context, GoRouterState state) =>
            const HomeDashboardScreen(),
      ),
      GoRoute(
        path: '/home',
        redirect: (BuildContext context, GoRouterState state) =>
            RouteNames.dashboard,
      ),

      // --- Intake wizard ----------------------------------------------------
      GoRoute(
        path: RouteNames.step1Profile,
        builder: (BuildContext context, GoRouterState state) =>
            const ProfileScreen(),
      ),
      GoRoute(
        path: RouteNames.step2Clinical,
        builder: (BuildContext context, GoRouterState state) =>
            const ClinicalStatusScreen(),
      ),
      GoRoute(
        path: RouteNames.step2Medications,
        builder: (BuildContext context, GoRouterState state) =>
            const MedicationsFamilyScreen(),
      ),
      GoRoute(
        path: RouteNames.step3Symptoms,
        builder: (BuildContext context, GoRouterState state) =>
            const SymptomsScreen(),
      ),
      GoRoute(
        path: RouteNames.step4Labs,
        builder: (BuildContext context, GoRouterState state) =>
            const LabsVitalsScreen(),
      ),
      GoRoute(
        path: RouteNames.step5Review,
        builder: (BuildContext context, GoRouterState state) =>
            const ReviewConfirmScreen(),
      ),

      // --- Results flow -----------------------------------------------------
      GoRoute(
        path: RouteNames.resultsRoot,
        redirect: (BuildContext context, GoRouterState state) =>
            RouteNames.resultsReports,
      ),
      GoRoute(
        path: RouteNames.resultsReports,
        builder: (BuildContext context, GoRouterState state) =>
            AssessmentMainFindingScreen(
          onTrajectoryAction: () => context.push(RouteNames.resultsTrajectory),
          onReasoningAction: () => context.push(RouteNames.resultsReasoning),
          onClose: () => context.go(RouteNames.dashboard),
        ),
      ),
      GoRoute(
        path: RouteNames.resultsReasoning,
        builder: (BuildContext context, GoRouterState state) =>
            FirstAssessmentScreen(
          onPrimaryAction: () => context.push(RouteNames.resultsTrajectory),
          onSecondaryAction: () => context.go(RouteNames.resultsReports),
          onClose: () => context.go(RouteNames.resultsReports),
        ),
      ),
      GoRoute(
        path: RouteNames.resultsTrajectory,
        builder: (BuildContext context, GoRouterState state) =>
            RiskTrajectoryScreen(
          onSecondaryAction: () => context.go(RouteNames.resultsReports),
          onClose: () => context.go(RouteNames.resultsReports),
        ),
      ),
      GoRoute(
        path: RouteNames.resultsCareFinder,
        builder: (BuildContext context, GoRouterState state) =>
            DoctorRecommendationScreen(
          backLabel: context.canPop() ? 'Back' : 'Back to Dashboard',
          onBack: () {
            if (context.canPop()) {
              context.pop();
            } else {
              context.go(RouteNames.dashboard);
            }
          },
        ),
      ),
      GoRoute(
        path: RouteNames.resultsSimulate,
        builder: (BuildContext context, GoRouterState state) =>
            SimulateLifestyleScreen(
          onClose: () => context.go(RouteNames.dashboard),
          onSaveActionPlan: () => context.go(RouteNames.dashboard),
        ),
      ),
    ],
  );
}
