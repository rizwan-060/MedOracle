import 'dart:ui' show PathMetric;

import 'package:material_ui/material_ui.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../providers/clinical_status_provider.dart';

/// `/step_2_medication_and_family_history` — clinical status (Step 2A).
///
/// The same native screen renders three states from [ClinicalStatusPhase]:
/// empty, adding and the "conditions added" summary.
class Step2MedicationAndFamilyHistoryScreen extends ConsumerStatefulWidget {
  const Step2MedicationAndFamilyHistoryScreen({super.key});

  static const String routePath = RouteNames.step2ClinicalStatus;

  static const List<String> knownConditions = <String>[
    'Hypertension',
    'Asthma',
    'Dyslipidemia',
    'Type 2 Diabetes',
    'Coronary Artery Disease',
    'Chronic Kidney Disease',
    'Hypothyroidism',
    'Migraine',
  ];

  @override
  ConsumerState<Step2MedicationAndFamilyHistoryScreen> createState() =>
      _Step2MedicationAndFamilyHistoryScreenState();
}

class _Step2MedicationAndFamilyHistoryScreenState
    extends ConsumerState<Step2MedicationAndFamilyHistoryScreen> {
  final TextEditingController _searchController = TextEditingController();
  final FocusNode _searchFocus = FocusNode();

  @override
  void dispose() {
    _searchController.dispose();
    _searchFocus.dispose();
    super.dispose();
  }

  List<String> get _suggestions {
    final String query = _searchController.text.trim().toLowerCase();
    if (query.isEmpty) return const <String>[];
    final List<String> added = ref.read(clinicalStatusProvider).conditions;
    return Step2MedicationAndFamilyHistoryScreen.knownConditions
        .where((c) => c.toLowerCase().contains(query) && !added.contains(c))
        .take(5)
        .toList();
  }

  void _addCondition(String name) {
    ref.read(clinicalStatusProvider.notifier).addCondition(name);
    _searchController.clear();
    _searchFocus.requestFocus();
    setState(() {});
  }

  void _finishAdding() {
    _searchFocus.unfocus();
    ref.read(clinicalStatusProvider.notifier).completeAdding();
  }

  void _goToMedications() {
    context.go(RouteNames.step2b);
  }

  void _addExtra({required bool surgery}) {
    final ClinicalStatusState state = ref.read(clinicalStatusProvider);
    final ClinicalStatusController controller =
        ref.read(clinicalStatusProvider.notifier);
    if (surgery) {
      controller.addSurgery('Surgery ${state.surgeries.length + 1}');
    } else {
      controller.addAllergy('Allergy ${state.allergies.length + 1}');
    }
  }

  @override
  Widget build(BuildContext context) {
    final ClinicalStatusState state = ref.watch(clinicalStatusProvider);

    return Scaffold(
      resizeToAvoidBottomInset: false,
      backgroundColor: AppColors.canvasBackground,
      body: SafeArea(
        bottom: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            const _AppHeader(currentStep: 2, totalSteps: 5),
            Expanded(child: _body(state: state)),
            _Footer(
              showPrimaryCta: state.conditions.isNotEmpty,
              onBack: () => context.go(RouteNames.dashboard),
              onContinue: _goToMedications,
            ),
          ],
        ),
      ),
    );
  }

  Widget _body({required ClinicalStatusState state}) {
    return CustomScrollView(
      slivers: <Widget>[
        SliverFillRemaining(
          hasScrollBody: false,
          child: Padding(
            padding: const EdgeInsets.fromLTRB(20, 20, 20, 16),
            child: switch (state.phase) {
              ClinicalStatusPhase.empty => Stack(
                  children: <Widget>[
                    const Positioned(left: 0, top: 0, child: _Eyebrow()),
                    Center(
                      child: SizedBox(
                        width: double.infinity,
                        child: _conditionsCard(state: state),
                      ),
                    ),
                  ],
                ),
              ClinicalStatusPhase.adding => Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: <Widget>[
                    const _Eyebrow(),
                    const SizedBox(height: 16),
                    _conditionsCard(state: state),
                    const SizedBox(height: 36),
                    _addCardsRow(state: state, summary: false),
                    const Spacer(),
                    const _NotesButton(),
                  ],
                ),
              ClinicalStatusPhase.done => Stack(
                  children: <Widget>[
                    const Positioned(left: 0, top: 0, child: _Eyebrow()),
                    Center(
                      child: SizedBox(
                        width: double.infinity,
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: <Widget>[
                            _addedCountRow(state: state),
                            const SizedBox(height: 24),
                            _addCardsRow(state: state, summary: true),
                          ],
                        ),
                      ),
                    ),
                    const Positioned(
                      left: 0,
                      right: 0,
                      bottom: 0,
                      child: _NotesButton(),
                    ),
                  ],
                ),
            },
          ),
        ),
      ],
    );
  }

  Widget _conditionsCard({required ClinicalStatusState state}) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _cardDecoration(),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          Text(
            'Current Health Conditions',
            style: _text(17, FontWeight.w800, AppColors.deepInk),
          ),
          const SizedBox(height: 4),
          Text(
            'Add any health issues you are currently dealing with.',
            style: _text(
              13,
              FontWeight.w500,
              AppColors.deepInk.withValues(alpha: 0.6),
              height: 20 / 13,
            ),
          ),
          if (state.phase == ClinicalStatusPhase.adding) ...<Widget>[
            const SizedBox(height: 16),
            SizedBox(height: 172, child: _conditionFan(state: state)),
          ] else ...<Widget>[
            const SizedBox(height: 16),
            _searchField(state),
            if (_suggestions.isNotEmpty) ...<Widget>[
              const SizedBox(height: 4),
              _suggestionList(),
            ],
          ],
          if (state.phase == ClinicalStatusPhase.empty) ...<Widget>[
            const SizedBox(height: 12),
            Row(
              children: <Widget>[
                Expanded(
                  child: _Pill(
                    label: 'Done adding',
                    filled: true,
                    fill: AppColors.terraCotta,
                    foreground: AppColors.cardSurface,
                    fontSize: 13,
                    onTap: _finishAdding,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _Pill(
                    label: "I don't have any",
                    outlined: true,
                    outline: AppColors.headerText,
                    foreground: AppColors.headerText,
                    fontSize: 13,
                    onTap: () {
                      ref.read(clinicalStatusProvider.notifier).clearConditions();
                      _goToMedications();
                    },
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _conditionFan({required ClinicalStatusState state}) {
    final List<String> conditions = state.conditions;
    if (conditions.isEmpty) return const SizedBox.shrink();

    final double cardWidth = 100;
    final double step = 88;
    final double totalWidth = cardWidth + (conditions.length - 1) * step;
    final double mid = (conditions.length - 1) / 2;

    return Stack(
      alignment: Alignment.topLeft,
      children: <Widget>[
        Positioned.fill(
          child: FittedBox(
            fit: BoxFit.scaleDown,
            child: SizedBox(
              width: totalWidth,
              height: 148,
              child: Stack(
                children: <Widget>[
                  for (int i = 0; i < conditions.length; i++)
                    Positioned(
                      left: i * step,
                      top: 0,
                      child: _conditionCard(
                        label: conditions[i],
                        shift: i - mid,
                        onRemove: () => ref
                            .read(clinicalStatusProvider.notifier)
                            .removeCondition(conditions[i]),
                      ),
                    ),
                ],
              ),
            ),
          ),
        ),
        Positioned(
          left: 0,
          right: 0,
          top: 120,
          child: _searchField(state),
        ),
        if (_suggestions.isNotEmpty)
          Positioned(
            left: 0,
            right: 0,
            top: 168,
            child: _suggestionList(),
          ),
      ],
    );
  }

  Widget _conditionCard({
    required String label,
    required double shift,
    required VoidCallback onRemove,
  }) {
    final double angle = shift == 0 ? 0 : (shift > 0 ? 6 : -6) * 3.14159265 / 180;
    final bool tilted = shift != 0;
    final Color fill = shift < 0
        ? AppColors.headerText.withValues(alpha: 0.2)
        : shift == 0
            ? AppColors.headerText.withValues(alpha: 0.1)
            : AppColors.cardSurface;

    return Transform.rotate(
      angle: angle,
      child: Transform.translate(
        offset: Offset(0, tilted ? 8 : 0),
        child: Transform.scale(
          scale: tilted ? 0.94 : 1,
          child: GestureDetector(
            onTap: onRemove,
            child: Container(
              width: 100,
              height: 148,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: fill,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.headerText),
                boxShadow: <BoxShadow>[
                  BoxShadow(
                    color: AppColors.deepInk.withValues(alpha: 0.35),
                    blurRadius: 20,
                    spreadRadius: -10,
                    offset: const Offset(0, 14),
                  ),
                ],
              ),
              child: Stack(
                children: <Widget>[
                  const Positioned(
                    right: 8,
                    top: 8,
                    child: Icon(
                      Icons.close,
                      size: 12,
                      color: AppColors.deepInk,
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.only(top: 24),
                    child: Text(
                      label,
                      maxLines: 2,
                      style: _text(
                        11.5,
                        FontWeight.w800,
                        AppColors.deepInk,
                        height: 16 / 11.5,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _searchField(ClinicalStatusState state) {
    final bool showDone =
        state.phase == ClinicalStatusPhase.adding && _searchFocus.hasFocus;
    return SizedBox(
      height: 48,
      child: TextField(
        controller: _searchController,
        focusNode: _searchFocus,
        onChanged: (String value) {
          ref.read(clinicalStatusProvider.notifier).setConditionQuery(value);
          setState(() {});
        },
        onSubmitted: (String value) {
          if (value.trim().isEmpty) {
            _finishAdding();
          } else {
            _addCondition(value.trim());
          }
        },
        cursorColor: AppColors.terraCotta,
        style: _text(14, FontWeight.w500, AppColors.deepInk),
        decoration: InputDecoration(
          filled: true,
          fillColor: AppColors.cardSurface,
          hintText: 'Search or add conditions...',
          hintStyle: _text(
            14,
            FontWeight.w400,
            AppColors.deepInk.withValues(alpha: 0.6),
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          prefixIcon: const Padding(
            padding: EdgeInsets.only(right: 10),
            child: Icon(Icons.search, size: 16, color: AppColors.headerText),
          ),
          prefixIconConstraints: const BoxConstraints(minWidth: 0, minHeight: 0),
          suffixIcon: showDone
              ? GestureDetector(
                  onTap: _finishAdding,
                  child: Padding(
                    padding: const EdgeInsets.only(right: 16, left: 4),
                    child: Text(
                      'Done adding',
                      style: _text(12, FontWeight.w700, AppColors.headerText),
                    ),
                  ),
                )
              : null,
          suffixIconConstraints: const BoxConstraints(minWidth: 0, minHeight: 0),
          border: _fieldBorder(),
          enabledBorder: _fieldBorder(),
          focusedBorder: _fieldBorder(),
        ),
      ),
    );
  }

  OutlineInputBorder _fieldBorder() => OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: AppColors.headerText),
      );

  Widget _suggestionList() {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.borderSubtle),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.deepInk.withValues(alpha: 0.18),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          for (final String condition in _suggestions)
            InkWell(
              onTap: () => _addCondition(condition),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                child: Text(
                  condition,
                  style: _text(14, FontWeight.w500, AppColors.deepInk),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _addedCountRow({required ClinicalStatusState state}) {
    return Container(
      height: 44,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: AppColors.cardSurface.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Row(
        children: <Widget>[
          Icon(Icons.check, size: 16, color: AppColors.headerText),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              '${state.conditions.length} Health conditions added',
              style: _text(
                13,
                FontWeight.w700,
                AppColors.deepInk.withValues(alpha: 0.6),
              ),
            ),
          ),
          GestureDetector(
            onTap: () =>
                ref.read(clinicalStatusProvider.notifier).editConditions(),
            child: const Icon(
              Icons.edit_outlined,
              size: 16,
              color: AppColors.headerText,
            ),
          ),
        ],
      ),
    );
  }

  Widget _addCardsRow({
    required ClinicalStatusState state,
    required bool summary,
  }) {
    return Row(
      children: <Widget>[
        Expanded(
          child: _addCard(
            label: summary ? '+ Add a past surgery' : 'Add past surgery',
            icon: Icons.medical_services_outlined,
            count: state.surgeries.length,
            showCount: !summary,
            height: summary ? 176 : 150,
            onTap: () => _addExtra(surgery: true),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _addCard(
            label: summary ? '+ Add known allergies' : 'Add known allergies',
            icon: Icons.coronavirus_outlined,
            count: state.allergies.length,
            showCount: !summary,
            height: summary ? 176 : 150,
            onTap: () => _addExtra(surgery: false),
          ),
        ),
      ],
    );
  }

  Widget _addCard({
    required String label,
    required IconData icon,
    required int count,
    required bool showCount,
    required double height,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: CustomPaint(
        painter: const _DashedBorderPainter(AppColors.headerText, 24),
        child: Container(
          height: height,
          padding: const EdgeInsets.symmetric(horizontal: 8).copyWith(bottom: 24),
          decoration: BoxDecoration(
            color: AppColors.headerText.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(24),
            boxShadow: <BoxShadow>[
              BoxShadow(
                color: AppColors.headerText.withValues(alpha: 0.5),
                blurRadius: 18,
                spreadRadius: -10,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: Stack(
            children: <Widget>[
              Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: <Widget>[
                    Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        color: AppColors.cardSurface,
                        shape: BoxShape.circle,
                        border: Border.all(color: AppColors.headerText, width: 2),
                      ),
                      child: Icon(icon, size: 20, color: AppColors.headerText),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      label,
                      textAlign: TextAlign.center,
                      style: _text(
                        14,
                        FontWeight.w800,
                        AppColors.deepInk,
                        height: 16 / 14,
                      ),
                    ),
                  ],
                ),
              ),
              if (showCount)
                Positioned(
                  left: 16,
                  bottom: 12,
                  child: Text(
                    '$count added',
                    style: _text(12, FontWeight.w700, AppColors.deepInk),
                  ),
                ),
              Positioned(
                right: 16,
                bottom: 12,
                child: Icon(Icons.add, size: 20, color: AppColors.headerText),
              ),
            ],
          ),
        ),
      ),
    );
  }

  BoxDecoration _cardDecoration() => BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.borderSubtle),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.deepInk.withValues(alpha: 0.35),
            blurRadius: 30,
            spreadRadius: -20,
            offset: const Offset(0, 18),
          ),
        ],
      );

  TextStyle _text(
    double size,
    FontWeight weight,
    Color color, {
    double? height,
    double? letterSpacing,
  }) {
    return TextStyle(
      fontFamily: 'Plus Jakarta Sans',
      fontSize: size,
      fontWeight: weight,
      color: color,
      height: height,
      letterSpacing: letterSpacing,
    );
  }
}

class _AppHeader extends StatelessWidget {
  const _AppHeader({required this.currentStep, required this.totalSteps});

  final int currentStep;
  final int totalSteps;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.headerText,
        borderRadius: const BorderRadius.vertical(bottom: Radius.circular(28)),
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: <Color>[
            AppColors.cardSurface.withValues(alpha: 0.05),
            AppColors.deepInk.withValues(alpha: 0.2),
          ],
        ),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.deepInk.withValues(alpha: 0.18),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            SizedBox(
              height: 28,
              child: Row(
                children: <Widget>[
                  const _Autosave(),
                  const Expanded(child: Center(child: _Brand())),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: AppColors.cardSurface.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(999),
                      border: Border.all(
                        color: AppColors.cardSurface.withValues(alpha: 0.4),
                      ),
                    ),
                    child: Text(
                      'Save & exit',
                      style: _headerText(12, FontWeight.w700),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: <Widget>[
                for (int i = 1; i <= totalSteps; i++) ...<Widget>[
                  if (i > 1) const SizedBox(width: 6),
                  Expanded(
                    child: Container(
                      height: 4,
                      decoration: BoxDecoration(
                        color: i <= currentStep
                            ? AppColors.cardSurface
                            : AppColors.cardSurface.withValues(alpha: 0.3),
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }

  TextStyle _headerText(double size, FontWeight weight) => TextStyle(
        fontFamily: 'Plus Jakarta Sans',
        fontSize: size,
        fontWeight: weight,
        color: AppColors.cardSurface,
      );
}

class _Autosave extends StatelessWidget {
  const _Autosave();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        Icon(Icons.check, size: 16, color: AppColors.cardSurface),
        const SizedBox(width: 6),
        Text(
          'Autosaved',
          style: TextStyle(
            fontFamily: 'Plus Jakarta Sans',
            fontSize: 11,
            fontWeight: FontWeight.w700,
            color: AppColors.cardSurface,
          ),
        ),
      ],
    );
  }
}

class _Brand extends StatelessWidget {
  const _Brand();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        Icon(
          Icons.health_and_safety_outlined,
          size: 20,
          color: AppColors.cardSurface,
        ),
        const SizedBox(width: 6),
        Text(
          'MedOracle',
          style: TextStyle(
            fontFamily: 'Plus Jakarta Sans',
            fontSize: 16,
            fontWeight: FontWeight.w800,
            color: AppColors.cardSurface,
          ),
        ),
      ],
    );
  }
}

class _Eyebrow extends StatelessWidget {
  const _Eyebrow();

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Step 2 · Clinical status',
      child: Text(
        'Step 2 · Clinical status',
        style: TextStyle(
          fontFamily: 'Plus Jakarta Sans',
          fontSize: 12,
          fontWeight: FontWeight.w700,
          letterSpacing: 1.44,
          color: AppColors.headerText,
        ),
      ),
    );
  }
}

class _NotesButton extends StatelessWidget {
  const _NotesButton();

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 48,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.headerText, width: 2),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.headerText.withValues(alpha: 0.5),
            blurRadius: 14,
            spreadRadius: -8,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Center(
        child: RichText(
          text: TextSpan(
            style: TextStyle(
              fontFamily: 'Plus Jakarta Sans',
              fontSize: 14,
              fontWeight: FontWeight.w700,
              color: AppColors.headerText,
            ),
            children: <TextSpan>[
              const TextSpan(text: '+ Add additional notes '),
              TextSpan(
                text: '(Optional)',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: AppColors.deepInk.withValues(alpha: 0.6),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Footer extends StatelessWidget {
  const _Footer({
    required this.showPrimaryCta,
    required this.onBack,
    required this.onContinue,
  });

  final bool showPrimaryCta;
  final VoidCallback onBack;
  final VoidCallback onContinue;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 12),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        border: Border(top: BorderSide(color: AppColors.borderSubtle)),
      ),
      child: Row(
        children: <Widget>[
          Expanded(
            child: _Pill(
              label: 'Back',
              outlined: true,
              outline: AppColors.borderSubtle,
              foreground: AppColors.headerText,
              fontSize: 14,
              onTap: onBack,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            flex: 2,
            child: _Pill(
              label: 'Continue to medications',
              filled: true,
              fill: showPrimaryCta
                  ? AppColors.terraCotta
                  : AppColors.borderSubtle.withValues(alpha: 0.6),
              foreground: showPrimaryCta
                  ? AppColors.cardSurface
                  : AppColors.deepInk.withValues(alpha: 0.6),
              fontSize: 14,
              onTap: onContinue,
            ),
          ),
        ],
      ),
    );
  }
}

class _Pill extends StatelessWidget {
  const _Pill({
    required this.label,
    required this.foreground,
    required this.fontSize,
    this.onTap,
    this.filled = false,
    this.outlined = false,
    this.fill,
    this.outline,
  });

  final String label;
  final Color foreground;
  final double fontSize;
  final VoidCallback? onTap;
  final bool filled;
  final bool outlined;
  final Color? fill;
  final Color? outline;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 44,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(999),
          child: Container(
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: filled ? fill : AppColors.cardSurface,
              borderRadius: BorderRadius.circular(999),
              border: outlined && outline != null
                  ? Border.all(color: outline!, width: 2)
                  : null,
            ),
            child: Text(
              label,
              style: TextStyle(
                fontFamily: 'Plus Jakarta Sans',
                fontSize: fontSize,
                fontWeight: FontWeight.w700,
                color: foreground,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _DashedBorderPainter extends CustomPainter {
  const _DashedBorderPainter(this.color, this.radius);

  final Color color;
  final double radius;

  @override
  void paint(Canvas canvas, Size size) {
    final RRect rect = RRect.fromRectAndRadius(
      Offset.zero & size,
      Radius.circular(radius),
    );
    final Path path = Path()..addRRect(rect);
    final Paint paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    const double dash = 6;
    const double gap = 4;
    for (final PathMetric metric in path.computeMetrics()) {
      double distance = 0;
      while (distance < metric.length) {
        canvas.drawPath(
          metric.extractPath(distance, distance + dash),
          paint,
        );
        distance += dash + gap;
      }
    }
  }

  @override
  bool shouldRepaint(_DashedBorderPainter oldDelegate) =>
      oldDelegate.color != color || oldDelegate.radius != radius;
}
