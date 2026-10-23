import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

/// Label + control pair with generous vertical rhythm
/// (24px between groups, 8px between label and control).
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
      padding: EdgeInsets.only(top: isFirst ? 0 : 24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          Text(
            label,
            style: AppTextStyles.lexend(
              fontSize: 14.0,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 8.0),
          control,
        ],
      ),
    );
  }
}
