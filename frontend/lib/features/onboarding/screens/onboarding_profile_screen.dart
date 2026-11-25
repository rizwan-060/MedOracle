import 'dart:async';
import 'dart:math' as math;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:material_ui/material_ui.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../navigation/onboarding_navigation.dart';
import '../providers/onboarding_provider.dart';
import '../widgets/onboarding_shell.dart';
import '../widgets/onboarding_type.dart';

const List<String> _bloodTypes = <String>[
  'A+',
  'A-',
  'B+',
  'B-',
  'AB+',
  'AB-',
  'O+',
  'O-',
];

/// Onboarding 3 — Let's start with you.
///
/// Age, sex and blood type are collected one question at a time. Each committed
/// answer becomes an editable sticky note with a pin, fold and check badge.
class OnboardingProfileScreen extends ConsumerStatefulWidget {
  const OnboardingProfileScreen({super.key, this.initialPreviewMode = false});

  static const String routePath = RouteNames.onboardingProfile;

  /// Renders the static design preview: pinned age/sex notes, blood question.
  final bool initialPreviewMode;

  @override
  ConsumerState<OnboardingProfileScreen> createState() =>
      _OnboardingProfileScreenState();
}

class _OnboardingProfileScreenState
    extends ConsumerState<OnboardingProfileScreen>
    with SingleTickerProviderStateMixin {
  static const int _questionOutMs = 280;
  static const int _questionInMs = 550;
  static const double _questionOutEnd =
      _questionOutMs / (_questionOutMs + _questionInMs);
  static const List<String> _profileKeys = <String>['age', 'sex', 'blood'];

  late final AnimationController _stepController;
  late final AnimationController _noteController;
  late final AnimationController _ageController;
  final List<Timer> _timers = <Timer>[];

  int _displayedStep = 0;
  String? _droppingKey;
  int? _pressedStepper;
  String? _pressedOption;
  bool _transitioning = false;

  @override
  void initState() {
    super.initState();

    final OnboardingController controller =
        ref.read(onboardingProvider.notifier);
    if (widget.initialPreviewMode) {
      controller.applyProfilePreview();
    } else {
      controller.resetProfile();
    }
    _displayedStep = ref.read(onboardingProvider).profileStep;

    _stepController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: _questionOutMs + _questionInMs),
    );
    _noteController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    )..value = 1;
    _ageController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 170),
    )..value = 1;

    _stepController.addStatusListener((AnimationStatus status) {
      if (status == AnimationStatus.completed && mounted) {
        setState(() => _transitioning = false);
      }
    });
    _noteController.addStatusListener((AnimationStatus status) {
      if (status == AnimationStatus.completed && mounted) {
        setState(() => _droppingKey = null);
      }
    });
  }

  @override
  void dispose() {
    for (final Timer timer in _timers) {
      timer.cancel();
    }
    _timers.clear();
    _stepController.dispose();
    _noteController.dispose();
    _ageController.dispose();
    super.dispose();
  }

  void _clearTimers() {
    for (final Timer timer in _timers) {
      timer.cancel();
    }
    _timers.clear();
  }

  void _changeAge(int delta) {
    if (delta < 0 && ref.read(onboardingProvider).age <= 18) return;
    if (delta > 0 && ref.read(onboardingProvider).age >= 100) return;
    ref.read(onboardingProvider.notifier).changeAge(delta);
    _ageController.forward(from: 0);
  }

  void _setStepperPress(int? value) {
    if (!mounted) return;
    setState(() => _pressedStepper = value);
  }

  void _setOptionPress(String? value) {
    if (!mounted) return;
    setState(() => _pressedOption = value);
  }

  void _edit(String key) {
    if (_transitioning) return;
    final int target = _profileKeys.indexOf(key);
    if (target < 0) return;
    ref.read(onboardingProvider.notifier).editProfile(key);
    _beginStepTransition(target);
  }

  void _handleCta(BuildContext context) {
    if (_transitioning) return;
    final OnboardingState state = ref.read(onboardingProvider);
    if (state.profileStep > 2) {
      OnboardingNavigation.next(context, RouteNames.onboardingBodyDetails);
      return;
    }

    final String key = _profileKeys[state.profileStep];
    if (key == 'sex' && state.sex == null) return;

    ref.read(onboardingProvider.notifier).commitProfile();
    final int target = ref.read(onboardingProvider).profileStep;
    _beginStepTransition(target, dropKey: key);
  }

  void _beginStepTransition(int targetStep, {String? dropKey}) {
    _clearTimers();
    if (_stepController.isAnimating) _stepController.stop();
    setState(() => _transitioning = true);

    if (dropKey != null) {
      setState(() => _droppingKey = dropKey);
      _noteController.forward(from: 0);
    }

    _timers.add(Timer(Duration(milliseconds: dropKey != null ? 700 : 0), () {
      if (!mounted) return;
      _stepController.forward(from: 0);
      _timers.add(Timer(const Duration(milliseconds: _questionOutMs), () {
        if (!mounted) return;
        setState(() => _displayedStep = targetStep);
      }));
    }));
  }

  @override
  Widget build(BuildContext context) {
    final OnboardingState state = ref.watch(onboardingProvider);
    final bool finished = state.profileStep > 2;

    final String ctaLabel;
    final bool ctaEnabled;
    if (finished) {
      ctaLabel = 'Add my body details';
      ctaEnabled = true;
    } else {
      final bool bloodChosen =
          state.bloodType != null && state.bloodType != 'skip';
      ctaLabel = switch (state.profileStep) {
        0 => 'Add my age',
        1 => 'Add my sex',
        _ => bloodChosen ? 'Add blood type' : 'Skip for now',
      };
      ctaEnabled = state.profileStep != 1 || state.sex != null;
    }

    return OnboardingShell(
      step: 3,
      title: "Let's start with you",
      subtitle: 'One quick question at a time.',
      ctaLabel: ctaLabel,
      ctaEnabled: ctaEnabled,
      onCta: () => _handleCta(context),
      onBack: () => context.go(RouteNames.onboardingWelcome),
      child: Padding(
        // OnboardingShell supplies 20px horizontally; this completes 24px.
        padding: const EdgeInsets.fromLTRB(4, 24, 4, 24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            AnimatedBuilder(
              animation: _noteController,
              builder: (BuildContext context, Widget? child) {
                return _NotesBoard(
                  state: state,
                  displayedStep: _displayedStep,
                  droppingKey: _droppingKey,
                  dropProgress: _noteController.value,
                  onEdit: _edit,
                );
              },
            ),
            if (_displayedStep < 3) const SizedBox(height: 28),
            if (_displayedStep < 3)
              AnimatedBuilder(
                animation: _stepController,
                builder: (BuildContext context, Widget? child) {
                  final double t = _stepController.value;
                  final double outP = Curves.easeIn.transform(
                    (t / _questionOutEnd).clamp(0.0, 1.0).toDouble(),
                  );
                  final double inP = Curves.easeOut.transform(
                    ((t - _questionOutEnd) / (1 - _questionOutEnd))
                        .clamp(0.0, 1.0)
                        .toDouble(),
                  );
                  final bool showNext = t >= _questionOutEnd;
                  final double opacity = showNext ? inP : 1 - outP;
                  final double dy = showNext ? 26 * (1 - inP) : -18 * outP;

                  return Opacity(
                    opacity: opacity,
                    child: Transform.translate(
                      offset: Offset(0, dy),
                      child: _QuestionCard(
                        step: _displayedStep,
                        state: state,
                        ageController: _ageController,
                        pressedStepper: _pressedStepper,
                        pressedOption: _pressedOption,
                        onChangeAge: _changeAge,
                        onSetStepperPress: _setStepperPress,
                        onSetSex: (String value) =>
                            ref.read(onboardingProvider.notifier).setSex(value),
                        onSetBlood: (String? value) => ref
                            .read(onboardingProvider.notifier)
                            .setBloodType(value),
                        onSetOptionPress: _setOptionPress,
                      ),
                    ),
                  );
                },
              ),
          ],
        ),
      ),
    );
  }
}

