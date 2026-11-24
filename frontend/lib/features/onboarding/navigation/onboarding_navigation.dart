import 'package:go_router/go_router.dart';
import 'package:material_ui/material_ui.dart';

/// Small navigation helper shared by the onboarding steps.
///
/// Forward steps are pushed so the platform back button walks back through the
/// wizard. Deep links fall back to `go` when there is no onboarding stack.
abstract final class OnboardingNavigation {
  static void next(BuildContext context, String route) {
    if (context.canPop()) {
      context.push(route);
    } else {
      context.go(route);
    }
  }

  static void back(BuildContext context, String route) {
    if (context.canPop()) {
      context.pop();
    } else {
      context.go(route);
    }
  }
}
