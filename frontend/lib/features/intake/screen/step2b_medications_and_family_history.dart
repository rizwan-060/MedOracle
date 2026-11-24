import 'package:material_ui/material_ui.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import 'intake_screen_chrome.dart';

const List<String> _frequencies = <String>[
  'Once Daily',
  'Twice Daily',
  'At Night',
  'As Needed',
];

const List<String> _relations = <String>[
  'Father',
  'Mother',
  'Brother',
  'Sister',
  'Grandparent',
  'Child',
];

/// `/intake/step-2b` — medications and family history (Step 2B).
class Step2BMedicationsAndFamilyHistoryScreen extends StatefulWidget {
  const Step2BMedicationsAndFamilyHistoryScreen({super.key});

  static const String routePath = RouteNames.step2b;

  @override
  State<Step2BMedicationsAndFamilyHistoryScreen> createState() =>
      _Step2BMedicationsAndFamilyHistoryScreenState();
}

class _Step2BMedicationsAndFamilyHistoryScreenState
    extends State<Step2BMedicationsAndFamilyHistoryScreen> {
  final List<_Record> _medicines = <_Record>[
    _Record('Amlodipine', '5mg, Once Daily'),
    _Record('Metformin', '500mg, Twice Daily'),
    _Record('Atorvastatin', '20mg, At Night'),
  ];
  final List<_Record> _family = <_Record>[
    _Record('Father', 'Heart Attack, 52 yrs'),
    _Record('Mother', 'Type 2 Diabetes, 61 yrs'),
  ];

  bool _medOpen = false;
  bool _famOpen = false;
  bool _formOpen = true;
  bool _familyTab = false;

  final TextEditingController _nameController =
      TextEditingController(text: 'Metformin');
  final TextEditingController _conditionController =
      TextEditingController(text: 'Myocardial infarction');
  String _frequency = 'Twice Daily';
  String _relation = 'Father';
  int _dose = 500;
  int _age = 52;

  @override
  void dispose() {
    _nameController.dispose();
    _conditionController.dispose();
    super.dispose();
  }

  void _saveRecord() {
    setState(() {
      if (_familyTab) {
        _family.add(
          _Record(_relation, '${_conditionController.text.trim()}, $_age yrs'),
        );
        _famOpen = true;
      } else {
        _medicines.add(
          _Record(
            _nameController.text.trim(),
            '$_dose mg, $_frequency',
          ),
        );
        _medOpen = true;
      }
      _formOpen = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      resizeToAvoidBottomInset: false,
      backgroundColor: AppColors.canvasBackground,
      body: SafeArea(
        bottom: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            const IntakeHeader(step: 2),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: <Widget>[
                    _Section(
                      title: 'Current Medications',
                      count: '${_medicines.length} Medications',
                      records: _medicines,
                      open: _medOpen,
                      onToggle: () => setState(() => _medOpen = !_medOpen),
                      onRemove: (int index) =>
                          setState(() => _medicines.removeAt(index)),
                    ),
                    const SizedBox(height: 16),
                    _Section(
                      title: 'Family History',
                      count: '${_family.length} Records',
                      records: _family,
                      open: _famOpen,
                      onToggle: () => setState(() => _famOpen = !_famOpen),
                      onRemove: (int index) =>
                          setState(() => _family.removeAt(index)),
                      emberBadge: true,
                    ),
                    const SizedBox(height: 24),
                    _AddForm(
                      open: _formOpen,
                      onToggle: () => setState(() => _formOpen = !_formOpen),
                      familyTab: _familyTab,
                      onTab: (bool family) =>
                          setState(() => _familyTab = family),
                      nameController: _nameController,
                      conditionController: _conditionController,
                      frequency: _frequency,
                      relation: _relation,
                      dose: _dose,
                      age: _age,
                      onFrequency: (String value) =>
                          setState(() => _frequency = value),
                      onRelation: (String value) =>
                          setState(() => _relation = value),
                      onDose: (int value) => setState(() => _dose = value),
                      onAge: (int value) => setState(() => _age = value),
                      onSave: _saveRecord,
                    ),
                  ],
                ),
              ),
            ),
            IntakeFooter(
              ctaLabel: 'Next: Symptoms',
              onBack: () => _go(context, RouteNames.step2Medications),
              onContinue: () => _go(context, RouteNames.step3Symptoms),
            ),
          ],
        ),
      ),
    );
  }

  void _go(BuildContext context, String path) => context.go(path);
}