class _NotesBoard extends StatelessWidget {
  const _NotesBoard({
    required this.state,
    required this.displayedStep,
    required this.droppingKey,
    required this.dropProgress,
    required this.onEdit,
  });

  final OnboardingState state;
  final int displayedStep;
  final String? droppingKey;
  final double dropProgress;
  final ValueChanged<String> onEdit;

  static const List<String> _keys = <String>['age', 'sex', 'blood'];
  static const List<String> _labels = <String>['Age', 'Sex', 'Blood type'];
  static const List<Color> _tints = <Color>[
    AppColors.onboardingAgeFill,
    AppColors.onboardingSexFill,
    AppColors.onboardingBloodFill,
  ];
  static const List<double> _rotations = <double>[-1.4, 1.2, -0.9];

  @override
  Widget build(BuildContext context) {
    final bool finished = displayedStep > 2;
    final List<Widget> notes = <Widget>[];

    for (int i = 0; i < _keys.length; i++) {
      final String key = _keys[i];
      final bool filled = state.profileDone[key] ?? false;
      final String value = switch (key) {
        'age' => '$state.age',
        'sex' => state.sex ?? '',
        _ => state.bloodType == 'skip' ? 'Skipped' : (state.bloodType ?? ''),
      };
      final bool dropping = droppingKey == key;
      final double eased = Curves.elasticOut.transform(dropProgress);
      final double progress = eased.clamp(0.0, 1.04).toDouble();

      notes.add(
        _NoteCard(
          label: _labels[i],
          value: value,
          filled: filled,
          tint: _tints[i],
          rotation: _rotations[i],
          current: !finished && displayedStep == i,
          dropping: dropping,
          dropProgress: dropping ? progress : 1,
          onTap: filled ? () => onEdit(key) : null,
        ),
      );
    }

    if (finished) {
      return Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: <Widget>[
          for (int i = 0; i < notes.length; i++) ...<Widget>[
            notes[i],
            if (i < notes.length - 1) const SizedBox(height: 24),
          ],
        ],
      );
    }

