import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../models/dashboard_models.dart';
import 'dashboard_icons.dart';
import 'dashboard_risk_gauge.dart';

/// Hero metric card of the dashboard.
///
/// Shows the latest risk result - score gauge, condition name and urgency -
/// on a maroon surface, and links through to the full report.
class DashboardHeroMetricCard extends StatelessWidget {
  const DashboardHeroMetricCard({
    super.key,
    required this.result,
    this.onViewReport,
  });

  /// The risk result to display.
  final DashboardRiskResult result;

  /// Invoked when the user taps "View Full Report".
  final VoidCallback? onViewReport;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 6),
      decoration: BoxDecoration(
        color: AppColors.headerBg,
        borderRadius: BorderRadius.circular(12.0),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.headerShadow,
            blurRadius: 40,
            spreadRadius: -18,
            offset: const Offset(0, 22),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12.0),
        child: Stack(
          children: <Widget>[
            DecoratedBox(
              decoration: const BoxDecoration(
                gradient: AppColors.headerGlowGradient,
              ),
              child: DecoratedBox(
                decoration: const BoxDecoration(
                  gradient: AppColors.headerSheenGradient,
                ),
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      Text(
                        'LATEST RESULT',
                        style: AppTextStyles.dashboardHeroEyebrow.copyWith(
                          color: AppColors.onPlum.withValues(alpha: 0.82),
                        ),
                      ),
                      const SizedBox(height: 10),
                      DashboardRiskGauge(score: result.score),
                      const SizedBox(height: 6),
                      Text(
                        result.condition,
                        textAlign: TextAlign.center,
                        style: AppTextStyles.dashboardHeroTitle,
                      ),
                      const SizedBox(height: 10),
                      _UrgencyBadge(label: result.urgencyLabel),
                      const SizedBox(height: 18),
                      _ViewReportButton(onTap: onViewReport),
                    ],
                  ),
                ),
              ),
            ),
            // 1px inset highlight along the top edge of the maroon surface.
            const Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: SizedBox(
                height: 1,
                child: ColoredBox(color: AppColors.headerHighlight),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Urgency pill of the hero metric card.
class _UrgencyBadge extends StatelessWidget {
  const _UrgencyBadge({required this.label});

  /// Urgency text, e.g. `High urgency`.
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 32,
      padding: const EdgeInsets.symmetric(horizontal: 14),
      decoration: BoxDecoration(
        color: AppColors.amberSurface,
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(color: AppColors.amberWarning),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Container(
            width: 8,
            height: 8,
            decoration: const BoxDecoration(
              color: AppColors.amberWarning,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 6),
          Text(label, style: AppTextStyles.dashboardUrgency),
        ],
      ),
    );
  }
}

/// "View Full Report" pill of the hero metric card.
class _ViewReportButton extends StatelessWidget {
  const _ViewReportButton({this.onTap});

