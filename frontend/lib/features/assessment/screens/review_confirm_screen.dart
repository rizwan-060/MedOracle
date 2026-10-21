import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../providers/clinical_status_provider.dart';
import '../providers/labs_vitals_provider.dart';
import '../providers/medications_family_provider.dart';
import '../providers/review_provider.dart';
import '../providers/symptoms_provider.dart';
import '../widgets/edit_icon_button.dart';
import '../widgets/key_value_row.dart';
import '../widgets/narrative_box.dart';
import '../widgets/review_sub_header.dart';
import '../widgets/section_card.dart';
import '../widgets/selectable_chips.dart';
import '../widgets/severity_slider.dart';
import '../widgets/assessment_header.dart';
import '../widgets/assessment_nav_buttons.dart';

/// Step 5 (final) of the intake wizard — a read-only summary of every
/// completed step, with per-section edit jumps and the submit CTA.
class ReviewConfirmScreen extends ConsumerWidget {
  const ReviewConfirmScreen({super.key});

  static const String routePath = RouteNames.review;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ReviewProfileSummary profile = ref.watch(reviewProfileProvider);
    final ClinicalStatusState clinical =
        ref.watch(clinicalStatusProvider);
    final MedicationsFamilyState meds =
        ref.watch(medicationsFamilyProvider);
    final SymptomsState symptoms = ref.watch(symptomsProvider);
    final LabsVitalsState labs = ref.watch(labsVitalsProvider);