class _Record {
  const _Record(this.name, this.detail);

  final String name;
  final String detail;
}

class _Section extends StatelessWidget {
  const _Section({
    required this.title,
    required this.count,
    required this.records,
    required this.open,
    required this.onToggle,
    required this.onRemove,
    this.emberBadge = false,
  });

  final String title;
  final String count;
  final List<_Record> records;
  final bool open;
  final VoidCallback onToggle;
  final ValueChanged<int> onRemove;
  final bool emberBadge;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.borderSubtle),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.deepInk.withValues(alpha: 0.22),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          GestureDetector(
            onTap: onToggle,
            child: Row(
              children: <Widget>[
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Text(
                        title,
                        style: IntakeType.jakarta(
                          17,
                          FontWeight.w800,
                          AppColors.deepInk,
                          height: 24 / 17,
                        ),
                      ),
                      Text(
                        '$count  • Tap to expand',
                        style: IntakeType.jakarta(
                          13,
                          FontWeight.w500,
                          AppColors.textMuted,
                          height: 18 / 13,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 10),
                _Pill(
                  label: open ? 'Show less' : 'Show records',
                  ember: emberBadge && !open,
                  onTap: onToggle,
                ),
              ],
            ),
          ),
          if (open) ...<Widget>[
            const SizedBox(height: 16),
            for (int i = 0; i < records.length; i++)
              _RecordRow(
                record: records[i],
                onRemove: () => onRemove(i),
              ),
            const SizedBox(height: 6),
            Align(
              alignment: Alignment.centerLeft,
              child: GestureDetector(
                onTap: onToggle,
                child: Text(
                  'Show less',
                  style: IntakeType.jakarta(
                    13,
                    FontWeight.w700,
                    AppColors.headerText,
                  ),
                ),
              ),
            ),
          ] else
            Padding(
              padding: const EdgeInsets.only(top: 12),
              child: SizedBox(height: 36, child: _Pile(records: records)),
            ),
        ],
      ),
    );
  }
}

class _Pile extends StatelessWidget {
  const _Pile({required this.records});

  final List<_Record> records;

  @override
  Widget build(BuildContext context) {
    final int shown = records.length > 3 ? 3 : records.length;
    return Stack(
      children: <Widget>[
        for (int i = 0; i < shown; i++)
          Positioned(
            left: (i * 22).toDouble(),
            top: (i * 2).toDouble(),
            child: Transform.rotate(
              angle: (i - 1) * 0.035,
              child: Container(
                width: 150,
                height: 32,
                padding: const EdgeInsets.symmetric(horizontal: 10),
                alignment: Alignment.centerLeft,
                decoration: BoxDecoration(
                  color: i == shown - 1
                      ? AppColors.cardSurface
                      : AppColors.secondarySurface,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: AppColors.borderSubtle),
                ),
                child: Text(
                  records[i].name,
                  overflow: TextOverflow.ellipsis,
                  style: IntakeType.jakarta(
                    12,
                    FontWeight.w700,
                    AppColors.deepInk,
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}

class _RecordRow extends StatelessWidget {
  const _RecordRow({required this.record, required this.onRemove});

  final _Record record;
  final VoidCallback onRemove;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: <Widget>[
          Expanded(
            child: Text(
              '${record.name} (${record.detail})',
              style: IntakeType.jakarta(
                13,
                FontWeight.w500,
                AppColors.deepInk,
              ),
            ),
          ),
          GestureDetector(
            onTap: onRemove,
            child: const Icon(Icons.close, size: 12, color: AppColors.textMuted),
          ),
        ],
      ),
    );
  }
}

class _Pill extends StatelessWidget {
  const _Pill({
    required this.label,
    required this.onTap,
    this.ember = false,
  });

  final String label;
  final VoidCallback onTap;
  final bool ember;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 36,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: ember
              ? AppColors.terraCotta.withValues(alpha: 0.1)
              : AppColors.cardSurface,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(
            color: ember ? AppColors.terraCotta : AppColors.headerText,
          ),
        ),
        child: Text(
          label,
          style: IntakeType.jakarta(
            13,
            FontWeight.w800,
            ember ? AppColors.terraCotta : AppColors.headerText,
          ),
        ),
      ),
    );
  }
}

