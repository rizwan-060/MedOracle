import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:material_ui/material_ui.dart';

import '../../../core/theme/app_colors.dart';
import '../providers/clinical_status_provider.dart';
import 'assessment_type.dart';

enum ClinicalStatusSheetKind { surgery, allergy, notes }

/// Opens the 265px bottom sheet used by the done-state detail tiles.
Future<void> showClinicalStatusSheet({
  required BuildContext context,
  required ClinicalStatusSheetKind kind,
}) {
  return showModalBottomSheet<void>(
    context: context,
    backgroundColor: AppColors.cardSurface,
    barrierColor: AppColors.intakeInk.withValues(alpha: 0.45),
    isScrollControlled: false,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.only(
        topLeft: Radius.circular(24),
        topRight: Radius.circular(24),
      ),
    ),
    builder: (BuildContext context) => SizedBox(
      height: 265,
      child: ClinicalStatusEditorSheet(kind: kind),
    ),
  );
}

class ClinicalStatusEditorSheet extends ConsumerStatefulWidget {
  const ClinicalStatusEditorSheet({super.key, required this.kind});

  final ClinicalStatusSheetKind kind;

  @override
  ConsumerState<ClinicalStatusEditorSheet> createState() =>
      _ClinicalStatusEditorSheetState();
}

