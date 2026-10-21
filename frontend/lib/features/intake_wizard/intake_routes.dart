import '../../core/routing/route_names.dart';

/// Route paths for every step of the intake wizard flow.
///
/// These delegate to the app-level [RouteNames] constants so the router
/// and the screens can never drift apart.
abstract final class IntakeRoutes {
  static const String profile = RouteNames.step1Profile;
  static const String clinicalStatus = RouteNames.step2Clinical;
  static const String medicationsFamily = RouteNames.step2Medications;
  static const String symptoms = RouteNames.step3Symptoms;
  static const String labsVitals = RouteNames.step4Labs;
  static const String review = RouteNames.step5Review;

  /// Post-submission analysis screens (design Step 6A — stacked reports).
  static const String results = RouteNames.resultsReports;

  /// Step 6B — "Where your risk is heading" (risk dial + habit deltas).
  static const String trajectory = RouteNames.resultsTrajectory;

  /// Step 6C — "How Our AI Reached This Result" (visual reasoning map).
  static const String reasoning = RouteNames.resultsReasoning;
}
