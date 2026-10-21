import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../features/doctors/screens/doctor_recommendation_screen.dart';
import '../../features/intake_wizard/screens/clinical_status_screen.dart';
import '../../features/intake_wizard/screens/first_assessment_screen.dart';
import '../../features/intake_wizard/screens/labs_vitals_screen.dart';
import '../../features/intake_wizard/screens/medications_family_screen.dart';
import '../../features/intake_wizard/screens/review_confirm_screen.dart';
import '../../features/intake_wizard/screens/risk_trajectory_screen.dart';
import '../../features/intake_wizard/screens/symptoms_screen.dart';
import '../../features/profile/screens/profile_screen.dart';
import '../../features/risk/screens/risk_analysis_screen.dart';
import 'route_names.dart';

/// Application router.
///
/// The intake flow is a linear 5-step wizard; each step is its own route so the
/// navigation stack survives back/forward gestures and deep links.
///
/// Submitting the wizard hands over to the results flow, which is wired the
/// same way:
///
/// ```text
/// /intake/step-5  --Submit Assessment-->  /results/reports
/// /results/reports --How we reached this result--> /results/reasoning
/// /results/reasoning --View risk trajectory-->    /results/trajectory
/// /results/trajectory --Find a cardiologist-->    /results/care-finder
/// /results/*        --Back to results-->          /results/reports
/// ```
GoRouter createAppRouter() {
  return GoRouter(
    initialLocation: RouteNames.step1Profile,
    routes: <RouteBase>[
      GoRoute(
        path: '/',
        redirect: (BuildContext context, GoRouterState state) =>
            RouteNames.step1Profile,
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
            RiskAnalysisScreen(
          onReasoningAction: () => context.push(RouteNames.resultsReasoning),
          onTrajectoryAction: () => context.push(RouteNames.resultsTrajectory),
          onClose: () => context.go(RouteNames.step5Review),
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
          onPrimaryAction: () => context.push(RouteNames.resultsCareFinder),
          onSecondaryAction: () => context.go(RouteNames.resultsReports),
          onClose: () => context.go(RouteNames.resultsReports),
        ),
      ),
      GoRoute(
        path: RouteNames.resultsCareFinder,
        builder: (BuildContext context, GoRouterState state) =>
            DoctorRecommendationScreen(
          onBack: () => context.go(RouteNames.resultsTrajectory),
        ),
      ),
    ],
  );
}
