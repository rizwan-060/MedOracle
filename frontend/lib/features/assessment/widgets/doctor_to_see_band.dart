import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// Double-ruled divider band naming the recommended specialty
/// (design: "DOCTOR TO SEE — Cardiology" between two 1.5px rules).
class DoctorToSeeBand extends StatelessWidget {
  const DoctorToSeeBand({
    super.key,
    this.specialty = 'Cardiology',
  });

  final String specialty;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 20),
      decoration: const BoxDecoration(
        border: Border.symmetric(
          horizontal: BorderSide(
            color: AppColors.borderSubtle,
            width: 1.5,
          ),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: <Widget>[
          Flexible(
            child: FittedBox(
              fit: BoxFit.scaleDown,
              child: Text(
                'Doctor to see',
                maxLines: 1,
                style: AppTextStyles.lexend(
                  fontSize: 14.0,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.5,
                  color: AppColors.textPrimary,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Flexible(
            child: FittedBox(
              fit: BoxFit.scaleDown,
              child: Text(
                specialty,
                maxLines: 1,
                style: AppTextStyles.instrumentSerif(
                  fontSize: 24.0,
                  fontWeight: FontWeight.w600,
                  color: AppColors.headerText,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
