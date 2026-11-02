import 'dart:ui' show ImageFilter;

import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../models/dashboard_models.dart';
import 'dashboard_icons.dart';

/// Bottom navigation bar of the dashboard.
///
/// A translucent, blurred sheet pinned to the bottom of the screen that
/// mirrors the app's four top level destinations.
class DashboardBottomNavBar extends StatelessWidget {
  const DashboardBottomNavBar({
    super.key,
    required this.selected,
    required this.onSelected,
  });

  /// The destination that is currently active.
  final DashboardDestination selected;

  /// Invoked with the destination the user tapped.
  final ValueChanged<DashboardDestination> onSelected;

  @override
  Widget build(BuildContext context) {
    return ClipRect(
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
        child: Container(
          padding: const EdgeInsets.fromLTRB(12, 8, 12, 22),
          decoration: BoxDecoration(
            color: AppColors.canvasBackground.withValues(alpha: 0.82),
            border: Border(
              top: BorderSide(
                color: AppColors.cardSurface.withValues(alpha: 0.95),
              ),
            ),
            boxShadow: <BoxShadow>[
              BoxShadow(
                color: AppColors.controlShadowStrong,
                blurRadius: 30,
                spreadRadius: -14,
                offset: const Offset(0, -12),
              ),
            ],
          ),
          child: SafeArea(
            top: false,
            child: Row(
              children: <Widget>[
                for (final DashboardDestination destination
                    in DashboardDestination.values)
                  Expanded(
                    child: _NavDestinationTile(
                      destination: destination,
                      isSelected: destination == selected,
                      onTap: () => onSelected(destination),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// A single tab of the bottom navigation bar.
class _NavDestinationTile extends StatelessWidget {
  const _NavDestinationTile({
    required this.destination,
    required this.isSelected,
    required this.onTap,
  });

  /// The destination this tab represents.
  final DashboardDestination destination;

  /// Whether this tab is the active one.
  final bool isSelected;

  /// Invoked when the tab is tapped.
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final Color foreground =
        isSelected ? AppColors.textPrimary : AppColors.textMuted;
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
              Container(
                width: 56,
                height: 32,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: isSelected
                      ? AppColors.primaryMaroon.withValues(alpha: 0.08)
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(999),
                ),
                child: DashboardIcon(
                  _iconFor(destination),
                  size: 24,
                  color: foreground,
                  strokeWidth: destination == DashboardDestination.home
                      ? 1.9
                      : 1.8,
                  filled: destination == DashboardDestination.home && isSelected,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                _labelFor(destination),
                style: isSelected
                    ? AppTextStyles.dashboardNavLabelActive
                    : AppTextStyles.dashboardNavLabel,
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Glyph of the destination.
  static DashboardIconType _iconFor(DashboardDestination destination) {
    return switch (destination) {
      DashboardDestination.home => DashboardIconType.home,
      DashboardDestination.history => DashboardIconType.history,
      DashboardDestination.doctors => DashboardIconType.doctors,
      DashboardDestination.profile => DashboardIconType.profile,
    };
  }

  /// Caption of the destination.
  static String _labelFor(DashboardDestination destination) {
    return switch (destination) {
      DashboardDestination.home => 'Home',
      DashboardDestination.history => 'History',
      DashboardDestination.doctors => 'Doctors',
      DashboardDestination.profile => 'Profile',
    };
  }
}
