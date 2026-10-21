import 'package:flutter/material.dart';
import 'package:medoracle/core/theme/app_colors.dart';
import 'package:medoracle/core/theme/app_text_styles.dart';
import 'package:medoracle/data/models/doctor_model.dart';

/// Card describing one specialist, as shown by the care finder.
class DoctorCard extends StatelessWidget {
  const DoctorCard({
    super.key,
    required this.doctor,
    this.onTap,
  });

  /// The specialist to describe.
  final Doctor doctor;

  /// Invoked when the card is tapped.
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      type: MaterialType.transparency,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.cardSurface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.refCardRing),
            boxShadow: <BoxShadow>[
              BoxShadow(
                color: AppColors.refCardShadow,
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Expanded(
                    child: Text(
                      doctor.name,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: AppTextStyles.sectionTitle,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Flexible(
                    child: _SpecialtyBadge(label: doctor.specialty),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(doctor.clinic, style: AppTextStyles.helperText),
              const SizedBox(height: 12),
              Wrap(
                spacing: 14,
                runSpacing: 6,
                children: <Widget>[
                  _MetaItem(
                    icon: Icons.near_me_outlined,
                    label: doctor.distanceLabel,
                  ),
                  _MetaItem(
                    icon: Icons.event_available_outlined,
                    label: doctor.nextAvailable,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Small outlined pill holding the specialty.
class _SpecialtyBadge extends StatelessWidget {
  const _SpecialtyBadge({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: AppColors.canvasBackground,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.refCardRing, width: 1.5),
      ),
      child: Text(
        label,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: AppTextStyles.chipLabel.copyWith(
          fontWeight: FontWeight.w800,
          color: AppColors.refPlum,
        ),
      ),
    );
  }
}

/// Icon + label pair used inside the card.
class _MetaItem extends StatelessWidget {
  const _MetaItem({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        Icon(icon, size: 15, color: AppColors.refSubtitle),
        const SizedBox(width: 5),
        Flexible(
          child: Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: AppTextStyles.metricLabel,
          ),
        ),
      ],
    );
  }
}
