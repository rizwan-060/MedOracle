import 'dart:math' as math;

import 'package:material_ui/material_ui.dart';

import '../../../core/theme/app_colors.dart';
import 'assessment_type.dart';

void _noopRemove(String _) {}

/// Condition entry card used by the empty and adding states of AS2A.
class ClinicalStatusSearchCard extends StatelessWidget {
  const ClinicalStatusSearchCard.empty({
    super.key,
    required this.controller,
    required this.focusNode,
    required this.suggestionsVisible,
    required this.onSearchTap,
    required this.onQueryChanged,
    required this.onSuggestion,
    required this.onDoneAdding,
    required this.onNoConditions,
  })  : conditions = const <String>[],
        onRemoveCondition = _noopRemove,
        showFan = false;

  const ClinicalStatusSearchCard.adding({
    super.key,
    required this.controller,
    required this.focusNode,
    required this.conditions,
    required this.onSearchTap,
    required this.onQueryChanged,
    required this.onSuggestion,
    required this.onRemoveCondition,
    required this.onDoneAdding,
  })  : suggestionsVisible = false,
        onNoConditions = null,
        showFan = true;

  final TextEditingController controller;
  final FocusNode focusNode;
  final List<String> conditions;
  final bool showFan;
  final bool suggestionsVisible;
  final VoidCallback onSearchTap;
  final ValueChanged<String> onQueryChanged;
  final ValueChanged<String> onSuggestion;
  final ValueChanged<String> onRemoveCondition;
  final VoidCallback onDoneAdding;
  final VoidCallback? onNoConditions;

  static const List<String> suggestions = <String>[
    'Hypertension',
    'Dyslipidemia',
    'Type 2 diabetes',
    'Asthma',
    'Hypothyroidism',
  ];

