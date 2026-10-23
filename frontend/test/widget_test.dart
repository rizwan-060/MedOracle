import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:medoracle/features/auth/screens/auth_screen.dart';
import 'package:medoracle/main.dart';

void main() {
  testWidgets('App smoke test - starts on AuthScreen', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: MedOracleApp()));
    await tester.pumpAndSettle();

    expect(find.byType(AuthScreen), findsOneWidget);
  });
}
