import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/misc.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/widgets/expandable_section_card.dart';
import '../../../core/widgets/step_scaffold.dart';
import '../../../data/models/patient_profile_model.dart';
import '../../intake/providers/section_accordion_controller.dart';
import '../../intake/providers/section_providers.dart';
import '../providers/profile_controller.dart';
import '../widgets/body_measurements_section.dart';
import '../widgets/lifestyle_section.dart';
import '../widgets/personal_details_section.dart';

/// Section ids used by the Step 1 accordion.
abstract final class _ProfileSection {
  static const String details = 'personal-details';
  static const String body = 'body-measurements';
  static const String lifestyle = 'lifestyle';
}

/// Accordion controller that opens "Personal Details" first.
class _ProfileAccordion extends SectionAccordionController {
  _ProfileAccordion() : super(initialSection: _ProfileSection.details);
}

/// Step 1 of the intake flow - **Profile**.
///
/// Translates the `v8 - Step 1 - Profile` frame of the design reference:
/// three expandable cards (Personal Details, Body Measurements, Lifestyle)
/// with exactly one section open at a time.
class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Screen-scoped accordion so the open section never leaks between steps.
    return ProviderScope(
      overrides: <Override>[
        sectionAccordionProvider.overrideWith(_ProfileAccordion.new),
      ],
      child: const _ProfileView(),
    );
  }
}

class _ProfileView extends ConsumerWidget {
  const _ProfileView();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ProfileState state = ref.watch(profileControllerProvider);
    final String openSection = ref.watch(sectionAccordionProvider);

    // Wrapped in a Scaffold to instantly fix the double yellow line bug
    return Scaffold(
      body: StepScaffold(
        stepNumber: 1,
        totalSteps: 5,
        ctaLabel: 'Next: Clinical Status',
        isSaving: state.isSaving,
        onCta: () => context.go(RouteNames.step2Clinical),
        onBack: () => context.go(RouteNames.dashboard),
        onSaveExit: () => context.go(RouteNames.dashboard),
        child: _ProfileBody(
          state: state,
          openSection: openSection,
          onToggleSection: (String section) =>
              ref.read(sectionAccordionProvider.notifier).toggle(section),
          onProfileChanged: (PatientProfile next) => ref
              .read(profileControllerProvider.notifier)
              .update((PatientProfile _) => next),
        ),
      ),
    );
  }
}

class _ProfileBody extends StatelessWidget {
  const _ProfileBody({
    required this.state,
    required this.openSection,
    required this.onToggleSection,
    required this.onProfileChanged,
  });

  final ProfileState state;
  final String openSection;
  final ValueChanged<String> onToggleSection;
  final ValueChanged<PatientProfile> onProfileChanged;

  @override
  Widget build(BuildContext context) {
    final PatientProfile? profile = state.profile;

    if (profile == null) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 48),
        child: Center(child: CircularProgressIndicator()),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        ExpandableSectionCard(
          title: 'Personal Details',
          isExpanded: openSection == _ProfileSection.details,
          onToggle: () => onToggleSection(_ProfileSection.details),
          child: PersonalDetailsSection(
            profile: profile,
            onDateOfBirthTap: () => _pickDateOfBirth(context, profile),
            onGenderChanged: (String value) =>
                onProfileChanged(profile.copyWith(gender: value)),
            onBloodGroupChanged: (String value) =>
                onProfileChanged(profile.copyWith(bloodGroup: value)),
          ),
        ),
        ExpandableSectionCard(
          title: 'Body Measurements',
          isExpanded: openSection == _ProfileSection.body,
          onToggle: () => onToggleSection(_ProfileSection.body),
          child: BodyMeasurementsSection(
            profile: profile,
            onChanged: onProfileChanged,
          ),
        ),
        ExpandableSectionCard(
          title: 'Lifestyle',
          isExpanded: openSection == _ProfileSection.lifestyle,
          onToggle: () => onToggleSection(_ProfileSection.lifestyle),
          child: LifestyleSection(
            profile: profile,
            onSmokingStatusChanged: (String value) =>
                onProfileChanged(profile.copyWith(smokingStatus: value)),
            onActivityLevelChanged: (String value) =>
                onProfileChanged(profile.copyWith(activityLevel: value)),
          ),
        ),
      ],
    );
  }

  Future<void> _pickDateOfBirth(
    BuildContext context,
    PatientProfile profile,
  ) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: profile.dateOfBirth,
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
      onProfileChanged(profile.copyWith(dateOfBirth: picked));
    }
  }
}