  @override
  Widget build(BuildContext context) {
    return Stack(
      clipBehavior: Clip.none,
      children: <Widget>[
        Container(
          width: 350,
          height: showFan ? 344 : 224,
          padding: const EdgeInsets.fromLTRB(17, 17, 15, 17),
          decoration: BoxDecoration(
            color: AppColors.cardSurface,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: AppColors.intakeLine, width: 1),
            boxShadow: <BoxShadow>[
              BoxShadow(
                color: AppColors.intakeInk.withValues(alpha: 0.35),
                offset: const Offset(0, 18),
                blurRadius: 30,
                spreadRadius: -20,
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: <Widget>[
              if (!showFan) ...<Widget>[
                SizedBox(
                  height: 25.5,
                  child: FittedBox(
                    fit: BoxFit.scaleDown,
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Current Health Conditions',
                      maxLines: 1,
                      style: AssessmentType.jakarta(
                        17,
                        FontWeight.w800,
                        AppColors.intakeInk,
                        height: 25.5 / 17,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 4),
                SizedBox(
                  height: 20,
                  child: FittedBox(
                    fit: BoxFit.scaleDown,
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Add any health issues you are currently dealing with.',
                      maxLines: 1,
                      style: AssessmentType.jakarta(
                        13,
                        FontWeight.w400,
                        AppColors.textMuted,
                        height: 20 / 13,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 14),
              ],
              if (showFan) _ConditionFan(
                conditions: conditions,
                onRemove: onRemoveCondition,
              ),
              if (showFan) const SizedBox(height: 16),
              _SearchField(
                controller: controller,
                focusNode: focusNode,
                onTap: onSearchTap,
                onChanged: onQueryChanged,
              ),
              const SizedBox(height: 14),
              if (showFan)
                SizedBox(
                  width: 316,
                  height: 44,
                  child: _ActionPill(
                    label: 'Done adding',
                    width: 316,
                    height: 44,
                    fill: AppColors.headerText,
                    textColor: AppColors.cardSurface,
                    border: null,
                    onTap: onDoneAdding,
                  ),
                )
              else
                Row(
                  children: <Widget>[
                    SizedBox(
                      width: 150,
                      height: 44,
                      child: _ActionPill(
                        label: 'Done adding',
                        width: 150,
                        height: 44,
                        fill: AppColors.headerText,
                        textColor: AppColors.cardSurface,
                        border: null,
                        onTap: onDoneAdding,
                      ),
                    ),
                    const SizedBox(width: 12),
                    SizedBox(
                      width: 154,
                      height: 44,
                      child: _ActionPill(
                        label: "I don't have any",
                        width: 154,
                        height: 44,
                        fill: AppColors.cardSurface,
                        textColor: AppColors.intakeButtonInk,
                        border: Border.all(
                          color: AppColors.intakeButtonLine,
                          width: 2,
                        ),
                        onTap: onNoConditions ?? () {},
                      ),
                    ),
                  ],
                ),
            ],
          ),
        ),
        if (suggestionsVisible)
          Positioned(
            left: 17,
            top: 142,
            child: _Suggestions(
              onPick: onSuggestion,
            ),
          ),
      ],
    );
  }
}

class _SearchField extends StatelessWidget {
  const _SearchField({
    required this.controller,
    required this.focusNode,
    required this.onTap,
    required this.onChanged,
  });

  final TextEditingController controller;
  final FocusNode focusNode;
  final VoidCallback onTap;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    final OutlineInputBorder border = OutlineInputBorder(
      borderRadius: BorderRadius.circular(16),
      borderSide: BorderSide(color: AppColors.intakeButtonLine, width: 1),
    );

    return SizedBox(
      height: 48,
      child: TextField(
        controller: controller,
        focusNode: focusNode,
        onTap: onTap,
        onChanged: onChanged,
        decoration: InputDecoration(
          filled: true,
          fillColor: AppColors.cardSurface,
          hintText: 'Search or add conditions...',
          hintStyle: AssessmentType.sans(
            13,
            FontWeight.w400,
            AppColors.textMuted,
          ),
          prefixIcon: const Icon(
            Icons.search,
            size: 20,
            color: AppColors.intakeButtonLine,
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 14),
          enabledBorder: border,
          focusedBorder: border,
          border: border,
        ),
        style: AssessmentType.sans(
          13,
          FontWeight.w500,
          AppColors.intakeInk,
        ),
      ),
    );
  }
}

class _ConditionFan extends StatelessWidget {
  const _ConditionFan({required this.conditions, required this.onRemove});

  final List<String> conditions;
  final ValueChanged<String> onRemove;

  @override
  Widget build(BuildContext context) {
    const double cardWidth = 108;
    const double cardHeight = 148;
    const double step = 22;
    final double span = cardWidth + step * (conditions.length - 1);
    final double startLeft = (316 - span) / 2;

    return SizedBox(
      height: cardHeight,
      child: Stack(
        clipBehavior: Clip.none,
        children: List<Widget>.generate(conditions.length, (int index) {
          final double rotation = conditions.length == 1
              ? 0
              : (-5.6 + 11.2 * index / (conditions.length - 1)) *
                  math.pi /
                  180;
          return Positioned(
            left: startLeft + step * index,
            top: 0,
            child: Transform.rotate(
              angle: rotation,
              child: _FanCard(
                name: conditions[index],
                first: index == 0,
                onRemove: () => onRemove(conditions[index]),
              ),
            ),
          );
        }),
      ),
    );
  }
}

class _FanCard extends StatelessWidget {
  const _FanCard({
    required this.name,
    required this.first,
    required this.onRemove,
  });

  final String name;
  final bool first;
  final VoidCallback onRemove;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: <Widget>[
        Container(
          width: 108,
          height: 148,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: first ? AppColors.intakeFanFill : AppColors.cardSurface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.intakeButtonLine, width: 1),
          ),
          child: Align(
            alignment: Alignment.topCenter,
            child: Text(
              name,
              textAlign: TextAlign.center,
              maxLines: 3,
              style: AssessmentType.jakarta(
                11.5,
                FontWeight.w800,
                AppColors.intakeInk,
                height: 1.2,
              ),
            ),
          ),
        ),
        Positioned(
          top: 5,
          right: 5,
          child: GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: onRemove,
            child: Container(
              width: 20,
              height: 20,
              decoration: const BoxDecoration(
                color: AppColors.cardSurface,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.close,
                size: 12,
                color: AppColors.intakeButtonLine,
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _Suggestions extends StatelessWidget {
  const _Suggestions({required this.onPick});

  final ValueChanged<String> onPick;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 316,
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.intakeLine, width: 1),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.intakeInk.withValues(alpha: 0.12),
            blurRadius: 16,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: ClinicalStatusSearchCard.suggestions
            .map((String name) => _SuggestionRow(
                  name: name,
                  onTap: () => onPick(name),
                ))
            .toList(),
      ),
    );
  }
}

class _SuggestionRow extends StatelessWidget {
  const _SuggestionRow({required this.name, required this.onTap});

  final String name;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        child: Container(
          height: 36,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          alignment: Alignment.centerLeft,
          child: Text(
            name,
            style: AssessmentType.sans(
              14,
              FontWeight.w500,
              AppColors.intakeSlateDark,
            ),
          ),
        ),
      ),
    );
  }
}

class _ActionPill extends StatelessWidget {
  const _ActionPill({
    required this.label,
    required this.width,
    required this.height,
    required this.fill,
    required this.textColor,
    required this.border,
    required this.onTap,
  });

  final String label;
  final double width;
  final double height;
  final Color fill;
  final Color textColor;
  final Border? border;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      height: height,
      child: Material(
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
                13,
                FontWeight.w700,
                textColor,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
