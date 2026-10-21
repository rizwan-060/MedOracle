import 'package:flutter/material.dart';

import '../theme/app_text_styles.dart';

/// Label + control pair with the reference's vertical rhythm
/// (12px above every group after the first, 4px between label and control).
class FieldGroup extends StatelessWidget {
  const FieldGroup({
    super.key,
    required this.label,
    required this.control,
    this.isFirst = false,
  });

  final String label;
  final Widget control;

  /// True for the first group inside a section (no top spacing).
  final bool isFirst;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(top: isFirst ? 0 : 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          Text(label, style: AppTextStyles.fieldLabel),
          const SizedBox(height: 4),
          control,
        ],
      ),
    );
  }
}