  /// Invoked when the pill is tapped.
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12.0),
        gradient: const LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: <Color>[AppColors.canvasBackground, AppColors.borderSubtle],
        ),
        border: Border.all(
          color: AppColors.onPlum.withValues(alpha: 0.7),
        ),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.controlShadowStrong,
            blurRadius: 22,
            spreadRadius: -8,
            offset: const Offset(0, 10),
          ),
          BoxShadow(
            color: AppColors.controlShadowSoft,
            blurRadius: 3,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(12.0),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12.0),
          child: SizedBox(
            height: 56.0,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                Flexible(
                  child: Text(
                    'View Full Report',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: AppTextStyles.dashboardHeroAction,
                  ),
                ),
                const SizedBox(width: 8),
                const DashboardIcon(
                  DashboardIconType.arrowRight,
                  size: 18,
                  color: AppColors.textPrimary,
                  strokeWidth: 2.2,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Primary dashboard action card - the "Start New Assessment" entry point.
///
/// Rendered as a wide row: icon tile, title + sub-title and a trailing
/// chevron. The ring around the card marks it as the primary action.
class DashboardPrimaryActionCard extends StatelessWidget {
  const DashboardPrimaryActionCard({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
    this.onTap,
  });

  /// Glyph rendered in the leading icon tile.
  final DashboardIconType icon;

  /// Card title.
  final String title;

  /// Supporting copy below the title.
  final String subtitle;

  /// Invoked when the card is tapped.
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return _DashboardCardSurface(
      ringColor: AppColors.dustyTaupe,
      ringWidth: 2,
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: <Widget>[
            DashboardIconTile(icon: icon),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: <Widget>[
                  Text(
                    title,
                    style: AppTextStyles.dashboardCardTitle,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: AppTextStyles.dashboardCardSubtitle,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            const SizedBox(width: 14),
            const DashboardChevronBadge(),
          ],
        ),
      ),
    );
  }
}

/// Compact dashboard action card - a secondary quick action.
///
/// Rendered as a vertical stack with the chevron pinned to the top right
/// corner.
class DashboardCompactActionCard extends StatelessWidget {
  const DashboardCompactActionCard({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
    this.onTap,
  });

  /// Glyph rendered in the leading icon tile.
  final DashboardIconType icon;

  /// Card title.
  final String title;

  /// Supporting copy below the title.
  final String subtitle;

  /// Invoked when the card is tapped.
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return _DashboardCardSurface(
      onTap: onTap,
      child: ConstrainedBox(
        constraints: const BoxConstraints(minHeight: 132),
        child: Stack(
          children: <Widget>[
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: <Widget>[
                  DashboardIconTile(icon: icon, size: 44, iconSize: 24),
                  const SizedBox(height: 12),
                  Text(
                    title,
                    style: AppTextStyles.dashboardCompactTitle,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: AppTextStyles.dashboardCompactSubtitle,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            const Positioned(
              top: 16,
              right: 16,
              child: DashboardChevronBadge(size: 28, strokeWidth: 2.4),
            ),
          ],
        ),
      ),
    );
  }
}

/// Shared white surface used by every dashboard action card.
class _DashboardCardSurface extends StatelessWidget {
  const _DashboardCardSurface({
    required this.child,
    this.onTap,
    this.ringColor,
    this.ringWidth = 1,
  });

  final Widget child;
  final VoidCallback? onTap;
  final Color? ringColor;
  final double ringWidth;

  @override
  Widget build(BuildContext context) {
    final Color? ring = ringColor;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(12.0),
        boxShadow: <BoxShadow>[
          if (ring != null)
            BoxShadow(
              color: ring,
              blurRadius: 0,
              spreadRadius: ringWidth,
            )
          else
            BoxShadow(
              color: AppColors.dustyTaupe.withValues(alpha: 0.45),
              blurRadius: 0,
              spreadRadius: 1,
            ),
          BoxShadow(
            color: AppColors.controlShadowStrong,
            blurRadius: 26,
            spreadRadius: -14,
            offset: const Offset(0, 12),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(12.0),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12.0),
          child: child,
        ),
      ),
    );
  }
}

/// Rounded icon tile used by the dashboard action cards.
class DashboardIconTile extends StatelessWidget {
  const DashboardIconTile({
    super.key,
    required this.icon,
    this.size = 48,
    this.iconSize = 26,
  });

  /// Glyph rendered inside the tile.
  final DashboardIconType icon;

  /// Edge length of the tile.
  final double size;

  /// Edge length of the glyph.
  final double iconSize;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: AppColors.primaryMaroon.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(14),
      ),
      child: DashboardIcon(
        icon,
        size: iconSize,
        color: AppColors.primaryMaroon,
      ),
    );
  }
}

/// Small circular chevron that trails a dashboard action card.
class DashboardChevronBadge extends StatelessWidget {
  const DashboardChevronBadge({
    super.key,
    this.size = 32,
    this.strokeWidth = 2.2,
  });

  /// Edge length of the badge.
  final double size;

  /// Stroke width of the chevron glyph.
  final double strokeWidth;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: AppColors.primaryMaroon.withValues(alpha: 0.07),
        shape: BoxShape.circle,
      ),
      child: DashboardIcon(
        DashboardIconType.chevronRight,
        size: size * 0.5,
        color: AppColors.primaryMaroon,
        strokeWidth: strokeWidth,
      ),
    );
  }
}
