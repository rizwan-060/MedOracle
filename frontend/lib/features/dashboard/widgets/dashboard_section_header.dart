import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// Section heading of the dashboard.
///
/// Renders a bold title with an optional trailing text action such as
/// "See all".
class DashboardSectionHeader extends StatelessWidget {
  const DashboardSectionHeader({
    super.key,
    required this.title,
    this.actionLabel,
    this.onAction,
  });

  /// Section title, e.g. `Quick actions`.
  final String title;

  /// Label of the optional trailing action.
  final String? actionLabel;

  /// Invoked when the trailing action is tapped.
  final VoidCallback? onAction;

  @override
  Widget build(BuildContext context) {
    final String? label = actionLabel;
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: <Widget>[
          Expanded(
            child: Text(
              title,
              style: AppTextStyles.instrumentSerif(
                fontSize: 24.0,
                fontWeight: FontWeight.w600,
                color: AppColors.headerText,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          if (label != null)
            // The reference draws a 44px action whose -10px margins keep the
            // visible row at the 24px title height.
            TextButton(
              onPressed: onAction,
              style: TextButton.styleFrom(
                foregroundColor: AppColors.primaryMaroon,
                backgroundColor: Colors.transparent,
                padding: const EdgeInsets.symmetric(horizontal: 8),
                minimumSize: const Size(0, 24),
                tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                shape: const RoundedRectangleBorder(),
              ),
              child: Text(label, style: AppTextStyles.dashboardSectionAction),
            ),
        ],
      ),
    );
  }
}
