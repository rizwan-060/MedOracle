import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Sentinel used by [OnboardingState.copyWith] so nullable fields can be
/// explicitly cleared without adding a separate `clearX` flag for each field.
const Object _unset = Object();

/// Mutable answers collected by the six onboarding screens.
///
/// The state is intentionally kept in memory: it survives navigation between
/// onboarding steps, but is discarded when the app is restarted.
class OnboardingState {
  const OnboardingState({
    this.age = 30,
    this.sex,
    this.bloodType,
    this.profileStep = 0,
    this.profileDone = const <String, bool>{
      'age': false,
      'sex': false,
      'blood': false,
    },
    this.heightFt = 5,
    this.heightIn = 9,
    this.weight = '172',
    this.weightUnit = 'lb',
    this.waist = '',
    this.habitsStep = 0,
    this.activity,
    this.produce,
    this.tobacco,
    this.sleep = 7.5,
    this.stress,
  });

  final int age;
  final String? sex;
  final String? bloodType;

  /// 0 = age, 1 = sex, 2 = blood type, 3 = notes-ready summary.
  final int profileStep;
  final Map<String, bool> profileDone;

  final int heightFt;
  final int heightIn;
  final String weight;
  final String weightUnit;
  final String waist;

  /// 0–4, matching the five habit questions.
  final int habitsStep;
  final int? activity;
  final int? produce;
  final int? tobacco;
  final double sleep;
  final int? stress;

  OnboardingState copyWith({
    int? age,
    Object? sex = _unset,
    Object? bloodType = _unset,
    int? profileStep,
    Map<String, bool>? profileDone,
    int? heightFt,
    int? heightIn,
    String? weight,
    String? weightUnit,
    String? waist,
    int? habitsStep,
    Object? activity = _unset,
    Object? produce = _unset,
    Object? tobacco = _unset,
    double? sleep,
    Object? stress = _unset,
  }) {
    return OnboardingState(
      age: age ?? this.age,
      sex: identical(sex, _unset) ? this.sex : sex as String?,
      bloodType: identical(bloodType, _unset)
          ? this.bloodType
          : bloodType as String?,
      profileStep: profileStep ?? this.profileStep,
      profileDone: profileDone ?? this.profileDone,
      heightFt: heightFt ?? this.heightFt,
      heightIn: heightIn ?? this.heightIn,
      weight: weight ?? this.weight,
      weightUnit: weightUnit ?? this.weightUnit,
      waist: waist ?? this.waist,
      habitsStep: habitsStep ?? this.habitsStep,
      activity: identical(activity, _unset) ? this.activity : activity as int?,
      produce: identical(produce, _unset) ? this.produce : produce as int?,
      tobacco: identical(tobacco, _unset) ? this.tobacco : tobacco as int?,
      sleep: sleep ?? this.sleep,
      stress: identical(stress, _unset) ? this.stress : stress as int?,
    );
  }
}

/// Session-scoped controller for the onboarding wizard.
class OnboardingController extends Notifier<OnboardingState> {
  /// Step 1 starts clean: default age, no sex/blood type, no pinned notes.
  static const OnboardingState _initialState = OnboardingState(
    age: 30,
    sex: null,
    bloodType: null,
    profileStep: 0,
    profileDone: <String, bool>{
      'age': false,
      'sex': false,
      'blood': false,
    },
  );

  @override
  OnboardingState build() => _initialState;

  static const List<String> _profileKeys = <String>['age', 'sex', 'blood'];

  void changeAge(int delta) {
    final int next = (state.age + delta).clamp(18, 100);
    state = state.copyWith(age: next);
  }

  void setSex(String? value) {
    state = state.copyWith(sex: value);
  }

  void setBloodType(String? value) {
    state = state.copyWith(bloodType: value);
  }

  void editProfile(String key) {
    final int index = _profileKeys.indexOf(key);
    if (index >= 0 && index < 3) {
      state = state.copyWith(profileStep: index);
    }
  }

  /// Explicitly restores the live OB3 entry state from a user action.
  void resetProfile() {
    state = state.copyWith(
      age: 30,
      sex: null,
      bloodType: null,
      profileStep: 0,
      profileDone: const <String, bool>{
        'age': false,
        'sex': false,
        'blood': false,
      },
    );
  }

  /// Static OB3 preview: age and sex are pinned, blood type is being asked.
  void applyProfilePreview() {
    state = state.copyWith(
      age: 30,
      sex: 'Male',
      bloodType: null,
      profileStep: 2,
      profileDone: const <String, bool>{
        'age': true,
        'sex': true,
        'blood': false,
      },
    );
  }

  /// Commits the currently visible profile question and advances to the first
  /// unanswered note, or to the notes-ready summary when all are complete.
  void commitProfile() {
    if (state.profileStep > 2) return;

    final String key = _profileKeys[state.profileStep];
    if (key == 'sex' && state.sex == null) return;

    final Map<String, bool> done = Map<String, bool>.from(state.profileDone);
    done[key] = true;

    final String? bloodType =
        key == 'blood' && state.bloodType == null ? 'skip' : state.bloodType;

    int next = 3;
    for (final String candidate in _profileKeys) {
      if (done[candidate] != true) {
        next = _profileKeys.indexOf(candidate);
        break;
      }
    }

    state = state.copyWith(
      bloodType: bloodType,
      profileDone: done,
      profileStep: next,
    );
  }

  void changeHeightFeet(int delta) {
    final int next = (state.heightFt + delta).clamp(4, 7);
    state = state.copyWith(heightFt: next);
  }

  void changeHeightInches(int delta) {
    final int next = (state.heightIn + delta).clamp(0, 11);
    state = state.copyWith(heightIn: next);
  }

  void setWeight(String value) {
    state = state.copyWith(weight: value);
  }

  void setWaist(String value) {
    state = state.copyWith(waist: value);
  }

  /// Converts the displayed weight when the lbs/kg toggle changes.
  void setWeightUnit(String unit) {
    if (unit == state.weightUnit) return;
    final double? value = double.tryParse(state.weight.trim());
    String converted = state.weight;
    if (value != null && value > 0) {
      final double result = unit == 'kg' ? value / 2.2046 : value * 2.2046;
      converted = result.toStringAsFixed(unit == 'kg' ? 1 : 0);
    }
    state = state.copyWith(weightUnit: unit, weight: converted);
  }

  void setHabitsStep(int step) {
    if (step < 0 || step > 4) return;
    state = state.copyWith(habitsStep: step);
  }

  void setHabitAnswer(int question, int choice) {
    switch (question) {
      case 0:
        state = state.copyWith(activity: choice);
        break;
      case 1:
        state = state.copyWith(produce: choice);
        break;
      case 2:
        state = state.copyWith(tobacco: choice);
        break;
      case 4:
        state = state.copyWith(stress: choice);
        break;
      default:
        break;
    }
  }

  void changeSleep(double delta) {
    final double next = (state.sleep + delta).clamp(3.0, 12.0);
    state = state.copyWith(sleep: next);
  }
}

final onboardingProvider =
    NotifierProvider<OnboardingController, OnboardingState>(
  OnboardingController.new,
);
