import 'package:flutter/material.dart';

import '../../../core/widgets/choice_segment.dart';
import '../../../core/widgets/field_group.dart';
import '../../../core/widgets/tappable_value_field.dart';
import '../../../data/models/patient_profile_model.dart';

/// "Personal Details" section of Step 1: date of birth, gender, blood group.
class PersonalDetailsSection extends StatelessWidget {
  const PersonalDetailsSection({
    super.key,
    required this.profile,
    required this.onDateOfBirthTap,
    required this.onGenderChanged,
    required this.onBloodGroupChanged,
  });

  final PatientProfile profile;
  final VoidCallback onDateOfBirthTap;
  final ValueChanged<String> onGenderChanged;
  final ValueChanged<String> onBloodGroupChanged;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        FieldGroup(
          label: 'Date of Birth',
          isFirst: true,
          control: TappableValueField(
            value: profile.formattedDateOfBirth,
            semanticLabel: 'Date of Birth',
            suffix: ValueFieldSuffix.caret,
            onTap: onDateOfBirthTap,
          ),
        ),
        FieldGroup(
          label: 'Gender',
          control: ChoiceSegment(
            options: PatientProfile.genderOptions,
            value: profile.gender,
            onChanged: onGenderChanged,
            semanticLabel: 'Gender',
          ),
        ),
        FieldGroup(
          label: 'Blood Group',
          control: TappableValueField(
            value: profile.bloodGroup,
            semanticLabel: 'Blood Group',
            onTap: () => _pickBloodGroup(context, onBloodGroupChanged),
          ),
        ),
      ],
    );
  }

  Future<void> _pickBloodGroup(
    BuildContext context,
    ValueChanged<String> onChanged,
  ) async {
    final String? picked = await showModalBottomSheet<String>(
      context: context,
      showDragHandle: true,
      builder: (BuildContext context) => _OptionSheet(
        title: 'Blood Group',
        options: PatientProfile.bloodGroupOptions,
        value: profile.bloodGroup,
      ),
    );
    if (picked != null) {
      onChanged(picked);
    }
  }
}

/// Bottom sheet option list reused by every select-style field.
class _OptionSheet extends StatelessWidget {
  const _OptionSheet({
    required this.title,
    required this.options,
    required this.value,
  });

  final String title;
  final List<String> options;
  final String value;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 0, 20, 8),
            child: Text(title),
          ),
          Flexible(
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: options.length,
              itemBuilder: (BuildContext context, int index) {
                final String option = options[index];
                return ListTile(
                  title: Text(option),
                  trailing: option == value
                      ? const Icon(Icons.check, size: 20)
                      : null,
                  onTap: () => Navigator.of(context).pop(option),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
