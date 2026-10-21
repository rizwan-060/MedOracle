import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../widgets/confidence_ring.dart';

/// Primary "Main finding" summary card (design: v8 Step 6A card 1).
///
/// Carries the urgency pill, the flagged condition, the consensus
/// confidence ring and the plain-language summary.
class MainFindingCard extends StatelessWidget {
  const MainFindingCard({
    super.key,
    this.onReasoningTap,
    this.condition = 'Coronary Artery Disease Risk',
    this.urgencyLabel = 'High Urgency',
    this.confidence = 88.5,
    this.summary =
        'Your reported chest pain on exertion, blood pressure history and '
        'cholesterol results together point to an elevated risk of heart '
        'disease. We recommend an in-person check-up with a specialist soon.',
  });

  /// Opens the explainable-AI screen (wired by the router).
  ///
  /// The confidence block is the way in to "How our AI reached this result";
  /// when the callback is null the block renders as plain text.
  final VoidCallback? onReasoningTap;

  final String condition;
  final String urgencyLabel;
  final double confidence;
  final String summary;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(16),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.textPrimary.withValues(alpha: 0.22),
          ),
          BoxShadow(
            color: AppColors.textPrimary.withValues(alpha: 0.06),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Row(
            children: <Widget>[
              const Expanded(
                child: Text(
                  'Main finding',
                  style: TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textMuted,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              _UrgencyPill(label: urgencyLabel),
            ],
          ),
          const SizedBox(height: 14),
          Text(
            condition,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 17,
              height: 27 / 17,
              fontWeight: FontWeight.w800,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 16),
          Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: onReasoningTap,
              borderRadius: BorderRadius.circular(12),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: <Widget>[
                  ConfidenceRing(percent: confidence),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: const <Widget>[
                        Text(
                          'How sure we are',
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w800,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        SizedBox(height: 4),
                        Text(
                          'Our AI analysis is 88.5% sure about this result',
                          style: TextStyle(
                            fontSize: 13,
                            height: 18 / 13,
                            fontWeight: FontWeight.w500,
                            color: AppColors.textMuted,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          Container(
            margin: const EdgeInsets.only(top: 24),
            padding: const EdgeInsets.only(top: 20),
            decoration: const BoxDecoration(
              border: Border(
                top: BorderSide(color: AppColors.borderSubtle),
              ),
            ),
            child: Text(
              summary,
              style: const TextStyle(
                fontSize: 15,
                height: 24 / 15,
                fontWeight: FontWeight.w500,
                color: AppColors.textPrimary,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _UrgencyPill extends StatelessWidget {
  const _UrgencyPill({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 34,
      padding: const EdgeInsets.symmetric(horizontal: 14),
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: AppColors.amberWarning,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w800,
          color: AppColors.cardSurface,
        ),
      ),
    );
  }
}
