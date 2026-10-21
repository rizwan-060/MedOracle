import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Double-ruled divider band naming the recommended specialty
/// (design: "DOCTOR TO SEE — Cardiology" between two 2px rules).
class DoctorToSeeBand extends StatelessWidget {
  const DoctorToSeeBand({
    super.key,
    this.specialty = 'Cardiology',
  });

  final String specialty;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 22),
      decoration: const BoxDecoration(
        border: Border.symmetric(
          horizontal: BorderSide(
            color: AppColors.dustyTaupe,
            width: 2,
          ),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: <Widget>[
          Flexible(
            child: FittedBox(
              fit: BoxFit.scaleDown,
              child: Text(
                'Doctor to see',
                maxLines: 1,
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 17 * 0.08,
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
                style: const TextStyle(
                  fontSize: 28,
                  height: 34 / 28,
                  fontWeight: FontWeight.w700,
                  fontStyle: FontStyle.italic,
                  color: AppColors.textPrimary,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