class _ClinicalStatusEditorSheetState
    extends ConsumerState<ClinicalStatusEditorSheet> {
  late final TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(
      text: widget.kind == ClinicalStatusSheetKind.notes
          ? ref.read(clinicalStatusProvider).notes
          : '',
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  String get _title => switch (widget.kind) {
        ClinicalStatusSheetKind.surgery => 'Add past surgery',
        ClinicalStatusSheetKind.allergy => 'Add allergy',
        ClinicalStatusSheetKind.notes => 'Additional notes',
      };

  String get _subtitle => switch (widget.kind) {
        ClinicalStatusSheetKind.surgery =>
          'Operations or procedures you have had.',
        ClinicalStatusSheetKind.allergy =>
          'Anything that gives you a reaction.',
        ClinicalStatusSheetKind.notes => '',
      };

  String get _hint => switch (widget.kind) {
        ClinicalStatusSheetKind.surgery => 'e.g., Appendectomy',
        ClinicalStatusSheetKind.allergy => 'e.g., Penicillin',
        ClinicalStatusSheetKind.notes => '',
      };

  void _add() {
    final String value = _controller.text.trim();
    if (value.isEmpty) return;
    final ClinicalStatusController controller =
        ref.read(clinicalStatusProvider.notifier);
    if (widget.kind == ClinicalStatusSheetKind.surgery) {
      controller.addSurgery(value);
    } else if (widget.kind == ClinicalStatusSheetKind.allergy) {
      controller.addAllergy(value);
    }
    _controller.clear();
  }

  void _close() => Navigator.of(context).pop();

  @override
  Widget build(BuildContext context) {
    final ClinicalStatusState state = ref.watch(clinicalStatusProvider);
    final bool isNotes = widget.kind == ClinicalStatusSheetKind.notes;
    final List<String> items = switch (widget.kind) {
      ClinicalStatusSheetKind.surgery => state.surgeries,
      ClinicalStatusSheetKind.allergy => state.allergies,
      ClinicalStatusSheetKind.notes => const <String>[],
    };

    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          SizedBox(
            height: 24,
            child: FittedBox(
              fit: BoxFit.scaleDown,
              alignment: Alignment.centerLeft,
              child: Text(
                _title,
                maxLines: 1,
                style: AssessmentType.sans(
                  17,
                  FontWeight.w700,
                  AppColors.intakeInk,
                ),
              ),
            ),
          ),
          if (_subtitle.isNotEmpty) ...<Widget>[
            const SizedBox(height: 4),
            SizedBox(
              height: 18,
              child: FittedBox(
                fit: BoxFit.scaleDown,
                alignment: Alignment.centerLeft,
                child: Text(
                  _subtitle,
                  maxLines: 1,
                  style: AssessmentType.sans(
                    13,
                    FontWeight.w400,
                    AppColors.textMuted,
                  ),
                ),
              ),
            ),
          ],
          const SizedBox(height: 12),
          if (isNotes)
            SizedBox(
              height: 104,
              child: TextField(
                controller: _controller,
                maxLines: 4,
                onChanged: ref.read(clinicalStatusProvider.notifier).setNotes,
                decoration: _fieldDecoration(''),
              ),
            )
          else
            SizedBox(
              height: 48,
              child: TextField(
                controller: _controller,
                decoration: _fieldDecoration(_hint),
              ),
            ),
          const SizedBox(height: 10),
          if (!isNotes)
            SizedBox(
              height: 30,
              child: Wrap(
                spacing: 8,
                runSpacing: 6,
                children: items
                    .map(
                      (String item) => _Chip(
                        label: item,
                        onRemove: () {
                          if (widget.kind == ClinicalStatusSheetKind.surgery) {
                            ref
                                .read(clinicalStatusProvider.notifier)
                                .removeSurgery(item);
                          } else {
                            ref
                                .read(clinicalStatusProvider.notifier)
                                .removeAllergy(item);
                          }
                        },
                      ),
                    )
                    .toList(),
              ),
            ),
          const Spacer(),
          if (!isNotes)
            Row(
              children: <Widget>[
                SizedBox(
                  width: 167,
                  height: 44,
                  child: _SheetButton(
                    label: 'Add',
                    fill: AppColors.headerText,
                    textColor: AppColors.cardSurface,
                    onTap: _add,
                  ),
                ),
                const SizedBox(width: 12),
                SizedBox(
                  width: 171,
                  height: 44,
                  child: _SheetButton(
                    label: 'Done',
                    fill: AppColors.cardSurface,
                    textColor: AppColors.headerText,
                    border: Border.all(color: AppColors.intakeButtonLine),
                    onTap: _close,
                  ),
                ),
              ],
            )
          else
            SizedBox(
              width: 350,
              height: 44,
              child: _SheetButton(
                label: 'Done',
                fill: AppColors.cardSurface,
                textColor: AppColors.headerText,
                border: Border.all(color: AppColors.intakeButtonLine),
                onTap: _close,
              ),
            ),
        ],
      ),
    );
  }

  InputDecoration _fieldDecoration(String hint) {
    final OutlineInputBorder border = OutlineInputBorder(
      borderRadius: BorderRadius.circular(16),
      borderSide: BorderSide(color: AppColors.intakeButtonLine, width: 1),
    );
    return InputDecoration(
      filled: true,
      fillColor: AppColors.cardSurface,
      hintText: hint,
      hintStyle: AssessmentType.sans(
        13,
        FontWeight.w400,
        AppColors.textMuted,
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      enabledBorder: border,
      focusedBorder: border,
      border: border,
    );
  }
}

class _Chip extends StatelessWidget {
  const _Chip({required this.label, required this.onRemove});

  final String label;
  final VoidCallback onRemove;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 30,
      padding: const EdgeInsets.only(left: 12, right: 6),
      decoration: BoxDecoration(
        color: AppColors.secondarySurface,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Text(
            label,
            style: AssessmentType.sans(
              12,
              FontWeight.w600,
              AppColors.intakeSlateDark,
            ),
          ),
          const SizedBox(width: 4),
          GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: onRemove,
            child: const Padding(
              padding: EdgeInsets.all(3),
              child: Icon(
                Icons.close,
                size: 12,
                color: AppColors.intakeButtonLine,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _SheetButton extends StatelessWidget {
  const _SheetButton({
    required this.label,
    required this.fill,
    required this.textColor,
    required this.onTap,
    this.border,
  });

  final String label;
  final Color fill;
  final Color textColor;
  final VoidCallback onTap;
  final Border? border;

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
