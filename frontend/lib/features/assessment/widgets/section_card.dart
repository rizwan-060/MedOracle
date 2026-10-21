import 'package:flutter/material.dart';

import '../../../core/widgets/app_section_card.dart';

/// White rounded card used for each section of an intake step.
/// Delegates directly to the generic [AppSectionCard] core widget.
class SectionCard extends StatelessWidget {
  const SectionCard({
    super.key,
    required this.title,
    required this.child,
    this.subtitle,
    this.trailing,
    this.isActive = false,
    this.isExpanded = true,
    this.onToggle,
  });

  final String title;
  final String? subtitle;
  final Widget? trailing;
  final Widget child;
  final bool isActive;
  final bool isExpanded;
  final VoidCallback? onToggle;

  @override
  Widget build(BuildContext context) {
    return AppSectionCard(
      title: title,
      subtitle: subtitle,
      trailing: trailing,
      isActive: isActive,
      isExpanded: isExpanded,
      onToggle: onToggle,
      child: child,
    );
  }
}
