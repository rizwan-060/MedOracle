import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../features/intake/screens/pending_step_screen.dart';
import '../../features/profile/screens/profile_screen.dart';
import 'route_names.dart';

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
            const PendingStepScreen(
          stepNumber: 2,
          stepTitle: 'Clinical Status',
          ctaLabel: 'Next: Medications & Family',
          nextRoute: RouteNames.step2Medications,
        ),
      ),
      GoRoute(
        path: RouteNames.step2Medications,
        builder: (BuildContext context, GoRouterState state) =>
            const PendingStepScreen(
          stepNumber: 3,
          stepTitle: 'Medications & Family',
          ctaLabel: 'Next: Symptoms',
          nextRoute: RouteNames.step3Symptoms,
        ),
      ),
      GoRoute(
        path: RouteNames.step3Symptoms,
        builder: (BuildContext context, GoRouterState state) =>
            const PendingStepScreen(
          stepNumber: 3,
          stepTitle: 'Symptoms',
          ctaLabel: 'Next: Labs & Vitals',
          nextRoute: RouteNames.step4Labs,
        ),
      ),
      GoRoute(
        path: RouteNames.step4Labs,
        builder: (BuildContext context, GoRouterState state) =>
            const PendingStepScreen(
          stepNumber: 4,
          stepTitle: 'Labs & Vitals',
          ctaLabel: 'Next: Review & Confirm',
          nextRoute: RouteNames.step5Review,
        ),
      ),
      GoRoute(
        path: RouteNames.step5Review,
        builder: (BuildContext context, GoRouterState state) =>
            const PendingStepScreen(
          stepNumber: 5,
          stepTitle: 'Review & Confirm',
          ctaLabel: 'Submit Assessment',
          nextRoute: null,
        ),
      ),
    ],
  );
}
