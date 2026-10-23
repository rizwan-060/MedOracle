import 'package:flutter/material.dart';

import '../../../core/widgets/choice_segment.dart';
import '../../../core/widgets/field_group.dart';
import '../../../core/widgets/tappable_value_field.dart';
import '../../../data/models/patient_profile_model.dart';

/// "Lifestyle" section of Step 1: smoking status and activity level.
class LifestyleSection extends StatelessWidget {
  const LifestyleSection({
    super.key,
    required this.profile,
    required this.onSmokingStatusChanged,
    required this.onActivityLevelChanged,
  });

  final PatientProfile profile;
  final ValueChanged<String> onSmokingStatusChanged;
  final ValueChanged<String> onActivityLevelChanged;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        FieldGroup(
          label: 'Smoking Status',
          isFirst: true,
          control: ChoiceSegment(
            options: PatientProfile.smokingStatusOptions,
            value: profile.smokingStatus,
            onChanged: onSmokingStatusChanged,
            semanticLabel: 'Smoking Status',
          ),
        ),
        FieldGroup(
          label: 'Activity Level',
          control: TappableValueField(
            value: profile.activityLevel,
            semanticLabel: 'Activity Level',
            onTap: () => _pickActivityLevel(context),
          ),
        ),
      ],
    );
  }

  Future<void> _pickActivityLevel(BuildContext context) async {
    final String? picked = await showModalBottomSheet<String>(
      context: context,
      showDragHandle: true,
      builder: (BuildContext context) => SafeArea(
        child: ListView(
          shrinkWrap: true,
          children: <Widget>[
            for (final String option in PatientProfile.activityLevelOptions)
              ListTile(
                title: Text(option),
                trailing: option == profile.activityLevel
                    ? const Icon(Icons.check, size: 20)
                    : null,
                onTap: () => Navigator.of(context).pop(option),
              ),
          ],
        ),
      ),
    );
    if (picked != null) {
      onActivityLevelChanged(picked);
    }
  }
}