    return Padding(
      padding: const EdgeInsets.only(top: 10),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          for (int i = 0; i < notes.length; i++) ...<Widget>[
            notes[i],
            if (i < notes.length - 1) const SizedBox(width: 12),
          ],
        ],
      ),
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
    required this.current,
    required this.dropping,
    required this.dropProgress,
    this.onTap,
  });

  final String label;
  final String value;
  final bool filled;
  final Color tint;
  final double rotation;
  final bool current;
  final bool dropping;
  final double dropProgress;
  final VoidCallback? onTap;

  static const BorderRadius _radius = BorderRadius.only(
    topLeft: Radius.circular(3),
    topRight: Radius.circular(3),
    bottomLeft: Radius.circular(3),
    bottomRight: Radius.circular(16),
  );

  @override
  Widget build(BuildContext context) {
    final double dy = dropping ? -36 * (1 - dropProgress) : 0;
    final double scale = dropping ? 0.86 + 0.14 * dropProgress : 1;
    final double angle = dropping
        ? rotation + (-rotation * 2) * (1 - dropProgress)
        : rotation;

    return Semantics(
      button: filled,
      enabled: filled,
      label: '$label: ${filled ? value : 'not added yet'}',
      child: GestureDetector(
        onTap: onTap,
        child: Transform.translate(
          offset: Offset(0, dy),
          child: Transform.scale(
            scale: scale,
            child: Transform.rotate(
              angle: angle * math.pi / 180,
              child: Stack(
                clipBehavior: Clip.none,
                children: <Widget>[
                  _NoteSurface(
                    label: label,
                    value: value,
                    filled: filled,
                    tint: tint,
                    current: current,
                  ),
                  if (!filled)
                    Positioned.fill(
                      child: CustomPaint(
                        painter: _DashedNoteBorderPainter(
                          color: current
                              ? AppColors.headerText
                              : AppColors.onboardingLine,
                        ),
                      ),
                    ),
                  if (filled)
                    const Positioned(
                      top: -9,
                      left: 43,
                      child: CustomPaint(
                        painter: _PinPainter(),
                        size: Size(18, 18),
                      ),
                    ),
                  if (filled)
                    const Positioned(
                      right: 0,
                      bottom: 0,
                      child: CustomPaint(
                        painter: _FoldPainter(),
                        size: Size(16, 16),
                      ),
                    ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _NoteSurface extends StatelessWidget {
  const _NoteSurface({
    required this.label,
    required this.value,
    required this.filled,
    required this.tint,
    required this.current,
  });

  final String label;
  final String value;
  final bool filled;
  final Color tint;
  final bool current;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 104,
      constraints: const BoxConstraints(minHeight: 92),
      padding: const EdgeInsets.fromLTRB(12, 22, 12, 12),
      decoration: BoxDecoration(
        color: filled ? tint : Colors.transparent,
        borderRadius: _NoteCard._radius,
        border: filled
            ? Border.all(
                color: current ? AppColors.headerText : Colors.transparent,
                width: 1.5,
              )
            : null,
        boxShadow: filled
            ? <BoxShadow>[
                BoxShadow(
                  color: AppColors.deepInk.withValues(alpha: 0.35),
                  offset: const Offset(0, 8),
                  blurRadius: 14,
                  spreadRadius: -8,
                ),
                BoxShadow(
                  color: AppColors.deepInk.withValues(alpha: 0.12),
                  offset: const Offset(0, 1),
                  blurRadius: 2,
                ),
              ]
            : null,
      ),
      child: Stack(
        children: <Widget>[
          if (filled)
            Positioned.fill(
              child: ClipRRect(
                borderRadius: _NoteCard._radius,
                child: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: <Color>[
                        AppColors.authOnSlate.withValues(alpha: 0.55),
                        Colors.transparent,
                      ],
                    ),
                  ),
                ),
              ),
            ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
              Text(
                label.toUpperCase(),
                style: OnboardingType.sans(
                  11,
                  FontWeight.w500,
                  filled
                      ? AppColors.onboardingLabelInk
                      : AppColors.onboardingHint,
                  spacing: 0.08 * 11,
                ),
              ),
              const SizedBox(height: 6),
              ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 24),
                child: Row(
                  children: <Widget>[
                    Expanded(
                      child: Text(
                        filled ? value : '—',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: OnboardingType.serif(
                          17,
                          FontWeight.w700,
                          filled ? AppColors.deepInk : AppColors.onboardingLine,
                          height: 24 / 17,
                        ),
                      ),
                    ),
                    if (filled && value != 'Skipped') ...<Widget>[
                      const SizedBox(width: 4),
                      const _CheckBadge(),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _CheckBadge extends StatelessWidget {
  const _CheckBadge();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 20,
      height: 20,
      decoration: const BoxDecoration(
        color: AppColors.onboardingLabelInk,
        shape: BoxShape.circle,
      ),
      child: const Center(
        child: CustomPaint(
          painter: _CheckMarkPainter(),
          size: Size(12, 12),
        ),
      ),
    );
  }
}

class _QuestionCard extends StatelessWidget {
  const _QuestionCard({
    required this.step,
    required this.state,
    required this.ageController,
    required this.pressedStepper,
    required this.pressedOption,
    required this.onChangeAge,
    required this.onSetStepperPress,
    required this.onSetSex,
    required this.onSetBlood,
    required this.onSetOptionPress,
  });

  final int step;
  final OnboardingState state;
  final AnimationController ageController;
  final int? pressedStepper;
  final String? pressedOption;
  final ValueChanged<int> onChangeAge;
  final ValueChanged<int?> onSetStepperPress;
  final ValueChanged<String> onSetSex;
  final ValueChanged<String?> onSetBlood;
  final ValueChanged<String?> onSetOptionPress;

  static const List<String> _titles = <String>[
    'How old are you?',
    'What is your sex?',
    'Blood type',
  ];
  static const List<String> _hints = <String>[
    'Your age helps us read your results correctly.',
    'Some health checks differ by sex. Choose what fits you best.',
    'Select your blood group if you know it.',
  ];

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(minHeight: 262),
      child: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
              if (step == 2)
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: <Widget>[
                    _title(),
                    const SizedBox(width: 10),
                    const _OptionalPill(),
                  ],
                )
              else
                _title(),
              const SizedBox(height: 6),
              Text(
                _hints[step],
                textAlign: TextAlign.center,
                style: OnboardingType.sans(
                  14,
                  FontWeight.w400,
                  AppColors.onboardingMutedInk,
                  height: 20 / 14,
                ),
              ),
              const SizedBox(height: 22),
              switch (step) {
                0 => _AgeStepper(
                    age: state.age,
                    controller: ageController,
                    pressedStepper: pressedStepper,
                    onChangeAge: onChangeAge,
                    onSetStepperPress: onSetStepperPress,
                  ),
                1 => _SexChoices(
                    selected: state.sex,
                    pressedOption: pressedOption,
                    onSetSex: onSetSex,
                    onSetOptionPress: onSetOptionPress,
                  ),
                _ => _BloodChoices(
                    selected: state.bloodType,
                    pressedOption: pressedOption,
                    onSetBlood: onSetBlood,
                    onSetOptionPress: onSetOptionPress,
                  ),
              },
            ],
          ),
        ),
      ),
    );
  }

  Widget _title() {
    return Text(
      _titles[step],
      textAlign: TextAlign.center,
      style: OnboardingType.serif(
        22,
        FontWeight.w700,
        AppColors.deepInk,
        height: 28 / 22,
      ),
    );
  }
}

class _OptionalPill extends StatelessWidget {
  const _OptionalPill();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 2),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.onboardingLine, width: 1),
      ),
      child: Text(
        'optional',
        style: OnboardingType.sans(
          14,
          FontWeight.w400,
          AppColors.onboardingMutedInk,
        ),
      ),
    );
  }
}

