import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:medoracle/core/widgets/app_button.dart';
import 'package:medoracle/core/widgets/app_section_card.dart';
import 'package:medoracle/core/widgets/app_text_field.dart';

void main() {
  group('Core Reusable Widgets Tests', () {
    testWidgets('AppTextField renders label, placeholder, and suffix unit', (
      WidgetTester tester,
    ) async {
      String typedValue = '';
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppTextField(
              label: 'Systolic Blood Pressure',
              hintText: 'e.g. 120',
              unit: 'mmHg',
              onChanged: (String val) => typedValue = val,
            ),
          ),
        ),
      );

      expect(find.text('Systolic Blood Pressure'), findsOneWidget);
      expect(find.text('e.g. 120'), findsOneWidget);
      expect(find.text('mmHg'), findsOneWidget);

      await tester.enterText(find.byType(TextField), '125');
      expect(typedValue, equals('125'));
    });

    testWidgets('AppButton renders gradient variant and handles taps', (
      WidgetTester tester,
    ) async {
      bool tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(
              label: 'Confirm Assessment',
              variant: AppButtonVariant.gradient,
              onTap: () => tapped = true,
            ),
          ),
        ),
      );

      expect(find.text('Confirm Assessment'), findsOneWidget);
      await tester.tap(find.text('Confirm Assessment'));
      expect(tapped, isTrue);
    });

    testWidgets('AppButton renders dashed variant for adding records', (
      WidgetTester tester,
    ) async {
      bool tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(
              label: '+ Add Condition',
              variant: AppButtonVariant.dashed,
              onTap: () => tapped = true,
            ),
          ),
        ),
      );

      expect(find.text('+ Add Condition'), findsOneWidget);
      await tester.tap(find.text('+ Add Condition'));
      expect(tapped, isTrue);
    });

    testWidgets('AppSectionCard supports title, trailing action, and accordion toggle', (
      WidgetTester tester,
    ) async {
      bool toggled = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppSectionCard(
              title: 'Lipid Profile',
              trailing: const Icon(Icons.edit, key: Key('edit_icon')),
              onToggle: () => toggled = true,
              isExpanded: true,
              child: const Text('Total Cholesterol: 210 mg/dL'),
            ),
          ),
        ),
      );

      expect(find.text('Lipid Profile'), findsOneWidget);
      expect(find.byKey(const Key('edit_icon')), findsOneWidget);
      expect(find.text('Total Cholesterol: 210 mg/dL'), findsOneWidget);

      await tester.tap(find.text('Lipid Profile'));
      expect(toggled, isTrue);
    });
  });
}
