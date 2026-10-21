import '../../core/routing/route_names.dart';

/// Legacy alias mapping for the intake wizard routes.
/// Delegates directly to the central [RouteNames] single source of truth.
abstract final class IntakeRoutes {
  static const String profile = RouteNames.profile;
  static const String clinicalStatus = RouteNames.clinicalStatus;
  static const String medicationsFamily = RouteNames.medicationsFamily;
  static const String symptoms = RouteNames.symptoms;
  static const String labsVitals = RouteNames.labsVitals;
  static const String review = RouteNames.review;
  static const String results = RouteNames.results;
  static const String trajectory = RouteNames.trajectory;
  static const String reasoning = RouteNames.reasoning;
}