class _AgeStepper extends StatelessWidget {
  const _AgeStepper({
    required this.age,
    required this.controller,
    required this.pressedStepper,
    required this.onChangeAge,
    required this.onSetStepperPress,
  });

  final int age;
  final AnimationController controller;
  final int? pressedStepper;
  final ValueChanged<int> onChangeAge;
  final ValueChanged<int?> onSetStepperPress;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        _RoundStepper(
          plus: false,
          disabled: age <= 18,
          pressed: pressedStepper == -1,
          onTap: () => onChangeAge(-1),
          onPressChange: (bool pressed) =>
              onSetStepperPress(pressed ? -1 : null),
        ),
        const SizedBox(width: 16),
        AnimatedBuilder(
          animation: controller,
          builder: (BuildContext context, Widget? child) {
            final double progress =
                Curves.easeOut.transform(controller.value.clamp(0.0, 1.0));
            return Transform.scale(
              scale: 1 + 0.14 * (1 - progress),
              child: child,
            );
          },
          child: _AgeNumberBox(age: age),
        ),
        const SizedBox(width: 16),
        _RoundStepper(
          plus: true,
          disabled: age >= 100,
          pressed: pressedStepper == 1,
          onTap: () => onChangeAge(1),
          onPressChange: (bool pressed) =>
              onSetStepperPress(pressed ? 1 : null),
        ),
      ],
    );
  }
}

