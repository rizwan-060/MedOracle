import 'package:material_ui/material_ui.dart';

import '../../../core/theme/app_colors.dart';
import 'assessment_type.dart';

/// Collapsed stacked pile and expanded rows shared by AS2B sections.
class MedicationsFamilySection extends StatelessWidget {
  const MedicationsFamilySection({
    super.key,
    required this.title,
    required this.items,
    required this.countLabel,
    required this.expanded,
    required this.onToggle,
    required this.onRemove,
  });

  final String title;
  final List<String> items;
  final String countLabel;
  final bool expanded;
  final VoidCallback onToggle;
  final ValueChanged<int> onRemove;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        SizedBox(
          height: 22,
          child: FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Text(
              title,
              maxLines: 1,
              style: AssessmentType.jakarta(
                17,
                FontWeight.w800,
                AppColors.intakeInk,
                height: 22 / 17,
              ),
            ),
          ),
        ),
        const SizedBox(height: 14),
        if (expanded)
          Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: <Widget>[
              for (int index = 0; index < items.length; index++)
                Padding(
                  padding: EdgeInsets.only(
                    bottom: index == items.length - 1 ? 0 : 12,
                  ),
                  child: _RecordRow(
                    label: items[index],
                    onRemove: () => onRemove(index),
                  ),
                ),
              const SizedBox(height: 14),
              _ShowLess(onTap: onToggle),
            ],
          )
        else ...<Widget>[
          _CardPile(record: items.isEmpty ? '' : items.first),
          const SizedBox(height: 14),
          _ExpandPill(
            key: Key(title == 'Current Medications'
                ? 'as2b_expand_medications'
                : 'as2b_expand_family'),
            label: countLabel,
            onTap: onToggle,
          ),
        ],
      ],
    );
  }
}

class _CardPile extends StatelessWidget {
  const _CardPile({required this.record});

  final String record;

  @override
  Widget build(BuildContext context) {
    final (String, String) split = _splitRecord(record);
    final String name = split.$1;
    final String detail = split.$2;

    return SizedBox(
      height: 120,
      child: Stack(
        children: <Widget>[
          Positioned(
            left: 17.5,
            top: 32,
            child: Transform.scale(
              scale: 0.90,
              child: Container(
                width: 350,
                height: 88,
                decoration: BoxDecoration(
                  color: AppColors.intakeGhostDeepFill,
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
            ),
          ),
          Positioned(
            left: 8.75,
            top: 16,
            child: Transform.scale(
              scale: 0.95,
              child: Container(
                width: 350,
                height: 88,
                decoration: BoxDecoration(
                  color: AppColors.intakeGhostFill,
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
            ),
          ),
          Container(
            width: 350,
            height: 88,
            padding: const EdgeInsets.symmetric(horizontal: 20),
            decoration: BoxDecoration(
              color: AppColors.cardSurface,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: AppColors.intakeButtonLine, width: 1.5),
              boxShadow: <BoxShadow>[
                BoxShadow(
                  color: AppColors.intakeInk.withValues(alpha: 0.50),
                  offset: const Offset(0, 12),
                  blurRadius: 18,
                  spreadRadius: -10,
                ),
                BoxShadow(
                  color: AppColors.intakeInk.withValues(alpha: 0.08),
                  offset: const Offset(0, 2),
                  blurRadius: 4,
                ),
              ],
            ),
            child: Align(
              alignment: Alignment.centerLeft,
              child: FittedBox(
                fit: BoxFit.scaleDown,
                alignment: Alignment.centerLeft,
                child: RichText(
                  maxLines: 1,
                  text: TextSpan(
                    children: <TextSpan>[
                      TextSpan(
                        text: name,
                        style: AssessmentType.jakarta(
                          16,
                          FontWeight.w800,
                          AppColors.intakeCardInk,
                        ),
                      ),
                      TextSpan(
                        text: detail.isEmpty ? '' : ' $detail',
                        style: AssessmentType.jakarta(
                          16,
                          FontWeight.w500,
                          AppColors.intakeCardInk,
                        ),
                      ),
                    ],
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

(String, String) _splitRecord(String record) {
  final int open = record.indexOf(' (');
  if (open < 0 || !record.endsWith(')')) return (record, '');
  return (record.substring(0, open), record.substring(open + 1));
}

class _ExpandPill extends StatelessWidget {
  const _ExpandPill({super.key, required this.label, required this.onTap});

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: onTap,
        child: Container(
          height: 44,
          padding: const EdgeInsets.symmetric(horizontal: 18),
          decoration: BoxDecoration(
            color: AppColors.cardSurface,
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: AppColors.intakeButtonLine, width: 1.5),
          ),
          child: FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.center,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: <Widget>[
                Text(
                  label,
                  style: AssessmentType.sans(
                    13,
                    FontWeight.w800,
                    AppColors.intakeButtonInk,
                  ),
                ),
                Text(
                  ' Tap to expand',
                  style: AssessmentType.sans(
                    11,
                    FontWeight.w700,
                    AppColors.intakeButtonInk,
                  ),
                ),
                const SizedBox(width: 4),
                const Icon(
                  Icons.keyboard_arrow_down,
                  size: 18,
                  color: AppColors.intakeButtonInk,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
class _RecordRow extends StatelessWidget {
  const _RecordRow({required this.label, required this.onRemove});

  final String label;
  final VoidCallback onRemove;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 56,
      padding: const EdgeInsets.symmetric(horizontal: 14),
      decoration: BoxDecoration(
        color: AppColors.intakeRowFill,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.intakeRowBorder, width: 1.5),
      ),
      child: Row(
        children: <Widget>[
          Expanded(
            child: FittedBox(
              fit: BoxFit.scaleDown,
              alignment: Alignment.centerLeft,
              child: Text(
                label,
                maxLines: 1,
                style: AssessmentType.jakarta(
                  14,
                  FontWeight.w700,
                  AppColors.intakeInk,
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: onRemove,
            child: Container(
              width: 26,
              height: 26,
              decoration: BoxDecoration(
                color: AppColors.cardSurface,
                shape: BoxShape.circle,
                border:
                    Border.all(color: AppColors.intakeButtonLine, width: 1.5),
              ),
              child: const Icon(
                Icons.close,
                size: 13,
                color: AppColors.intakeButtonLine,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ShowLess extends StatelessWidget {
  const _ShowLess({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          child: Text(
            'Show less',
            style: AssessmentType.sans(
              13,
              FontWeight.w800,
              AppColors.intakeButtonInk,
            ),
          ),
        ),
      ),
    );
  }
}
