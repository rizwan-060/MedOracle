import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../widgets/confidence_ring.dart';

/// Primary "Main finding" summary card adhering to AGENTS.md tokens
/// (Radius 12.0, AppColors.borderSubtle, Instrument Serif header, Lexend body).
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
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(color: AppColors.borderSubtle, width: 1.5),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.textPrimary.withValues(alpha: 0.04),
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
              Expanded(
                child: Text(
                  'Main finding',
                  style: AppTextStyles.instrumentSerif(
                    fontSize: 24.0,
                    fontWeight: FontWeight.w600,
                    color: AppColors.headerText,
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
            textAlign: TextAlign.left,
            style: AppTextStyles.lexend(
              fontSize: 17.0,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 16),
          Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: onReasoningTap,
              borderRadius: BorderRadius.circular(12.0),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: <Widget>[
                  ConfidenceRing(percent: confidence),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Text(
                          'How sure we are',
                          style: AppTextStyles.lexend(
                            fontSize: 15.0,
                            fontWeight: FontWeight.w700,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Our AI analysis is 88.5% sure about this result',
                          style: AppTextStyles.lexend(
                            fontSize: 13.0,
                            fontWeight: FontWeight.w400,
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
              style: AppTextStyles.lexend(
                fontSize: 14.0,
                height: 1.5,
                fontWeight: FontWeight.w400,
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
      height: 32,
      padding: const EdgeInsets.symmetric(horizontal: 14),
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: AppColors.urgencyBadgeFill,
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(color: AppColors.urgencyBadgeText.withValues(alpha: 0.3)),
      ),
      child: Text(
        label,
        style: AppTextStyles.lexend(
          fontSize: 12.0,
          fontWeight: FontWeight.w700,
          color: AppColors.urgencyBadgeText,
        ),
      ),
    );
  }
}