class _AgeNumberBox extends StatelessWidget {
  const _AgeNumberBox({required this.age});

  final int age;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 130,
      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.onboardingNumberFill,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Text(
            '$age',
            style: OnboardingType.serif(
              40,
              FontWeight.w700,
              AppColors.deepInk,
              height: 44 / 40,
            ),
          ),
          Text(
            'years old',
            style: OnboardingType.sans(
              12,
              FontWeight.w500,
              AppColors.onboardingAgeSubLabel,
              height: 16 / 12,
            ),
          ),
        ],
      ),
    );
  }
}

class _RoundStepper extends StatelessWidget {
  const _RoundStepper({
    required this.plus,
    required this.disabled,
    required this.pressed,
    required this.onTap,
    required this.onPressChange,
  });

  final bool plus;
  final bool disabled;
  final bool pressed;
  final VoidCallback onTap;
  final ValueChanged<bool> onPressChange;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      enabled: !disabled,
      label: plus ? '1 year older' : '1 year younger',
      child: AnimatedOpacity(
        duration: const Duration(milliseconds: 150),
        opacity: disabled ? 0.35 : 1,
        child: GestureDetector(
          onTap: disabled ? null : onTap,
          onTapDown: disabled ? null : (_) => onPressChange(true),
          onTapUp: disabled ? null : (_) => onPressChange(false),
          onTapCancel: disabled ? null : () => onPressChange(false),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 100),
            width: 44,
            height: 44,
            transform: Matrix4.translationValues(0, pressed ? 2 : 0, 0),
            decoration: BoxDecoration(
              color: AppColors.headerText,
              shape: BoxShape.circle,
              boxShadow: <BoxShadow>[
                BoxShadow(
                  color: AppColors.onboardingStepperShadow,
                  offset: Offset(0, pressed ? 1 : 3),
                ),
              ],
            ),
            child: Center(
              child: CustomPaint(
                painter: _PlusMinusPainter(
                  plus: plus,
                  color: AppColors.authOnSlate,
                ),
                size: const Size(18, 18),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _SexChoices extends StatelessWidget {
  const _SexChoices({
    required this.selected,
    required this.pressedOption,
    required this.onSetSex,
    required this.onSetOptionPress,
  });

  final String? selected;
  final String? pressedOption;
  final ValueChanged<String> onSetSex;
  final ValueChanged<String?> onSetOptionPress;

  static const List<String> _options = <String>['Male', 'Female', 'Other'];

  @override
  Widget build(BuildContext context) {
    return Row(
      children: <Widget>[
        for (int i = 0; i < _options.length; i++) ...<Widget>[
          Expanded(
            child: _ChoiceButton(
              label: _options[i],
              selected: selected == _options[i],
              pressed: pressedOption == _options[i],
              onTap: () => onSetSex(_options[i]),
              onPressChange: (bool pressed) =>
                  onSetOptionPress(pressed ? _options[i] : null),
            ),
          ),
          if (i < _options.length - 1) const SizedBox(width: 10),
        ],
      ],
    );
  }
}

class _ChoiceButton extends StatelessWidget {
  const _ChoiceButton({
    required this.label,
    required this.selected,
    required this.pressed,
    required this.onTap,
    required this.onPressChange,
  });

  final String label;
  final bool selected;
  final bool pressed;
  final VoidCallback onTap;
  final ValueChanged<bool> onPressChange;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      selected: selected,
      child: GestureDetector(
        onTap: onTap,
        onTapDown: (_) => onPressChange(true),
        onTapUp: (_) => onPressChange(false),
        onTapCancel: () => onPressChange(false),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          height: 64,
          transform: Matrix4.translationValues(0, pressed ? -2 : 0, 0),
          decoration: BoxDecoration(
            color: selected
                ? AppColors.onboardingLabelInk
                : AppColors.cardSurface,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(
              color: pressed
                  ? AppColors.headerText
                  : (selected
                      ? AppColors.onboardingLabelInk
                      : AppColors.onboardingLine),
              width: 1.5,
            ),
          ),
          child: Center(
            child: Text(
              label,
              style: OnboardingType.sans(
                16,
                FontWeight.w500,
                selected ? AppColors.authOnSlate : AppColors.deepInk,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _BloodChoices extends StatelessWidget {
  const _BloodChoices({
    required this.selected,
    required this.pressedOption,
    required this.onSetBlood,
    required this.onSetOptionPress,
  });

  final String? selected;
  final String? pressedOption;
  final ValueChanged<String?> onSetBlood;
  final ValueChanged<String?> onSetOptionPress;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 4 * 64 + 3 * 12,
      child: Wrap(
        spacing: 12,
        runSpacing: 12,
        alignment: WrapAlignment.center,
        children: <Widget>[
          for (final String type in _bloodTypes)
            _DropChoice(
              label: type,
              selected: selected == type,
              pressed: pressedOption == type,
              onTap: () => onSetBlood(selected == type ? null : type),
              onPressChange: (bool pressed) =>
                  onSetOptionPress(pressed ? type : null),
            ),
        ],
      ),
    );
  }
}

class _DropChoice extends StatelessWidget {
  const _DropChoice({
    required this.label,
    required this.selected,
    required this.pressed,
    required this.onTap,
    required this.onPressChange,
  });

  final String label;
  final bool selected;
  final bool pressed;
  final VoidCallback onTap;
  final ValueChanged<bool> onPressChange;

  @override
  Widget build(BuildContext context) {
    final Color fill = selected
        ? AppColors.onboardingLabelInk
        : AppColors.cardSurface;
    final Color border = pressed
        ? AppColors.headerText
        : (selected ? AppColors.onboardingLabelInk : AppColors.onboardingLine);

    return Semantics(
      button: true,
      selected: selected,
      child: GestureDetector(
        onTap: onTap,
        onTapDown: (_) => onPressChange(true),
        onTapUp: (_) => onPressChange(false),
        onTapCancel: () => onPressChange(false),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          width: 64,
          height: 64,
          transform: Matrix4.translationValues(0, pressed ? -2 : 0, 0),
          child: Stack(
            alignment: Alignment.center,
            children: <Widget>[
              CustomPaint(
                painter: _DropShapePainter(fill: fill, border: border),
                size: const Size(64, 64),
              ),
              Text(
                label,
                style: OnboardingType.sans(
                  15,
                  FontWeight.w500,
                  selected ? AppColors.authOnSlate : AppColors.deepInk,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _DashedNoteBorderPainter extends CustomPainter {
  const _DashedNoteBorderPainter({required this.color});

  final Color color;

  static const double _stroke = 1.5;
  static const double _dash = 5;
  static const double _gap = 4;

  @override
  void paint(Canvas canvas, Size size) {
    final Rect rect = Rect.fromLTWH(
      _stroke / 2,
      _stroke / 2,
      size.width - _stroke,
      size.height - _stroke,
    );
    final RRect rounded = RRect.fromRectAndCorners(
      rect,
      topLeft: const Radius.circular(3),
      topRight: const Radius.circular(3),
      bottomLeft: const Radius.circular(3),
      bottomRight: const Radius.circular(16),
    );
    final Path path = Path()..addRRect(rounded);
    final metric = path.computeMetrics().first;
    final Paint paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = _stroke
      ..strokeCap = StrokeCap.round;

    double distance = 0;
    while (distance < metric.length) {
      final double end = math.min(distance + _dash, metric.length);
      canvas.drawPath(metric.extractPath(distance, end), paint);
      distance += _dash + _gap;
    }
  }

  @override
  bool shouldRepaint(covariant _DashedNoteBorderPainter oldDelegate) =>
      oldDelegate.color != color;
}

class _PinPainter extends CustomPainter {
  const _PinPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final Rect rect = Offset.zero & size;
    canvas.save();
    canvas.translate(0, 3);
    canvas.drawCircle(
      rect.center,
      size.width / 2,
      Paint()
        ..color = AppColors.deepInk.withValues(alpha: 0.3)
        ..maskFilter = MaskFilter.blur(BlurStyle.normal, 3),
    );
    canvas.restore();

    final RadialGradient gradient = RadialGradient(
      center: const Alignment(-0.35, -0.35),
      radius: 0.85,
      colors: <Color>[
        AppColors.onboardingPinHighlight,
        AppColors.onboardingPinMid,
        AppColors.onboardingPinDeep,
      ],
      stops: const <double>[0, 0.55, 1],
    );
    canvas.drawCircle(
      rect.center,
      size.width / 2,
      Paint()..shader = gradient.createShader(rect),
    );
  }

  @override
  bool shouldRepaint(covariant _PinPainter oldDelegate) => false;
}

class _FoldPainter extends CustomPainter {
  const _FoldPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final Path path = Path()
      ..moveTo(size.width, 0)
      ..lineTo(size.width, size.height)
      ..lineTo(0, size.height)
      ..close();
    canvas.drawPath(path, Paint()..color = AppColors.onboardingFoldSurface);
  }

  @override
  bool shouldRepaint(covariant _FoldPainter oldDelegate) => false;
}

class _CheckMarkPainter extends CustomPainter {
  const _CheckMarkPainter();

  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawPath(
      Path()
        ..moveTo(2, 6)
        ..lineTo(5, 9)
        ..lineTo(10, 3),
      Paint()
        ..color = AppColors.authOnSlate
        ..style = PaintingStyle.stroke
        ..strokeWidth = 3.2
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round,
    );
  }

  @override
  bool shouldRepaint(covariant _CheckMarkPainter oldDelegate) => false;
}

class _PlusMinusPainter extends CustomPainter {
  const _PlusMinusPainter({required this.plus, required this.color});

  final bool plus;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final Paint paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.2
      ..strokeCap = StrokeCap.round;

    canvas.drawLine(
      Offset(1, size.height / 2),
      Offset(size.width - 1, size.height / 2),
      paint,
    );
    if (plus) {
      canvas.drawLine(
        Offset(size.width / 2, 1),
        Offset(size.width / 2, size.height - 1),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _PlusMinusPainter oldDelegate) =>
      plus != oldDelegate.plus || color != oldDelegate.color;
}

class _DropShapePainter extends CustomPainter {
  const _DropShapePainter({required this.fill, required this.border});

  final Color fill;
  final Color border;

  @override
  void paint(Canvas canvas, Size size) {
    final double w = size.width;
    final double h = size.height;
    final Path path = Path()
      ..moveTo(w * 0.5, h)
      ..cubicTo(w * 0.86, h * 0.82, w, h * 0.66, w, h * 0.42)
      ..cubicTo(w, h * 0.18, w * 0.78, 0, w * 0.5, 0)
      ..cubicTo(w * 0.22, 0, 0, h * 0.18, 0, h * 0.42)
      ..cubicTo(0, h * 0.66, w * 0.14, h * 0.82, w * 0.5, h)
      ..close();

    canvas.drawPath(path, Paint()..color = fill);
    canvas.drawPath(
      path,
      Paint()
        ..color = border
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.5,
    );
  }

  @override
  bool shouldRepaint(covariant _DropShapePainter oldDelegate) =>
      fill != oldDelegate.fill || border != oldDelegate.border;
}
