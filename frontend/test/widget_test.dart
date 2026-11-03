import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:medoracle/features/auth/screens/login_screen.dart';
import 'package:medoracle/features/auth/screens/signup_screen.dart';
import 'package:medoracle/main.dart';

void main() {
  testWidgets('App starts on the login screen', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: MedOracleApp()));
    await tester.pumpAndSettle();

    expect(find.byType(LoginScreen), findsOneWidget);
  });

  testWidgets('Login requires an email and password', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const ProviderScope(child: MedOracleApp()));
    await tester.pumpAndSettle();

    await tester.ensureVisible(find.text('Log In'));
    await tester.tap(find.text('Log In'));
    await tester.pumpAndSettle();

    expect(find.text('Required'), findsNWidgets(2));
    expect(find.byType(LoginScreen), findsOneWidget);
  });

  testWidgets('Sign Up link opens the sign-up screen and back returns', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const ProviderScope(child: MedOracleApp()));
    await tester.pumpAndSettle();

    await tester.ensureVisible(find.text('Sign Up'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Sign Up'));
    await tester.pumpAndSettle();

    expect(find.byType(SignUpScreen), findsOneWidget);

    await tester.tap(find.text('Back to login'));
    await tester.pumpAndSettle();

    expect(find.byType(LoginScreen), findsOneWidget);
  });
}
