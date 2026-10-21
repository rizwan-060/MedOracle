import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../widgets/assessment_actions.dart';
import '../widgets/assessment_header.dart';
import '../widgets/doctor_to_see_band.dart';
import '../widgets/main_finding_card.dart';
import '../widgets/stacked_reports_card.dart';

/// Screen 6A — Main Finding.
///
/// First assessment output shown after the intake wizard is submitted
/// (design: v8 Step 6A "Stacked reports, heart on top"). The primary action
/// is handed in by the router and advances to the risk trajectory screen.
class AssessmentMainFindingScreen extends StatelessWidget {
  const AssessmentMainFindingScreen({
    super.key,
    this.onTrajectoryAction,
    this.onClose,
  });

  /// Routes forward to the risk trajectory screen (wired by the router).
  final VoidCallback? onTrajectoryAction;

  /// Leaves the results flow back to Step 5 (wired by the router).
  final VoidCallback? onClose;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.canvasBackground,
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: <Color>[
              AppColors.dustyTaupe.withValues(alpha: 0.30),
              AppColors.canvasBackground,
              AppColors.canvasBackground,
            ],
            stops: const <double>[0.0, 0.45, 1.0],
          ),
        ),
        child: SafeArea(
          bottom: false,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: <Widget>[
              AssessmentHeader(onClose: onClose),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.fromLTRB(20, 12, 20, 16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: const <Widget>[
                      MainFindingCard(),
                      DoctorToSeeBand(),
                      StackedReportsCard(),
                    ],
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: <Widget>[
                    AssessmentPrimaryAction(
                      label: 'View risk trajectory',
                      onTap: onTrajectoryAction,
                    ),
                    const SizedBox(height: 4),
                    AssessmentDonePill(
                      label: 'Done',
                      onTap: onClose,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
