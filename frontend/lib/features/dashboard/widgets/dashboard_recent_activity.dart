import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../models/dashboard_models.dart';
import 'dashboard_icons.dart';

/// "Recent assessments" list of the dashboard.
///
/// A single white sheet holding one row per assessment; every row shows the
/// run date, the assessment name and its status.
class DashboardRecentActivity extends StatelessWidget {
  const DashboardRecentActivity({
    super.key,
    required this.assessments,
    this.onItemTap,
  });

  /// Assessments to list, newest first.
  final List<DashboardAssessment> assessments;

  /// Invoked with the tapped assessment.
  final void Function(DashboardAssessment assessment)? onItemTap;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(12.0),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.dustyTaupe.withValues(alpha: 0.45),
            blurRadius: 0,
            spreadRadius: 1,
          ),
          BoxShadow(
            color: AppColors.controlShadowStrong,
            blurRadius: 26,
            spreadRadius: -14,
            offset: const Offset(0, 12),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12.0),
        child: Column(
          children: <Widget>[
            for (int index = 0; index < assessments.length; index++)
              _AssessmentTile(
                assessment: assessments[index],
                showDivider: index != 0,
                onTap: onItemTap == null
                    ? null
                    : () => onItemTap!(assessments[index]),
              ),
          ],
        ),
      ),
    );
  }
}

/// A single row of the "Recent assessments" list.
class _AssessmentTile extends StatelessWidget {
  const _AssessmentTile({
    required this.assessment,
    required this.showDivider,
    this.onTap,
  });

  /// The assessment rendered by this row.
  final DashboardAssessment assessment;

  /// Whether a hairline divider is drawn above the row.
  final bool showDivider;

  /// Invoked when the row is tapped.
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        if (showDivider)
          const Divider(height: 1, thickness: 1, color: AppColors.borderSubtle),
        Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onTap,
            child: ConstrainedBox(
              constraints: const BoxConstraints(minHeight: 76),
              child: Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
                child: Row(
                  children: <Widget>[
                    _DateChip(date: assessment.date),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: <Widget>[
                          Text(
                            assessment.title,
                            style: AppTextStyles.dashboardActivityTitle,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 6),
                          _StatusBadge(status: assessment.status),
                        ],
                      ),
                    ),
                    const SizedBox(width: 14),
                    const DashboardIcon(
                      DashboardIconType.chevronRight,
                      size: 16,
                      color: AppColors.primaryMaroon,
                      strokeWidth: 2.2,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

/// Month / day chip of a recent assessment row.
class _DateChip extends StatelessWidget {
  const _DateChip({required this.date});

  /// Day the assessment was run.
  final DateTime date;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 48,
      height: 52,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: AppColors.primaryMaroon.withValues(alpha: 0.07),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Text(
            _monthLabel(date.month),
            style: AppTextStyles.dashboardDateMonth,
          ),
          Text('${date.day}', style: AppTextStyles.dashboardDateDay),
        ],
      ),
    );
  }
}

/// Status pill of a recent assessment row.
class _StatusBadge extends StatelessWidget {
  const _StatusBadge({required this.status});

  /// Lifecycle of the assessment.
  final DashboardAssessmentStatus status;

  @override
  Widget build(BuildContext context) {
    final bool completed = status == DashboardAssessmentStatus.completed;
    return Container(
      height: 24,
      padding: const EdgeInsets.symmetric(horizontal: 10),
      decoration: BoxDecoration(
        color: completed
            ? AppColors.greenSurface
            : AppColors.amberSurface,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(
          color: completed
              ? AppColors.refAutosaveCircle
              : AppColors.amberWarning,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          if (completed)
            const DashboardIcon(
              DashboardIconType.check,
              size: 12,
              color: AppColors.refAutosaveTick,
              strokeWidth: 2,
            )
          else
            const DashboardIcon(
              DashboardIconType.check,
              size: 12,
              color: AppColors.amberWarning,
              strokeWidth: 2,
            ),
          const SizedBox(width: 5),
          Text(
            completed ? 'Completed' : 'In progress',
            style: AppTextStyles.dashboardStatusBadge.copyWith(
              color: completed
                  ? AppColors.refAutosaveTick
                  : AppColors.maroonDark,
            ),
          ),
        ],
      ),
    );
  }
}

/// Abbreviated month label, e.g. `Oct`.
String _monthLabel(int month) {
  const List<String> labels = <String>[
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',
  ];
  return labels[month - 1];
}