    return Scaffold(
      backgroundColor: AppColors.canvasBackground,
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              AppColors.dustyTaupe,
              AppColors.canvasBackground,
            ],
            stops: [0, 0.35],
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            AssessmentHeader(
              currentStep: 5,
              totalSteps: 5,
              onSaveExit: () {/* persist + leave wizard */},
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 12, 20, 18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // ── Profile & Demographics ──
                    SectionCard(
                      title: 'Profile & Demographics',
                      trailing: EditIconButton(
                        tooltip: 'Edit Profile & Demographics',
                        onTap: () => context.go(RouteNames.profile),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          KeyValueRow(label: 'Age', value: profile.age, first: true),
                          KeyValueRow(
                            label: 'Height',
                            value: labs.heightCm,
                            unit: 'cm',
                          ),
                          KeyValueRow(
                            label: 'Weight',
                            value: labs.weightKg,
                            unit: 'kg',
                          ),
                          KeyValueRow(
                            label: 'Smoking',
                            value: profile.smokingStatus,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),

                    // ── Clinical History ──
                    SectionCard(
                      title: 'Clinical History',
                      trailing: EditIconButton(
                        tooltip: 'Edit Clinical History',
                        onTap: () =>
                            context.go(RouteNames.clinicalStatus),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          const ReviewSubHeader('Chronic Conditions'),
                          if (clinical.conditions.isEmpty)
                            const _EmptyGroup()
                          else
                            Padding(
                              padding: const EdgeInsets.only(top: 6),
                              child: SelectableChips(
                                items: clinical.conditions,
                              ),
                            ),
                          const ReviewSubHeader('Past Surgeries'),
                          if (clinical.surgeries.isEmpty)
                            const _EmptyGroup()
                          else
                            Padding(
                              padding: const EdgeInsets.only(top: 6),
                              child: SelectableChips(
                                items: clinical.surgeries,
                              ),
                            ),
                          const ReviewSubHeader('Allergies'),
                          if (clinical.allergies.isEmpty)
                            const _EmptyGroup()
                          else
                            Padding(
                              padding: const EdgeInsets.only(top: 6),
                              child: SelectableChips(
                                items: clinical.allergies,
                              ),
                            ),
                          const ReviewSubHeader(
                            'Current Medications',
                            dividerAbove: true,
                          ),
                          if (meds.medications.isEmpty)
                            const _EmptyGroup()
                          else
                            for (final MedicationEntry med in meds.medications)
                                KeyValueRow(
                                  label: med.name,
                                  value:
                                      '${med.dosage} · ${med.frequency}',
                                ),
                          const ReviewSubHeader(
                            'Family History',
                            dividerAbove: true,
                          ),
                          if (meds.familyRecords.isEmpty)
                            const _EmptyGroup()
                          else
                            for (final FamilyHistoryRecord record
                                in meds.familyRecords)
                              KeyValueRow(
                                label: record.relative,
                                value:
                                    '${record.condition} at ${record.ageAtDiagnosis}',
                              ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),

                    // ── Active Symptoms ──
                    SectionCard(
                      title: 'Active Symptoms',
                      trailing: EditIconButton(
                        tooltip: 'Edit Active Symptoms',
                        onTap: () => context.go(RouteNames.symptoms),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          if (symptoms.symptoms.isEmpty)
                            const _EmptyGroup()
                          else
                            Padding(
                              padding: const EdgeInsets.only(top: 6),
                              child: SelectableChips(
                                items: symptoms.symptoms,
                              ),
                            ),
                          const SizedBox(height: 8),
                          KeyValueRow(
                            label: 'Severity',
                            value: '',
                            badge:
                                '${symptoms.severity} / 10 · ${severityDescriptor(symptoms.severity)}',
                          ),
                          KeyValueRow(
                            label: 'Duration',
                            value: symptoms.durationValue.isEmpty
                                ? 'Not specified'
                                : symptoms.durationValue,
                            unit: symptoms.durationValue.isEmpty
                                ? null
                                : 'days',
                          ),
                          const ReviewSubHeader('Reported Narrative'),
                          if (symptoms.notes.isEmpty)
                            const _EmptyGroup()
                          else
                            NarrativeBox(symptoms.notes),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),

                    // ── Lab Values ──
                    SectionCard(
                      title: 'Lab Values',
                      trailing: EditIconButton(
                        tooltip: 'Edit Lab Values',
                        onTap: () => context.go(RouteNames.labsVitals),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          const ReviewSubHeader('General Vitals'),
                          KeyValueRow(
                            label: 'Waist Circumference',
                            value: labs.waistCm,
                            unit: 'cm',
                            first: true,
                          ),
                          KeyValueRow(
                            label: 'Blood Pressure',
                            value: '${labs.systolicBp}/${labs.diastolicBp}',
                            unit: 'mmHg',
                          ),
                          const ReviewSubHeader('Lipid Panel'),
                          KeyValueRow(
                            label: 'Total Cholesterol',
                            value: labs.totalCholesterol,
                            unit: 'mg/dL',
                            first: true,
                          ),
                          KeyValueRow(label: 'HDL', value: labs.hdl, unit: 'mg/dL'),
                          KeyValueRow(label: 'LDL', value: labs.ldl, unit: 'mg/dL'),
                          const ReviewSubHeader('Glycemic & Renal'),
                          KeyValueRow(
                            label: 'HbA1c',
                            value: labs.hba1c,
                            unit: '%',
                            first: true,
                          ),
                          KeyValueRow(
                            label: 'Fasting Blood Glucose',
                            value: labs.fastingGlucose,
                            unit: 'mg/dL',
                          ),
                          KeyValueRow(
                            label: 'Serum Creatinine',
                            value: labs.creatinine,
                            unit: 'mg/dL',
                          ),
                          const ReviewSubHeader('Lab Details'),
                          KeyValueRow(
                            label: 'Test Date',
                            value: labs.testDate,
                            first: true,
                          ),
                          KeyValueRow(label: 'Lab Name', value: labs.labName),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),
                    const Text(
                      "Once submitted, your assessment can't be changed.",
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 12,
                        height: 16 / 12,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textMuted,
                      ),
                    ),
                    const SizedBox(height: 10),
                    GradientNextButton(
                      label: 'Submit Assessment',
                      onTap: () async {
                        // Synchronize any pending updates from all wizard steps
                        await ref.read(clinicalStatusProvider.notifier).save();
                        await ref
                            .read(medicationsFamilyProvider.notifier)
                            .save();
                        await ref.read(symptomsProvider.notifier).save();
                        await ref.read(labsVitalsProvider.notifier).save();

                        if (context.mounted) {
                          context.go(RouteNames.results);
                        }
                      },
                    ),
                    BackTextButton(
                      onTap: () => context.go(RouteNames.labsVitals),
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

/// Muted "None reported" placeholder for empty review groups.
class _EmptyGroup extends StatelessWidget {
  const _EmptyGroup();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.only(top: 6),
      child: Text(
        'None reported',
        style: TextStyle(
          fontSize: 14,
          height: 20 / 14,
          fontWeight: FontWeight.w500,
          color: AppColors.textMuted,
        ),
      ),
    );
  }
}
