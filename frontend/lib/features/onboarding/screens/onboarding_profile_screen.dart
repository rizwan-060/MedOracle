import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:material_ui/material_ui.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../navigation/onboarding_navigation.dart';
import '../providers/onboarding_provider.dart';
import '../widgets/onboarding_shell.dart';
import '../widgets/onboarding_type.dart';

/// Onboarding 3 — Let's start with you.
///
/// Age, sex and blood type are collected one question at a time. Completed
/// answers become editable sticky notes.
class OnboardingProfileScreen extends ConsumerWidget {
  const OnboardingProfileScreen({super.key});

  static const String routePath = RouteNames.onboardingProfile;

  static const List<String> _titles = <String>[
    'How old are you?',
    'What is your sex?',
    'Blood type',
    'Your notes are ready',
  ];
  static const List<String> _hints = <String>[
    'Your age helps us read your results correctly.',
    'Some health checks differ by sex. Choose what fits you best.',
    'Select your blood group if you know it.',
    'Tap any note above if you want to change it.',
  ];
  static const List<String> _bloodTypes = <String>[
    'A+',
    'A-',
    'B+',
    'B-',
    'AB+',
    'AB-',
    'O+',
    'O-',
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final OnboardingState state = ref.watch(onboardingProvider);
    final OnboardingController controller =
        ref.read(onboardingProvider.notifier);

    final bool finished = state.profileStep == 3;
    final String ctaLabel;
    final VoidCallback? onCta;
    final bool ctaEnabled;

    if (finished) {
      ctaLabel = 'Add my body details';
      onCta = () => OnboardingNavigation.next(
        context,
        RouteNames.onboardingBody,
      );
      ctaEnabled = true;
    } else {
      ctaLabel = switch (state.profileStep) {
        0 => 'Add my age',
        1 => 'Add my sex',
        _ => state.bloodType == null ? 'Skip for now' : 'Add blood type',
      };
      onCta = controller.commitProfile;
      ctaEnabled = state.profileStep != 1 || state.sex != null;
    }

    return OnboardingShell(
      step: 3,
      title: "Let's start with you",
      subtitle: 'One quick question at a time.',
      ctaLabel: ctaLabel,
      ctaEnabled: ctaEnabled,
      onCta: onCta,
      onBack: () => OnboardingNavigation.back(
        context,
        RouteNames.onboardingCareTeam,
      ),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            const SizedBox(height: 16),
            _NotesBoard(state: state, onEdit: controller.editProfile),
            const SizedBox(height: 24),
            AnimatedSwitcher(
              duration: const Duration(milliseconds: 400),
              child: _QuestionCard(
                key: ValueKey<int>(state.profileStep),
                state: state,
                controller: controller,
                title: _titles[state.profileStep],
                hint: _hints[state.profileStep],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _NotesBoard extends StatelessWidget {
  const _NotesBoard({required this.state, required this.onEdit});

  final OnboardingState state;
  final ValueChanged<String> onEdit;

  @override
  Widget build(BuildContext context) {
    final List<Widget> notes = <Widget>[
      _NoteCard(
        label: 'Age',
        value: '${state.age}',
        filled: state.profileDone['age'] ?? false,
        tint: AppColors.pastelMist,
        rotation: -1.4,
        onTap: () => onEdit('age'),
      ),
      _NoteCard(
        label: 'Sex',
        value: state.sex ?? '',
        filled: state.profileDone['sex'] ?? false,
        tint: AppColors.pastelSage,
        rotation: 1.2,
        onTap: () => onEdit('sex'),
      ),
      _NoteCard(
        label: 'Blood type',
        value: state.bloodType == 'skip' ? 'Skipped' : (state.bloodType ?? ''),
        filled: state.profileDone['blood'] ?? false,
        tint: AppColors.pastelSand,
        rotation: -0.9,
        onTap: () => onEdit('blood'),
      ),
    ];

    if (state.profileStep == 3) {
      return Column(
        children: <Widget>[
          for (final Widget note in notes) ...<Widget>[note, const SizedBox(height: 16)],
        ],
      );
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        for (final Widget note in notes) ...<Widget>[note, const SizedBox(width: 12)],
      ],
    );
  }
}

class _NoteCard extends StatelessWidget {
  const _NoteCard({
    required this.label,
    required this.value,
    required this.filled,
    required this.tint,
    required this.rotation,
    required this.onTap,
  });

  final String label;
  final String value;
  final bool filled;
  final Color tint;
  final double rotation;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: filled,
      enabled: filled,
      label: '$label: ${filled ? value : 'not added yet'}',
      child: GestureDetector(
        onTap: filled ? onTap : null,
        child: Transform.rotate(
          angle: rotation * 3.14159265 / 180,
          child: Container(
            width: 96,
            height: 92,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: filled ? tint : Colors.transparent,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: filled
                    ? AppColors.headerText.withValues(alpha: 0.5)
                    : AppColors.onboardingLine,
                width: 1.5,
              ),
              boxShadow: filled
                    ? <BoxShadow>[
                        BoxShadow(
                          color: AppColors.deepInk.withValues(alpha: 0.3),
                          offset: const Offset(0, 6),
                          blurRadius: 12,
                          spreadRadius: -8,
                        ),
                      ]
                    : null,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text(
                  label,
                  style: OnboardingType.sans(
                    11,
                    FontWeight.w700,
                    filled
                        ? AppColors.headerText
                        : AppColors.onboardingHint,
                  ),
                ),
                const SizedBox(height: 10),
                Row(
                  children: <Widget>[
                    Expanded(
                      child: Text(
                        filled ? value : '—',
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: OnboardingType.sans(
                          18,
                          FontWeight.w600,
                          filled ? AppColors.deepInk : AppColors.onboardingLine,
                        ),
                      ),
                    ),
                    if (filled && value != 'Skipped')
                      Icon(
                        Icons.check_circle_rounded,
                        size: 14,
                        color: AppColors.mutedGreen,
                      ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _QuestionCard extends StatelessWidget {
  const _QuestionCard({
    super.key,
    required this.state,
    required this.controller,
    required this.title,
    required this.hint,
  });

  final OnboardingState state;
  final OnboardingController controller;
  final String title;
  final String hint;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        Text(
          title,
          textAlign: TextAlign.center,
          style: OnboardingType.serif(
            22,
            FontWeight.w700,
            AppColors.deepInk,
            height: 28 / 22,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          hint,
          textAlign: TextAlign.center,
          style: OnboardingType.sans(
            14,
            FontWeight.w400,
            AppColors.onboardingMutedInk,
            height: 20 / 14,
          ),
        ),
        const SizedBox(height: 22),
        switch (state.profileStep) {
          0 => _AgeStepper(state: state, controller: controller),
          1 => _SexChoices(state: state, controller: controller),
          2 => _BloodChoices(state: state, controller: controller),
          _ => const _NotesReady(),
        },
      ],
    );
  }
}

class _AgeStepper extends StatelessWidget {
  const _AgeStepper({required this.state, required this.controller});

  final OnboardingState state;
  final OnboardingController controller;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        _RoundStepper(
          icon: Icons.remove_rounded,
          label: '1 year younger',
          onTap: state.age <= 18 ? null : () => controller.changeAge(-1),
        ),
        const SizedBox(width: 16),
        Column(
          children: <Widget>[
            Text(
              '${state.age}',
              style: OnboardingType.sans(
                42,
                FontWeight.w600,
                AppColors.deepInk,
                height: 1,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'years old',
              style: OnboardingType.sans(
                13,
                FontWeight.w500,
                AppColors.onboardingMutedInk,
              ),
            ),
          ],
        ),
        const SizedBox(width: 16),
        _RoundStepper(
          icon: Icons.add_rounded,
          label: '1 year older',
          onTap: state.age >= 100 ? null : () => controller.changeAge(1),
        ),
      ],
    );
  }
}

class _RoundStepper extends StatelessWidget {
  const _RoundStepper({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      enabled: onTap != null,
      label: label,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(20),
          child: AnimatedOpacity(
            duration: const Duration(milliseconds: 150),
            opacity: onTap == null ? 0.35 : 1,
            child: Ink(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: AppColors.headerText.withValues(alpha: 0.55),
                ),
              ),
              child: Icon(icon, size: 18, color: AppColors.headerText),
            ),
          ),
        ),
      ),
    );
  }
}

class _SexChoices extends StatelessWidget {
  const _SexChoices({required this.state, required this.controller});

  final OnboardingState state;
  final OnboardingController controller;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: <String>['Male', 'Female', 'Other']
          .map(
            (String option) => Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                child: _ChoiceButton(
                  label: option,
                  selected: state.sex == option,
                  onTap: () => controller.setSex(
                    state.sex == option ? null : option,
                  ),
                ),
              ),
            ),
          )
          .toList(),
    );
  }
}

