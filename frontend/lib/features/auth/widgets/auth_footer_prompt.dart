import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// Centered "New to MedOracle? Sign Up" prompt with an underlined action.
class AuthFooterPrompt extends StatelessWidget {
  const AuthFooterPrompt({
    super.key,
    required this.prompt,
    required this.actionLabel,
    required this.onAction,
  });

  final String prompt;
  final String actionLabel;
  final VoidCallback onAction;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Wrap(
        alignment: WrapAlignment.center,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: <Widget>[
          Text(prompt, style: AppTextStyles.authFooter()),
          Semantics(
            button: true,
            label: actionLabel,
            child: GestureDetector(
              onTap: onAction,
              behavior: HitTestBehavior.opaque,
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 6),
                child: Text(
                  actionLabel,
                  style: AppTextStyles.authFooterAction().copyWith(
                    decoration: TextDecoration.underline,
                    decorationColor: AppColors.headerText,
                    decorationThickness: 1.4,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