class _AddForm extends StatefulWidget {
  const _AddForm({
    required this.open,
    required this.onToggle,
    required this.familyTab,
    required this.onTab,
    required this.nameController,
    required this.conditionController,
    required this.frequency,
    required this.relation,
    required this.dose,
    required this.age,
    required this.onFrequency,
    required this.onRelation,
    required this.onDose,
    required this.onAge,
    required this.onSave,
  });

  final bool open;
  final VoidCallback onToggle;
  final bool familyTab;
  final ValueChanged<bool> onTab;
  final TextEditingController nameController;
  final TextEditingController conditionController;
  final String frequency;
  final String relation;
  final int dose;
  final int age;
  final ValueChanged<String> onFrequency;
  final ValueChanged<String> onRelation;
  final ValueChanged<int> onDose;
  final ValueChanged<int> onAge;
  final VoidCallback onSave;

  @override
  State<_AddForm> createState() => _AddFormState();
}

class _AddFormState extends State<_AddForm> {
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.cardSurface.withValues(alpha: 0.9),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.headerText, width: 2),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.deepInk.withValues(alpha: 0.3),
            blurRadius: 30,
            spreadRadius: -12,
            offset: const Offset(0, 12),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          GestureDetector(
            onTap: widget.onToggle,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(20, 18, 20, 12),
              child: Row(
                children: <Widget>[
                  Text(
                    'Add to your history',
                    style: IntakeType.jakarta(
                      17,
                      FontWeight.w800,
                      AppColors.deepInk,
                    ),
                  ),
                  const Spacer(),
                  Icon(
                    widget.open ? Icons.expand_more : Icons.expand_less,
                    size: 20,
                    color: AppColors.headerText,
                  ),
                ],
              ),
            ),
          ),
          if (widget.open) ...<Widget>[
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Row(
                children: <Widget>[
                  Expanded(
                    child: _Tab(
                      label: 'Medication',
                      active: !widget.familyTab,
                      onTap: () => widget.onTab(false),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _Tab(
                      label: 'Family Record',
                      active: widget.familyTab,
                      onTap: () => widget.onTab(true),
                    ),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 16),
              child: widget.familyTab ? _familyFields() : _medicineFields(),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
              child: SizedBox(
                height: 44,
                child: Material(
                  color: AppColors.headerText,
                  borderRadius: BorderRadius.circular(12),
                  child: InkWell(
                    onTap: widget.onSave,
                    child: Center(
                      child: Text(
                        'Save Record',
                        style: IntakeType.jakarta(
                          14,
                          FontWeight.w800,
                          AppColors.cardSurface,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _medicineFields() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        _Field(
          label: 'Medicine name',
          controller: widget.nameController,
          hint: 'Search or type a medicine',
        ),
        const SizedBox(height: 16),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Expanded(
              child: _DropdownField(
                label: 'How often',
                value: widget.frequency,
                items: _frequencies,
                onChanged: widget.onFrequency,
              ),
            ),
            const SizedBox(width: 12),
            SizedBox(
              width: 142,
              child: _CounterField(
                label: 'Dose (mg)',
                value: widget.dose,
                onDecrease: () => widget.onDose(widget.dose - 1),
                onIncrease: () => widget.onDose(widget.dose + 1),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _familyFields() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Expanded(
              child: _DropdownField(
                label: 'Relative',
                value: widget.relation,
                items: _relations,
                onChanged: widget.onRelation,
              ),
            ),
            const SizedBox(width: 12),
            SizedBox(
              width: 142,
              child: _CounterField(
                label: 'Age at diagnosis',
                value: widget.age,
                onDecrease: () => widget.onAge(widget.age - 1),
                onIncrease: () => widget.onAge(widget.age + 1),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        _Field(
          label: 'Condition',
          controller: widget.conditionController,
          hint: 'Search or type a condition',
        ),
      ],
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
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 44,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: active
              ? AppColors.headerText
              : AppColors.cardSurface.withValues(alpha: 0.62),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.borderSubtle),
        ),
        child: Text(
          label,
          style: IntakeType.jakarta(
            14,
            active ? FontWeight.w800 : FontWeight.w500,
            active ? AppColors.cardSurface : AppColors.headerText,
          ),
        ),
      ),
    );
  }
}

class _Field extends StatelessWidget {
  const _Field({
    required this.label,
    required this.controller,
    required this.hint,
  });

  final String label;
  final TextEditingController controller;
  final String hint;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(
          label,
          style: IntakeType.jakarta(
            12,
            FontWeight.w700,
            AppColors.headerText,
          ),
        ),
        const SizedBox(height: 4),
        SizedBox(
          height: 44,
          child: TextField(
            controller: controller,
            style: IntakeType.jakarta(15, FontWeight.w500, AppColors.deepInk),
            decoration: InputDecoration(
              hintText: hint,
              hintStyle: IntakeType.jakarta(15, FontWeight.w400, AppColors.textMuted),
              filled: true,
              fillColor: AppColors.cardSurface,
              contentPadding: const EdgeInsets.symmetric(horizontal: 12),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: AppColors.borderSubtle),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: AppColors.borderSubtle),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppColors.headerText),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _DropdownField extends StatelessWidget {
  const _DropdownField({
    required this.label,
    required this.value,
    required this.items,
    required this.onChanged,
  });

  final String label;
  final String value;
  final List<String> items;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(
          label,
          style: IntakeType.jakarta(
            12,
            FontWeight.w700,
            AppColors.headerText,
          ),
        ),
        const SizedBox(height: 4),
        SizedBox(
          height: 44,
          child: DropdownButtonFormField<String>(
            initialValue: value,
            items: <DropdownMenuItem<String>>[
              for (final String item in items)
                DropdownMenuItem<String>(value: item, child: Text(item)),
            ],
            onChanged: (String? next) {
              if (next != null) onChanged(next);
            },
            decoration: InputDecoration(
              filled: true,
              fillColor: AppColors.cardSurface,
              contentPadding: const EdgeInsets.symmetric(horizontal: 12),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: AppColors.borderSubtle),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: AppColors.borderSubtle),
              ),
            ),
            style: IntakeType.jakarta(14, FontWeight.w500, AppColors.deepInk),
          ),
        ),
      ],
    );
  }
}

class _CounterField extends StatelessWidget {
  const _CounterField({
    required this.label,
    required this.value,
    required this.onDecrease,
    required this.onIncrease,
  });

  final String label;
  final int value;
  final VoidCallback onDecrease;
  final VoidCallback onIncrease;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(
          label,
          style: IntakeType.jakarta(
            12,
            FontWeight.w700,
            AppColors.headerText,
          ),
        ),
        const SizedBox(height: 4),
        SizedBox(
          height: 44,
          child: Row(
            children: <Widget>[
              StepperButton(
                size: 36,
                icon: Icons.remove,
                onTap: onDecrease,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  '$value',
                  textAlign: TextAlign.center,
                  style: IntakeType.jakarta(
                    15,
                    FontWeight.w700,
                    AppColors.deepInk,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              StepperButton(
                size: 36,
                icon: Icons.add,
                filled: true,
                onTap: onIncrease,
              ),
            ],
          ),
        ),
      ],
    );
  }
}