class _BloodChoices extends StatelessWidget {
  const _BloodChoices({required this.state, required this.controller});

  final OnboardingState state;
  final OnboardingController controller;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 2),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: AppColors.onboardingLine),
          ),
          child: Text(
            'optional',
            style: OnboardingType.sans(
              12,
              FontWeight.w500,
              AppColors.onboardingMutedInk,
            ),
          ),
        ),
        const SizedBox(height: 16),
        Wrap(
          spacing: 10,
          runSpacing: 10,
          alignment: WrapAlignment.center,
          children: OnboardingProfileScreen._bloodTypes
              .map(
                (String type) => SizedBox(
                  width: 60,
                  height: 42,
                  child: _ChoiceButton(
                    label: type,
                    selected: state.bloodType == type,
                    onTap: () => controller.setBloodType(
                      state.bloodType == type ? null : type,
                    ),
                  ),
                ),
              )
              .toList(),
        ),
      ],
    );
  }
}

class _ChoiceButton extends StatelessWidget {
  const _ChoiceButton({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      selected: selected,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 180),
            decoration: BoxDecoration(
              color: selected ? AppColors.headerText : AppColors.cardSurface,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: selected ? AppColors.headerText : AppColors.onboardingLine,
              ),
            ),
            child: Center(
              child: Text(
                label,
                style: OnboardingType.sans(
                  14,
                  selected ? FontWeight.w700 : FontWeight.w500,
                  selected ? AppColors.cardSurface : AppColors.textPrimary,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _NotesReady extends StatelessWidget {
  const _NotesReady();

  @override
  Widget build(BuildContext context) {
    return Icon(
      Icons.check_circle_outline_rounded,
      size: 40,
      color: AppColors.mutedGreen,
    );
  }
}
