import 'package:flutter/material.dart';
import 'package:medoracle/core/theme/app_colors.dart';
import 'package:medoracle/core/theme/app_text_styles.dart';
import 'package:medoracle/core/widgets/assessment_section_card.dart';
import 'package:medoracle/core/widgets/disclaimer_text.dart';
import 'package:medoracle/core/widgets/glass_pill_button.dart';
import 'package:medoracle/core/widgets/gradient_cta_button.dart';
import 'package:medoracle/features/intake_wizard/models/assessment_data.dart';
import 'package:medoracle/features/intake_wizard/widgets/doubt_warning_card.dart';
import 'package:medoracle/features/intake_wizard/widgets/reasoning_map_chart.dart';
import 'package:medoracle/features/intake_wizard/widgets/specialist_check_stack.dart';
import 'package:medoracle/features/assessment/widgets/assessment_header.dart';

/// First assessment screen of the intake flow.
///
/// It explains *how* the result was reached: the reasoning map, the three
/// specialist checks and the doubt that was raised before the models agreed.
class FirstAssessmentScreen extends StatefulWidget {
  const FirstAssessmentScreen({
    super.key,
    this.onPrimaryAction,
    this.onSecondaryAction,
    this.onClose,
    this.confidence = '88.5%',
    this.facts = AssessmentDemoData.facts,
    this.models = AssessmentDemoData.models,
    this.checks = AssessmentDemoData.checks,
  });

  /// Wired to the primary button - route forward to the risk trajectory
  /// screen (`RouteNames.resultsTrajectory`).
  final VoidCallback? onPrimaryAction;

  /// Wired to the secondary button - go back to the results
  /// (`RouteNames.resultsReports`).
  final VoidCallback? onSecondaryAction;

  /// Wired to the close button (`RouteNames.resultsReports`).
  final VoidCallback? onClose;

  /// Confidence of the final conclusion.
  final String confidence;

  /// Patient details that fed the reasoning map.
  final List<ReasoningFact> facts;

  /// Specialist models that reviewed the details.
  final List<ReasoningModel> models;

  /// Specialist checks that agreed on the result.
  final List<SpecialistCheck> checks;

  @override
  State<FirstAssessmentScreen> createState() => _FirstAssessmentScreenState();
}

class _FirstAssessmentScreenState extends State<FirstAssessmentScreen> {
  int _selectedCheck = 0;

  void _placeholder(BuildContext context, String destination) {
    debugPrint(
      '[MedOracle] TODO: route to "$destination" from FirstAssessmentScreen.',
    );
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('TODO: route to $destination')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final String badge = widget.checks.isEmpty
        ? ''
        : widget.checks[_selectedCheck.clamp(0, widget.checks.length - 1)].badge;

    return Scaffold(
      backgroundColor: AppColors.refCanvasBottom,
      body: DecoratedBox(
        decoration: const BoxDecoration(gradient: AppColors.canvasGradient),
        child: SafeArea(
          bottom: false,
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(0, 0, 0, 28),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                AssessmentHeader(
                  onClose:
                      widget.onClose ?? () => _placeholder(context, 'close'),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: <Widget>[
                      const SizedBox(height: 18),
                      const Text(
                        'HOW OUR AI REACHED THIS RESULT',
                        style: AppTextStyles.eyebrow,
                      ),
                      const SizedBox(height: 8),
                      Text.rich(
                        TextSpan(
                          children: <InlineSpan>[
                            const TextSpan(text: 'Why we are '),
                            TextSpan(
                              text: '${widget.confidence}% sure',
                              style: AppTextStyles.resultsHeadlineAccent,
                            ),
                          ],
                        ),
                        style: AppTextStyles.resultsHeadline,
                      ),
                      const SizedBox(height: 10),
                      const Text(
                        '3 specialist AI checks reviewed your details separately and '
                        'agreed.',
                        style: AppTextStyles.resultsBody,
                      ),
                      const SizedBox(height: 22),
                      AssessmentSectionCard(
                        stepNumber: '1',
                        title: 'Visual reasoning map',
                        subtitle: 'How your details became the result',
                        child: ReasoningMapChart(
                          facts: widget.facts,
                          models: widget.models,
                          resultTitle: AssessmentDemoData.resultTitle,
                          resultConfidence: AssessmentDemoData.resultConfidence,
                        ),
                      ),
                      const SizedBox(height: 20),
                      AssessmentSectionCard(
                        stepNumber: '2',
                        title: 'The 3 specialist checks',
                        subtitle: 'Tap the paper behind to read the next one',
                        emphasized: true,
                        trailing: _HeaderPill(label: badge),
                        child: SpecialistCheckStack(
                          checks: widget.checks,
                          onIndexChanged: (int index) =>
                              setState(() => _selectedCheck = index),
                        ),
                      ),
                      const SizedBox(height: 20),
                      AssessmentSectionCard(
                        stepNumber: '3',
                        title: 'What our AI debated',
                        subtitle: 'We challenged the result before agreeing',
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: <Widget>[
                            const DoubtRaisedCard(
                              message:
                                  'Could this just be muscle strain, since it only '
                                  'started 4 days ago?',
                            ),
                            const VerticalFlowArrow(),
                            const RuledOutCard(
                              message:
                                  'Pain spreading to the jaw during walking, '
                                  'combined with these, points to the heart:',
                              highlights: <String>[
                                'Cholesterol 242',
                                'BP 146',
                                'Family history',
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),
                      const DisclaimerText(),
                      const SizedBox(height: 16),
                      GradientCtaButton(
                        label: 'View risk trajectory',
                        onPressed: widget.onPrimaryAction ??
                            () => _placeholder(context, 'risk trajectory'),
                      ),
                      const SizedBox(height: 10),
                      GlassPillButton.footer(
                        label: 'Back to results',
                        onTap: widget.onSecondaryAction ??
                            () => _placeholder(context, 'results'),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Small pill rendered in the header of the highlighted section.
class _HeaderPill extends StatelessWidget {
  const _HeaderPill({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      height: 32,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: AppColors.cardSurface.withValues(alpha: 0.60),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.borderSubtle, width: 1.5),
      ),
      child: Text(
        label,
        style: AppTextStyles.chipLabel.copyWith(
          fontWeight: FontWeight.w800,
          color: AppColors.refPlum,
        ),
      ),
    );
  }
}