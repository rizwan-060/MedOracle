import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../features/assessment/screens/assessment_primary_finding_screen.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/signup_screen.dart';
import '../../features/dashboard/screens/home_dashboard_screen.dart';
import '../../features/doctors/screens/doctor_recommendation_screen.dart';
import '../../features/intake/screens/step1_chronic_conditions_and_history_input_screen.dart';
import '../../features/assessment/screens/assessment_ai_reasoning_consensus_screen.dart';
import '../../features/intake/screens/step4_vitals_and_blood_tests_input_screen.dart';
import '../../features/intake/screens/step2_medications_and_family_history_input_screen.dart';
import '../../features/intake/screens/step5_data_review_and_submission_screen.dart';
import '../../features/assessment/screens/assessment_risk_trajectory_forecast_screen.dart';
import '../../features/intake/screens/step3_symptoms_and_severity_input_screen.dart';
import '../../features/simulation/screens/simulate_lifestyle_screen.dart';
import 'route_names.dart';

/// Application router.
///
/// Authentication is the entry point at `/login`, routing forward to
/// `/dashboard`. Both `/` and `/auth` redirect to `/login`, and `/signup`
/// holds the account-creation form.
///
/// Intake wizard:
/// ```text
/// /dashboard         --Start New Assessment-->  /intake/step-1
/// /intake/step-1     --Next-->                 /intake/step-2
/// /intake/step-2     --Next-->                 /intake/step-3
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
    initialLocation: RouteNames.login,
    routes: <RouteBase>[
      // --- Auth -------------------------------------------------------------
      GoRoute(
        path: '/',
        redirect: (BuildContext context, GoRouterState state) =>
            RouteNames.login,
      ),
      GoRoute(
        path: '/auth',
        redirect: (BuildContext context, GoRouterState state) =>
            RouteNames.login,
      ),
      GoRoute(
        path: RouteNames.login,
        builder: (BuildContext context, GoRouterState state) =>
            const LoginScreen(),
      ),
      GoRoute(
        path: RouteNames.signup,
        builder: (BuildContext context, GoRouterState state) =>
            const SignUpScreen(),
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
        path: RouteNames.step1Clinical,
        builder: (BuildContext context, GoRouterState state) =>
            const ClinicalStatusScreen(),
      ),
      GoRoute(
        path: '/intake/step-2a',
        redirect: (BuildContext context, GoRouterState state) =>
            RouteNames.step1Clinical,
      ),
      GoRoute(
        path: RouteNames.step2Medications,
        builder: (BuildContext context, GoRouterState state) =>
            const MedicationsFamilyScreen(),
      ),
      GoRoute(
        path: '/intake/step-2b',
        redirect: (BuildContext context, GoRouterState state) =>
            RouteNames.step2Medications,
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
              onTrajectoryAction: () =>
                  context.push(RouteNames.resultsTrajectory),
              onReasoningAction: () =>
                  context.push(RouteNames.resultsReasoning),
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
