import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/assessment/screens/clinical_status_screen.dart';
import '../../features/assessment/screens/labs_vitals_screen.dart';
import '../../features/assessment/screens/medications_family_screen.dart';
import '../../features/assessment/screens/review_confirm_screen.dart';
import '../../features/assessment/screens/symptoms_screen.dart';
import '../../features/profile/screens/profile_screen.dart';
import '../widgets/pending_step_screen.dart';
import 'route_names.dart';

/// Riverpod provider exposing the application [GoRouter].
///
/// Reactive and injectable for auth guard redirects and state-driven routing.
final Provider<GoRouter> routerProvider = Provider<GoRouter>((Ref ref) {
  final GoRouter router = createAppRouter();
  ref.onDispose(router.dispose);
  return router;
});

/// Application router configuring the patient clinical assessment navigation graph.
GoRouter createAppRouter() {
  return GoRouter(
    initialLocation: RouteNames.patientProfile,
    routes: <RouteBase>[
      GoRoute(
        path: '/',
        redirect: (BuildContext context, GoRouterState state) =>
            RouteNames.patientProfile,
      ),
      GoRoute(
        path: RouteNames.patientProfile,
        builder: (BuildContext context, GoRouterState state) =>
            const ProfileScreen(),
      ),
      GoRoute(
        path: RouteNames.clinicalStatus,
        builder: (BuildContext context, GoRouterState state) =>
            const ClinicalStatusScreen(),
      ),
      GoRoute(
        path: RouteNames.medicationsFamily,
        builder: (BuildContext context, GoRouterState state) =>
            const MedicationsFamilyScreen(),
      ),
      GoRoute(
        path: RouteNames.symptoms,
        builder: (BuildContext context, GoRouterState state) =>
            const SymptomsScreen(),
      ),
      GoRoute(
        path: RouteNames.laboratoryVitals,
        builder: (BuildContext context, GoRouterState state) =>
            const LabsVitalsScreen(),
      ),
      GoRoute(
        path: RouteNames.assessmentReview,
        builder: (BuildContext context, GoRouterState state) =>
            const ReviewConfirmScreen(),
      ),
      // Post-submission results flow — clinical report view placeholder
      GoRoute(
        path: RouteNames.assessmentReports,
        builder: (BuildContext context, GoRouterState state) =>
            const PendingStepScreen(
          stepNumber: 6,
          stepTitle: 'Clinical Reports',
          ctaLabel: 'Reports coming soon',
          nextRoute: null,
        ),
      ),
    ],
  );
}
