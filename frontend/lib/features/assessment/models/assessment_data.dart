/// Immutable models for the post-intake assessment screens (Step 6).
///
/// The `AssessmentDemoData` constants are placeholders that mirror the design
/// reference. Swap them for the decoded assessment API payload once the
/// backend contract is in place - the widgets only depend on the models.
library;

/// A single piece of patient detail that fed the reasoning map.
class ReasoningFact {
  const ReasoningFact({required this.label});

  /// Short summary shown inside the map, e.g. `Chest pain (8/10)`.
  final String label;
}

/// One specialist model that took part in the assessment.
class ReasoningModel {
  const ReasoningModel({required this.name, this.confidence});

  /// Model name, e.g. `Symptom AI`.
  final String name;

  /// Confidence in percent. `null` when the model did not report one.
  final int? confidence;
}

/// A labelled value pair rendered under "From your details".
class DetailFact {
  const DetailFact({required this.label, required this.value});

  final String label;
  final String value;
}

/// One specialist AI check together with the reasoning it produced.
class SpecialistCheck {
  const SpecialistCheck({
    required this.title,
    required this.badge,
    required this.headline,
    this.tags = const <String>[],
    this.facts = const <DetailFact>[],
    this.grid = false,
  });

  /// Name of the check, e.g. `Symptom Check`.
  final String title;

  /// Confidence label shown on the pill, e.g. `86% sure`.
  final String badge;

  /// One line conclusion drawn from the patient details.
  final String headline;

  /// Short supporting phrases.
  final List<String> tags;

  /// The details the check was derived from.
  final List<DetailFact> facts;

  /// Render [facts] as a two column grid instead of a single row.
  final bool grid;
}

/// A behaviour change that lowers the projected risk.
class RiskReductionAction {
  const RiskReductionAction({
    required this.title,
    required this.affectedFraction,
    required this.improvementFraction,
    required this.value,
  });

  /// Label of the action, e.g. `Quit smoking`.
  final String title;

  /// Share of the bar that stays affected after the change.
  final double affectedFraction;

  /// Share of the bar that drops below the "no change" projection.
  final double improvementFraction;

  /// Projected value (`22`) once the action is applied.
  final String value;
}

/// Placeholder payload mirroring the design reference.
class AssessmentDemoData {
  const AssessmentDemoData._();

  /// Patient details that fed the reasoning map.
  static const List<ReasoningFact> facts = <ReasoningFact>[
    ReasoningFact(label: 'Chest pain (8/10)'),
    ReasoningFact(label: 'Father heart attack (Age 52)'),
    ReasoningFact(label: 'BP 146 & Cholesterol 242'),
  ];

  /// Specialist models that reviewed the details.
  static const List<ReasoningModel> models = <ReasoningModel>[
    ReasoningModel(name: 'Symptom AI', confidence: 86),
    ReasoningModel(name: 'History AI', confidence: 91),
    ReasoningModel(name: 'Lab AI'),
  ];

  /// Final conclusion of the reasoning map.
  static const String resultTitle = 'Coronary Artery Disease Risk';

  /// Confidence of the final conclusion.
  static const String resultConfidence = '88.5% sure';

  /// The specialist checks that agreed on the result.
  static const List<SpecialistCheck> checks = <SpecialistCheck>[
    SpecialistCheck(
      title: 'Symptom Check',
      badge: '86% sure',
      headline: 'Chest tightness points to heart strain during activity',
      tags: <String>[
        'Triggered by brisk walking',
        'Spreads to jaw and shoulder',
        'Short relief with rest',
      ],
      facts: <DetailFact>[
        DetailFact(label: 'Severity', value: '8/10'),
        DetailFact(label: 'Duration', value: '4 days'),
      ],
    ),
    SpecialistCheck(
      title: 'Family & History Check',
      badge: '91% sure',
      headline: 'Family history and smoking both point to the heart',
      tags: <String>[
        'Father was under the age 55 threshold',
        'Current smoker status',
      ],
      facts: <DetailFact>[
        DetailFact(label: 'Father, heart attack', value: 'Age 52'),
        DetailFact(label: 'Smoking', value: 'Current'),
      ],
    ),
    SpecialistCheck(
      title: 'Lab Numbers Check',
      badge: 'High match',
      headline: 'Your lab numbers fit a heart-risk pattern',
      grid: true,
      facts: <DetailFact>[
        DetailFact(label: 'Blood pressure', value: '146/92'),
        DetailFact(label: 'Total cholesterol', value: '242'),
        DetailFact(label: 'LDL', value: '164'),
        DetailFact(label: 'HDL', value: '37'),
      ],
    ),
  ];

  /// Legal fine print shown at the bottom of the assessment screens.
  static const String disclaimer =
      'These are estimates, not predictions. MedOracle decision support only; '
      'does not provide diagnosis.';

  /// Behaviour changes ordered by how much they help.
  static const List<RiskReductionAction> actions = <RiskReductionAction>[
    RiskReductionAction(
      title: 'Quit smoking',
      affectedFraction: 0.55,
      improvementFraction: 0.175,
      value: '22',
    ),
    RiskReductionAction(
      title: 'Walk 30 minutes a day',
      affectedFraction: 0.65,
      improvementFraction: 0.075,
      value: '26',
    ),
    RiskReductionAction(
      title: 'Eat a heart-healthy diet',
      affectedFraction: 0.675,
      improvementFraction: 0.05,
      value: '27',
    ),
  ];
}
