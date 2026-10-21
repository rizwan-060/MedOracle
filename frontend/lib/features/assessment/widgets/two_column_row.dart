import 'package:flutter/material.dart';

/// Evenly weighted two-column layout with a 12px gutter, matching the
/// design's "Relative / Age at Diagnosis" pairing.
class TwoColumnRow extends StatelessWidget {
  const TwoColumnRow({super.key, required this.left, required this.right});

  final Widget left;
  final Widget right;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(child: left),
        const SizedBox(width: 12),
        Expanded(child: right),
      ],
    );
  }
}
