import 'package:material_ui/material_ui.dart';

import '../../../core/theme/app_colors.dart';
import 'assessment_type.dart';

/// Done-state summary for AS2A: conditions accordion, detail tiles, notes pill.
class ClinicalStatusDoneView extends StatelessWidget {
  const ClinicalStatusDoneView({
    super.key,
    required this.conditions,
    required this.surgeries,
    required this.allergies,
    required this.expanded,
    required this.onToggle,
    required this.onEdit,
    required this.onSurgeryTap,
    required this.onAllergyTap,
    required this.onNotesTap,
  });

  final List<String> conditions;
  final List<String> surgeries;
  final List<String> allergies;
  final bool expanded;
  final VoidCallback onToggle;
  final VoidCallback onEdit;
  final VoidCallback onSurgeryTap;
  final VoidCallback onAllergyTap;
  final VoidCallback onNotesTap;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        _ConditionsAccordion(
          conditions: conditions,
          expanded: expanded,
          onToggle: onToggle,
          onEdit: onEdit,
        ),
        const SizedBox(height: 20),
        Row(
          children: <Widget>[
            SizedBox(
              width: 168,
              height: 180,
              child: _DetailTile(
                title: 'Past surgery',
                subtitle: surgeries.isEmpty
                    ? 'Tap to add'
                    : '${surgeries.length} added',
                fill: AppColors.onboardingPeachSurface,
                border: BorderSide(color: AppColors.onboardingPeachBorder),
                icon: Icons.healing_outlined,
                iconColor: AppColors.terraCotta,
                onTap: onSurgeryTap,
              ),
            ),
            const SizedBox(width: 14),
            SizedBox(
              width: 168,
              height: 180,
              child: _DetailTile(
                title: 'Known allergies',
                subtitle: allergies.isEmpty
                    ? 'Tap to add'
                    : '${allergies.length} added',
                fill: AppColors.intakeSageFill,
                border: BorderSide(color: AppColors.intakeSageBorder),
                icon: Icons.coronavirus_outlined,
                iconColor: AppColors.intakeAllergyIcon,
                onTap: onAllergyTap,
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),
        _NotesPill(onTap: onNotesTap),
      ],
    );
  }
}

class _ConditionsAccordion extends StatelessWidget {
  const _ConditionsAccordion({
    required this.conditions,
    required this.expanded,
    required this.onToggle,
    required this.onEdit,
  });

  final List<String> conditions;
  final bool expanded;
  final VoidCallback onToggle;
  final VoidCallback onEdit;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: onToggle,
      child: Container(
        width: 350,
        decoration: BoxDecoration(
          color: AppColors.intakeMistFill,
          borderRadius: BorderRadius.circular(22),
          border: Border.all(color: AppColors.intakeMistBorder, width: 1),
          boxShadow: <BoxShadow>[
            BoxShadow(
              color: AppColors.headerText.withValues(alpha: 0.50),
              offset: const Offset(0, 12),
              blurRadius: 24,
              spreadRadius: -18,
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            SizedBox(
              height: 56,
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Row(
                  children: <Widget>[
                    Container(
                      width: 24,
                      height: 24,
                      decoration: const BoxDecoration(
                        color: AppColors.mutedGreen,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.check,
                        size: 14,
                        color: AppColors.cardSurface,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        '${conditions.length} Health conditions added',
                        style: AssessmentType.sans(
                          14,
                          FontWeight.w700,
                          AppColors.intakeSlateDark,
                        ),
                      ),
                    ),
                    AnimatedRotation(
                      turns: expanded ? 0.5 : 0,
                      duration: const Duration(milliseconds: 220),
                      child: const Icon(
                        Icons.keyboard_arrow_down,
                        size: 22,
                        color: AppColors.intakeSlateDark,
                      ),
                    ),
                    const SizedBox(width: 8),
                    GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTap: onEdit,
                      child: const Padding(
                        padding: EdgeInsets.all(4),
                        child: Icon(
                          Icons.edit_outlined,
                          size: 18,
                          color: AppColors.intakeSlateDark,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            if (expanded && conditions.isNotEmpty)
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                child: Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: conditions
                      .map(
                        (String condition) => Container(
                          height: 34,
                          padding: const EdgeInsets.symmetric(horizontal: 14),
                          decoration: BoxDecoration(
                            color: AppColors.cardSurface,
                            borderRadius: BorderRadius.circular(999),
                            border: Border.all(
                              color: AppColors.intakeMistBorder,
                              width: 1,
                            ),
                          ),
                          child: Center(
                            child: Text(
                              condition,
                              style: AssessmentType.sans(
                                13,
                                FontWeight.w600,
                                AppColors.intakeSlateDark,
                              ),
                            ),
                          ),
                        ),
                      )
                      .toList(),
                ),
              ),
            if (expanded && conditions.isEmpty) const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}

class _DetailTile extends StatelessWidget {
  const _DetailTile({
    required this.title,
    required this.subtitle,
    required this.fill,
    required this.border,
    required this.icon,
    required this.iconColor,
    required this.onTap,
  });

  final String title;
  final String subtitle;
  final Color fill;
  final BorderSide border;
  final IconData icon;
  final Color iconColor;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: fill,
          borderRadius: BorderRadius.circular(22),
          border: Border.fromBorderSide(border),
        ),
        child: Stack(
          children: <Widget>[
            Positioned.fill(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: <Widget>[
                  Container(
                    width: 54,
                    height: 54,
                    decoration: const BoxDecoration(
                      color: AppColors.cardSurface,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(icon, size: 26, color: iconColor),
                  ),
                  const SizedBox(height: 14),
                  Text(
                    title,
                    style: AssessmentType.sans(
                      15,
                      FontWeight.w600,
                      AppColors.intakeInk,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: AssessmentType.sans(
                      12.5,
                      FontWeight.w400,
                      AppColors.intakeMutedInk,
                    ),
                  ),
                ],
              ),
            ),
            Positioned(
              top: 12,
              right: 12,
              child: Container(
                width: 28,
                height: 28,
                decoration: const BoxDecoration(
                  color: AppColors.cardSurface,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.add,
                  size: 16,
                  color: AppColors.intakeSlateDark,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _NotesPill extends StatelessWidget {
  const _NotesPill({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: onTap,
      child: Container(
        width: 350,
        height: 56,
        decoration: BoxDecoration(
          color: AppColors.intakeSandFill,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: AppColors.intakeSandBorder, width: 1.5),
        ),
        child: Center(
          child: RichText(
            text: TextSpan(
              children: <TextSpan>[
                TextSpan(
                  text: '+ Add additional notes',
                  style: AssessmentType.sans(
                    14,
                    FontWeight.w600,
                    AppColors.intakeSlateDark,
                  ),
                ),
                TextSpan(
                  text: ' (Optional)',
                  style: AssessmentType.sans(
                    14,
                    FontWeight.w400,
                    AppColors.intakeMutedInk,
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
