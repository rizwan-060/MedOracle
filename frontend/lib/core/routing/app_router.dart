import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/intake/screens/pending_step_screen.dart';
import '../../features/intake_wizard/screens/clinical_status_screen.dart';
import '../../features/intake_wizard/screens/labs_vitals_screen.dart';
import '../../features/intake_wizard/screens/medications_family_screen.dart';
import '../../features/intake_wizard/screens/review_confirm_screen.dart';
import '../../features/intake_wizard/screens/symptoms_screen.dart';
import '../../features/profile/screens/profile_screen.dart';
import 'route_names.dart';

/// Riverpod provider exposing the application [GoRouter].
///
/// Reactive and injectable for auth guard redirects and state-driven routing.
final Provider<GoRouter> routerProvider = Provider<GoRouter>((Ref ref) {
  final GoRouter router = createAppRouter();
  ref.onDispose(router.dispose);
  return router;
});

/// Application router.
///
/// The intake flow is a linear 5-step wizard; each step is its own route so the
/// navigation stack survives back/forward gestures and deep links.
GoRouter createAppRouter() {
  return GoRouter(
    initialLocation: RouteNames.step1Profile,
    routes: <RouteBase>[
      GoRoute(
        path: '/',
        redirect: (BuildContext context, GoRouterState state) =>
            RouteNames.step1Profile,
      ),
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
      // Post-submission results flow — placeholder until Step 6A is built.
      GoRoute(
        path: RouteNames.resultsReports,
        builder: (BuildContext context, GoRouterState state) =>
            const PendingStepScreen(
          stepNumber: 6,
          stepTitle: 'Your Reports',
          ctaLabel: 'Reports coming soon',
          nextRoute: null,
        ),
      ),
    ],
  );
}
