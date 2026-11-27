import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:material_ui/material_ui.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../navigation/onboarding_navigation.dart';
import '../providers/onboarding_provider.dart';
import '../widgets/onboarding_shell.dart';
import '../widgets/onboarding_type.dart';

/// Onboarding 5 — Your daily habits.
///
/// Five compact questions with segmented answers and a sleep stepper. Choosing
/// an answer advances to the next question after a short delay.
class OnboardingHabitsScreen extends ConsumerWidget {
  const OnboardingHabitsScreen({super.key});

  static const String routePath = RouteNames.onboardingHabits;

  static const List<_Question> _questions = <_Question>[
    _Question(
      title: 'Physical movement & activity',
      hint: 'Do you engage in regular daily physical activity?',
      options: <String>['Yes', 'No'],
      icon: Icons.directions_walk_rounded,
    ),
    _Question(
      title: 'Vegetables, fruit & berries',
      hint: 'How often do you eat vegetables, fruit, or berries as part of your daily meals?',
      options: <String>['Every day', 'Not every day'],
      icon: Icons.eco_outlined,
    ),
    _Question(
      title: 'Current tobacco status',
      hint: 'Select your smoking or tobacco history.',
      options: <String>['Never smoked', 'Former smoker', 'Current smoker'],
      icon: Icons.local_fire_department_outlined,
    ),
    _Question(
      title: 'Average night sleep',
      hint: 'How many hours of sleep do you typically get per night?',
      options: <String>[],
      icon: Icons.nightlight_round,
    ),
    _Question(
      title: 'Perceived daily stress',
      hint: 'How would you rate your general daily stress level?',
      options: <String>['Low', 'Moderate', 'High'],
      icon: Icons.monitor_heart_outlined,
    ),
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final OnboardingState state = ref.watch(onboardingProvider);
    final OnboardingController controller =
        ref.read(onboardingProvider.notifier);
    final int step = state.habitsStep;
    final _Question question = _questions[step];
    final int? selected = _answerFor(state, step);
    final bool answered = step == 3 || selected != null;

    void pick(int questionIndex, int choice) {
      controller.setHabitAnswer(questionIndex, choice);
      if (questionIndex < 4) {
        unawaited(Future<void>.delayed(const Duration(milliseconds: 320), () {
          if (!context.mounted) return;
          if (ref.read(onboardingProvider).habitsStep == questionIndex) {
            controller.setHabitsStep(questionIndex + 1);
          }
        }));
      }
    }

    return OnboardingShell(
      step: 5,
      title: 'Your daily habits',
      subtitle: 'Tap the choice that fits you best.',
      backgroundColor: AppColors.authInputSurface,
      hardCtaShadow: true,
      ctaLabel: step == 4 ? 'See my path' : 'Next question',
      ctaEnabled: answered,
      onCta: () {
        if (step == 4) {
          OnboardingNavigation.next(context, RouteNames.onboardingPath);
        } else {
          controller.setHabitsStep(step + 1);
        }
      },
      onBack: step == 0
          ? null
          : () => controller.setHabitsStep(step - 1),
      child: SingleChildScrollView(
        child: Center(
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 420),
            child: _HabitQuestionCard(
              key: ValueKey<int>(step),
              question: question,
              selected: selected,
              sleep: state.sleep,
              onPick: (int choice) => pick(step, choice),
              onSleepChange: controller.changeSleep,
            ),
          ),
        ),
      ),
    );
  }

  static int? _answerFor(OnboardingState state, int index) {
    switch (index) {
      case 0:
        return state.activity;
      case 1:
        return state.produce;
      case 2:
        return state.tobacco;
      case 4:
        return state.stress;
      default:
        return null;
    }
  }
}

class _Question {
  const _Question({
    required this.title,
    required this.hint,
    required this.options,
    required this.icon,
  });

  final String title;
  final String hint;
  final List<String> options;
  final IconData icon;
}

class _HabitQuestionCard extends StatelessWidget {
  const _HabitQuestionCard({
    super.key,
    required this.question,
    required this.selected,
    required this.sleep,
    required this.onPick,
    required this.onSleepChange,
  });

