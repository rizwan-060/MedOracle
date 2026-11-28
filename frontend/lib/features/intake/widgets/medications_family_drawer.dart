import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:material_ui/material_ui.dart';

import '../../../core/theme/app_colors.dart';
import '../providers/as2b_meds_family_provider.dart';
import 'assessment_type.dart';

/// Bottom drawer for adding medication and family history records.
class MedicationsFamilyDrawer extends ConsumerStatefulWidget {
  const MedicationsFamilyDrawer({super.key});

  static const double openHeight = 440;
  static const double closedHeight = 76;

  static const List<String> relatives = <String>[
    'Father',
    'Mother',
    'Brother',
    'Sister',
    'Grandparent',
    'Child',
  ];

  static const List<String> frequencies = <String>[
    'Once Daily',
    'Twice Daily',
    'At Night',
    'As Needed',
  ];

  @override
  ConsumerState<MedicationsFamilyDrawer> createState() =>
      _MedicationsFamilyDrawerState();
}

class _MedicationsFamilyDrawerState
    extends ConsumerState<MedicationsFamilyDrawer> {
  late final TextEditingController _conditionController;
  late final TextEditingController _medicineController;

  @override
  void initState() {
    super.initState();
    final As2bMedsFamilyState current = ref.read(as2bMedsFamilyProvider);
    _conditionController = TextEditingController(text: current.condition);
    _medicineController = TextEditingController(text: current.medicine);
  }

  @override
  void dispose() {
    _conditionController.dispose();
    _medicineController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final As2bMedsFamilyState state = ref.watch(as2bMedsFamilyProvider);
    final As2bMedsFamilyController controller =
        ref.read(as2bMedsFamilyProvider.notifier);

    return AnimatedContainer(
      duration: const Duration(milliseconds: 260),
      curve: Curves.easeOut,
      height: state.drawerOpen
          ? MedicationsFamilyDrawer.openHeight
          : MedicationsFamilyDrawer.closedHeight,
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: AppColors.intakeDrawerSurface,
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(24),
          topRight: Radius.circular(24),
        ),
        border: const Border(
          top: BorderSide(color: AppColors.intakeDrawerBorder, width: 2),
        ),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.intakeButtonInk.withValues(alpha: 0.45),
            offset: const Offset(0, -14),
            blurRadius: 30,
            spreadRadius: -12,
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 16),
        child: SingleChildScrollView(
          physics: const NeverScrollableScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: <Widget>[
              Center(
                child: GestureDetector(
                  key: const Key('as2b_drawer_handle'),
                  behavior: HitTestBehavior.opaque,
                  onTap: controller.toggleDrawer,
                  child: Container(
                    width: 44,
                    height: 18,
                    alignment: Alignment.center,
                    child: Container(
                      width: 44,
                      height: 5,
                      decoration: BoxDecoration(
                        color: AppColors.intakeGhostFill,
                        borderRadius: BorderRadius.circular(999),
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 6),
              SizedBox(
                height: 22,
                child: FittedBox(
                  fit: BoxFit.scaleDown,
                  alignment: Alignment.centerLeft,
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      Container(
                        width: 8,
                        height: 8,
                        decoration: const BoxDecoration(
                          color: AppColors.cardSurface,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Add to your history',
                        style: AssessmentType.sans(
                          15,
                          FontWeight.w800,
                          AppColors.cardSurface,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              if (state.drawerOpen) ...<Widget>[
                const SizedBox(height: 12),
                _SegmentedTabs(
                  activeTab: state.activeTab,
                  onChanged: controller.setTab,
                ),
                const SizedBox(height: 14),
                if (state.activeTab == As2bHistoryTab.family) ...<Widget>[
                  _FieldLabel('Relative'),
                  const SizedBox(height: 6),
                  _SelectField<String>(
                    value: state.relative,
                    items: MedicationsFamilyDrawer.relatives,
                    onChanged: (String? value) {
                      if (value != null) controller.setRelative(value);
                    },
                  ),
                  const SizedBox(height: 12),
                  _FieldLabel('Age at diagnosis'),
                  const SizedBox(height: 6),
                  _StepperField(
                    value: '${state.age}',
                    onDecrement: () => controller.setAge(state.age - 1),
                    onIncrement: () => controller.setAge(state.age + 1),
                  ),
                  const SizedBox(height: 12),
                  _FieldLabel('Condition'),
                  const SizedBox(height: 6),
                  _TextField(
                    controller: _conditionController,
                    hint: 'Search or type a condition',
                    onChanged: controller.setCondition,
                  ),
                ] else ...<Widget>[
                  _FieldLabel('Medicine name'),
                  const SizedBox(height: 6),
                  _TextField(
                    controller: _medicineController,
                    hint: 'Search or type a medicine',
                    onChanged: controller.setMedicine,
                  ),
                  const SizedBox(height: 12),
                  _FieldLabel('How often'),
                  const SizedBox(height: 6),
                  _SelectField<String>(
                    value: state.frequency,
                    items: MedicationsFamilyDrawer.frequencies,
                    onChanged: (String? value) {
                      if (value != null) controller.setFrequency(value);
                    },
                  ),
                  const SizedBox(height: 12),
                  _FieldLabel('Dose (mg)'),
                  const SizedBox(height: 6),
                  _StepperField(
                    value: '${state.dose}',
                    onDecrement: () => controller.setDose(state.dose - 5),
                    onIncrement: () => controller.setDose(state.dose + 5),
                  ),
                ],
                const SizedBox(height: 14),
                SizedBox(
                  width: 350,
                  height: 50,
                  child: Material(
                    color: Colors.transparent,
                    child: InkWell(
                      onTap: () {
                        FocusScope.of(context).unfocus();
                        controller.saveRecord();
                      },
                      borderRadius: BorderRadius.circular(999),
                      child: Container(
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          color: AppColors.intakeSaveButton,
                          borderRadius: BorderRadius.circular(999),
                          boxShadow: <BoxShadow>[
                            BoxShadow(
                              color: AppColors.intakeSaveButton
                                  .withValues(alpha: 0.35),
                              offset: const Offset(0, 4),
                              blurRadius: 12,
                            ),
                          ],
                        ),
                        child: Text(
                          'Save Record',
                          style: AssessmentType.sans(
                            16,
                            FontWeight.w700,
                            AppColors.cardSurface,
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _SegmentedTabs extends StatelessWidget {
  const _SegmentedTabs({required this.activeTab, required this.onChanged});

  final As2bHistoryTab activeTab;
  final ValueChanged<As2bHistoryTab> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 350,
      height: 44,
      padding: const EdgeInsets.all(3),
      decoration: BoxDecoration(
        color: AppColors.cardSurface.withValues(alpha: 0.20),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(
          color: AppColors.cardSurface.withValues(alpha: 0.50),
          width: 1.5,
        ),
      ),
      child: Row(
        children: <Widget>[
          Expanded(
            child: _Tab(
              label: 'Medication',
              active: activeTab == As2bHistoryTab.medication,
              onTap: () => onChanged(As2bHistoryTab.medication),
            ),
          ),
          Expanded(
            child: _Tab(
              label: 'Family Record',
              active: activeTab == As2bHistoryTab.family,
              onTap: () => onChanged(As2bHistoryTab.family),
            ),
          ),
        ],
      ),
    );
  }
}

class _Tab extends StatelessWidget {
  const _Tab({
    required this.label,
    required this.active,
    required this.onTap,
  });

  final String label;
  final bool active;
  final VoidCallback onTap;

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
            color: active ? AppColors.cardSurface : Colors.transparent,
            borderRadius: BorderRadius.circular(999),
            border: active
                ? Border.all(color: AppColors.intakeButtonInk, width: 1.5)
                : null,
          ),
          child: Text(
            label,
            style: AssessmentType.sans(
              13,
              active ? FontWeight.w800 : FontWeight.w700,
              active ? AppColors.intakeInk : AppColors.cardSurface,
            ),
          ),
        ),
      ),
    );
  }
}

class _FieldLabel extends StatelessWidget {
  const _FieldLabel(this.label);

  final String label;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 14,
      child: FittedBox(
        fit: BoxFit.scaleDown,
        alignment: Alignment.centerLeft,
        child: Text(
          label,
          maxLines: 1,
          style: AssessmentType.sans(
            12,
            FontWeight.w700,
            AppColors.cardSurface,
          ),
        ),
      ),
    );
  }
}

BoxDecoration get _fieldDecoration => BoxDecoration(
      color: AppColors.cardSurface,
      borderRadius: BorderRadius.circular(12),
      border: Border.all(color: AppColors.intakeButtonInk, width: 1.5),
    );

class _TextField extends StatelessWidget {
  const _TextField({
    required this.controller,
    required this.hint,
    required this.onChanged,
  });

  final TextEditingController controller;
  final String hint;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    final OutlineInputBorder border = OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide.none,
    );
    return Container(
      height: 48,
      padding: const EdgeInsets.symmetric(horizontal: 14),
      decoration: _fieldDecoration,
      child: TextField(
        controller: controller,
        onChanged: onChanged,
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: AssessmentType.sans(
            13,
            FontWeight.w400,
            AppColors.textMuted,
          ),
          border: border,
          enabledBorder: border,
          focusedBorder: border,
        ),
        style: AssessmentType.sans(
          14,
          FontWeight.w600,
          AppColors.intakeInk,
        ),
      ),
    );
  }
}

class _SelectField<T> extends StatelessWidget {
  const _SelectField({
    required this.value,
    required this.items,
    required this.onChanged,
  });

  final T value;
  final List<T> items;
  final ValueChanged<T?> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 48,
      padding: const EdgeInsets.symmetric(horizontal: 14),
      decoration: _fieldDecoration,
      child: DropdownButtonHideUnderline(
        child: DropdownButton<T>(
          value: value,
          isExpanded: true,
          icon: const Icon(
            Icons.keyboard_arrow_down,
            size: 20,
            color: AppColors.intakeButtonInk,
          ),
          dropdownColor: AppColors.cardSurface,
          borderRadius: BorderRadius.circular(12),
          onChanged: onChanged,
          items: items
              .map(
                (T item) => DropdownMenuItem<T>(
                  value: item,
                  child: Text(
                    '$item',
                    style: AssessmentType.sans(
                      14,
                      FontWeight.w600,
                      AppColors.intakeInk,
                    ),
                  ),
                ),
              )
              .toList(),
          style: AssessmentType.sans(
            14,
            FontWeight.w600,
            AppColors.intakeInk,
          ),
        ),
      ),
    );
  }
}

class _StepperField extends StatelessWidget {
  const _StepperField({
    required this.value,
    required this.onDecrement,
    required this.onIncrement,
  });

  final String value;
  final VoidCallback onDecrement;
  final VoidCallback onIncrement;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 48,
      decoration: _fieldDecoration,
      child: Row(
        children: <Widget>[
          SizedBox(
            width: 48,
            height: 48,
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: onDecrement,
                child: const Icon(
                  Icons.remove,
                  size: 18,
                  color: AppColors.intakeButtonInk,
                ),
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              textAlign: TextAlign.center,
              style: AssessmentType.sans(
                14,
                FontWeight.w700,
                AppColors.intakeInk,
              ),
            ),
          ),
          SizedBox(
            width: 48,
            height: 48,
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: onIncrement,
                child: const Icon(
                  Icons.add,
                  size: 18,
                  color: AppColors.intakeButtonInk,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
