import 'package:material_ui/material_ui.dart';

import '../../../core/theme/app_colors.dart';
import 'assessment_type.dart';

/// Fixed 207px header shared by the assessment intake reference screens.
class AssessmentHeader extends StatelessWidget {
  const AssessmentHeader({
    super.key,
    required this.title,
    required this.filledSteps,
    required this.onBack,
  });

  final String title;
  final int filledSteps;
  final VoidCallback onBack;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 207,
      decoration: BoxDecoration(
        color: AppColors.headerText,
        borderRadius: const BorderRadius.only(
          bottomLeft: Radius.circular(40),
          bottomRight: Radius.circular(40),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(24, 52, 24, 36),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            Row(
              children: <Widget>[
                _BackCircle(onTap: onBack),
                Expanded(
                  child: Center(child: _StepProgress(filledSteps: filledSteps)),
                ),
                const SizedBox(width: 44, height: 44),
              ],
            ),
            const SizedBox(height: 21),
            SizedBox(
              height: 28,
              child: FittedBox(
                fit: BoxFit.scaleDown,
                alignment: Alignment.centerLeft,
                child: Text(
                  title,
                  maxLines: 1,
                  style: AssessmentType.serif(
                    24,
                    FontWeight.w700,
                    AppColors.cardSurface,
                    height: 28 / 24,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 6),
            SizedBox(
              height: 20,
              child: FittedBox(
                fit: BoxFit.scaleDown,
                alignment: Alignment.centerLeft,
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: <Widget>[
                    const Icon(
                      Icons.check,
                      size: 14,
                      color: AppColors.cardSurface,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Autosaved',
                      maxLines: 1,
                      style: AssessmentType.sans(
                        14,
                        FontWeight.w400,
                        AppColors.intakeAutosaveInk,
                        height: 20 / 14,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StepProgress extends StatelessWidget {
  const _StepProgress({required this.filledSteps});

  final int filledSteps;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 150,
      height: 4,
      child: Row(
        children: List<Widget>.generate(9, (int index) {
          if (index.isOdd) return const SizedBox(width: 6);
          final int barIndex = index ~/ 2;
          return Expanded(
            child: Container(
              height: 4,
              decoration: BoxDecoration(
                color: barIndex < filledSteps
                    ? AppColors.cardSurface
                    : AppColors.cardSurface.withValues(alpha: 0.30),
                borderRadius: BorderRadius.circular(999),
              ),
            ),
          );
        }),
      ),
    );
  }
}

class _BackCircle extends StatelessWidget {
  const _BackCircle({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: Colors.transparent,
            shape: BoxShape.circle,
            border: Border.all(color: AppColors.cardSurface, width: 1.5),
          ),
          child: const Icon(
            Icons.arrow_back,
            size: 22,
            color: AppColors.cardSurface,
          ),
        ),
      ),
    );
  }
}

/// Fixed 69px footer shared by the assessment intake reference screens.
class AssessmentFooter extends StatelessWidget {
  const AssessmentFooter({
    super.key,
    required this.ctaLabel,
    required this.ctaEnabled,
    required this.ctaColor,
    required this.onBack,
    this.onContinue,
  });

  final String ctaLabel;
  final bool ctaEnabled;
  final Color ctaColor;
  final VoidCallback onBack;
  final VoidCallback? onContinue;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 69,
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 12),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        border: Border(top: BorderSide(color: AppColors.intakeLine, width: 1)),
      ),
      child: Row(
        children: <Widget>[
          SizedBox(
            width: 114,
            height: 44,
            child: _FooterPill(
              label: 'Back',
              fill: AppColors.cardSurface,
              border: Border.all(color: AppColors.intakeLine, width: 1),
              textColor: AppColors.intakeButtonLine,
              onTap: onBack,
            ),
          ),
          const SizedBox(width: 12),
          SizedBox(
            width: 224,
            height: 44,
            child: _FooterPill(
              label: ctaLabel,
              fill: ctaEnabled
                  ? ctaColor
                  : AppColors.intakeLine.withValues(alpha: 0.60),
              textColor:
                  ctaEnabled ? AppColors.cardSurface : AppColors.textMuted,
              onTap: ctaEnabled ? onContinue : null,
            ),
          ),
        ],
      ),
    );
  }
}

class _FooterPill extends StatelessWidget {
  const _FooterPill({
    required this.label,
    required this.fill,
    required this.textColor,
    required this.onTap,
    this.border,
  });

  final String label;
  final Color fill;
  final Color textColor;
  final VoidCallback? onTap;
  final BoxBorder? border;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Container(
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: fill,
            borderRadius: BorderRadius.circular(999),
            border: border,
          ),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: AssessmentType.sans(
              14,
              FontWeight.w700,
              textColor,
            ),
          ),
        ),
      ),
    );
  }
}

/// Layout shell that centers reference content between the fixed header/footer.
class AssessmentShell extends StatelessWidget {
  const AssessmentShell({
    super.key,
    required this.title,
    required this.filledSteps,
    required this.ctaLabel,
    required this.ctaEnabled,
    required this.ctaColor,
    required this.onBack,
    this.onContinue,
    this.showFooter = true,
    required this.child,
  });

  final String title;
  final int filledSteps;
  final String ctaLabel;
  final bool ctaEnabled;
  final Color ctaColor;
  final VoidCallback onBack;
  final VoidCallback? onContinue;
  final bool showFooter;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      resizeToAvoidBottomInset: false,
      backgroundColor: AppColors.canvasBackground,
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          AssessmentHeader(
            title: title,
            filledSteps: filledSteps,
            onBack: onBack,
          ),
          Expanded(
            child: Center(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: child,
              ),
            ),
          ),
          if (showFooter)
            AssessmentFooter(
              ctaLabel: ctaLabel,
              ctaEnabled: ctaEnabled,
              ctaColor: ctaColor,
              onBack: onBack,
              onContinue: onContinue,
            ),
        ],
      ),
    );
  }
}