  final _Question question;
  final int? selected;
  final double sleep;
  final ValueChanged<int> onPick;
  final ValueChanged<double> onSleepChange;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        const SizedBox(height: 24),
        Center(
          child: Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: AppColors.secondarySurface,
              shape: BoxShape.circle,
              border: Border.all(
                color: AppColors.headerText.withValues(alpha: 0.3),
              ),
            ),
            child: Icon(
              question.icon,
              size: 30,
              color: AppColors.headerText,
            ),
          ),
        ),
        const SizedBox(height: 24),
        Text(
          question.title,
          textAlign: TextAlign.center,
          style: OnboardingType.serif(
            22,
            FontWeight.w600,
            AppColors.deepInk,
            height: 28 / 22,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          question.hint,
          textAlign: TextAlign.center,
          style: OnboardingType.sans(
            14,
            FontWeight.w400,
            AppColors.onboardingMutedInk,
            height: 20 / 14,
          ),
        ),
        const SizedBox(height: 32),
        if (question.options.isEmpty)
          _SleepStepper(sleep: sleep, onChanged: onSleepChange)
        else
          _SegmentedOptions(
            options: question.options,
            selected: selected,
            onPick: onPick,
          ),
      ],
    );
  }
}

class _SegmentedOptions extends StatelessWidget {
  const _SegmentedOptions({
    required this.options,
    required this.selected,
    required this.onPick,
  });

  final List<String> options;
  final int? selected;
  final ValueChanged<int> onPick;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (BuildContext context, BoxConstraints constraints) {
        final double width = constraints.maxWidth;
        final double segmentWidth = (width - 4) / options.length;

        return Container(
          height: 48,
          padding: const EdgeInsets.all(2),
          decoration: BoxDecoration(
            color: AppColors.secondarySurface,
            borderRadius: BorderRadius.circular(14),
          ),
          child: Stack(
            children: <Widget>[
              AnimatedPositioned(
                duration: const Duration(milliseconds: 220),
                curve: Curves.easeOut,
                left: selected == null ? 2 : 2 + selected! * segmentWidth,
                top: 2,
                width: segmentWidth,
                height: 44,
                child: AnimatedOpacity(
                  duration: const Duration(milliseconds: 160),
                  opacity: selected == null ? 0 : 1,
                  child: Container(
                    decoration: BoxDecoration(
                      color: AppColors.cardSurface,
                      borderRadius: BorderRadius.circular(12),
                      boxShadow: <BoxShadow>[
                        BoxShadow(
                          color: AppColors.headerText.withValues(alpha: 0.18),
                          blurRadius: 8,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              Row(
                children: List<Widget>.generate(options.length, (int i) {
                  return Expanded(
                    child: Semantics(
                      button: true,
                      selected: selected == i,
                      child: GestureDetector(
                        onTap: () => onPick(i),
                        child: Center(
                          child: Text(
                            options[i],
                            textAlign: TextAlign.center,
                            style: OnboardingType.sans(
                              13,
                              selected == i
                                  ? FontWeight.w700
                                  : FontWeight.w500,
                              selected == i
                                  ? AppColors.headerText
                                  : AppColors.onboardingMutedInk,
                            ),
                          ),
                        ),
                      ),
                    ),
                  );
                }),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _SleepStepper extends StatelessWidget {
  const _SleepStepper({required this.sleep, required this.onChanged});

  final double sleep;
  final ValueChanged<double> onChanged;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        _SleepButton(
          icon: Icons.remove_rounded,
          label: 'Fewer hours',
          onTap: sleep <= 3 ? null : () => onChanged(-0.5),
        ),
        const SizedBox(width: 24),
        Column(
          children: <Widget>[
            Text(
              sleep.toStringAsFixed(1),
              style: OnboardingType.sans(
                38,
                FontWeight.w600,
                AppColors.deepInk,
                height: 1,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'hours',
              style: OnboardingType.sans(
                13,
                FontWeight.w500,
                AppColors.onboardingMutedInk,
              ),
            ),
          ],
        ),
        const SizedBox(width: 24),
        _SleepButton(
          icon: Icons.add_rounded,
          label: 'More hours',
          onTap: sleep >= 12 ? null : () => onChanged(0.5),
        ),
      ],
    );
  }
}

class _SleepButton extends StatelessWidget {
  const _SleepButton({
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
          borderRadius: BorderRadius.circular(28),
          child: AnimatedOpacity(
            duration: const Duration(milliseconds: 150),
            opacity: onTap == null ? 0.35 : 1,
            child: Ink(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: AppColors.headerText.withValues(alpha: 0.55),
                ),
              ),
              child: Icon(icon, size: 22, color: AppColors.headerText),
            ),
          ),
        ),
      ),
    );
  }
}
