import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import 'dashboard_icons.dart';

/// Header bar of the dashboard.
///
/// Shows the avatar and the greeting on the left and the notification bell
/// on the right, with an unread dot while notifications are pending.
class DashboardHeaderBar extends StatelessWidget {
  const DashboardHeaderBar({
    super.key,
    required this.greeting,
    required this.hasUnreadNotifications,
    required this.onNotificationsTap,
  });

  /// Greeting text, e.g. `Hello, Hafsa`.
  final String greeting;

  /// Whether the bell should show its unread dot.
  final bool hasUnreadNotifications;

  /// Invoked when the bell is tapped.
  final VoidCallback onNotificationsTap;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 80,
      child: Padding(
        padding: const EdgeInsets.only(top: 8),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: <Widget>[
            Flexible(
              child: Row(
                children: <Widget>[
                  const _DashboardAvatar(),
                  const SizedBox(width: 12),
                  Flexible(
                    child: Text(
                      greeting,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: AppTextStyles.instrumentSerif(
                        fontSize: 28.0,
                        fontWeight: FontWeight.w600,
                        color: AppColors.headerText,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            _NotificationBell(
              hasUnread: hasUnreadNotifications,
              onTap: onNotificationsTap,
            ),
          ],
        ),
      ),
    );
  }
}

/// Round avatar of the dashboard header.
class _DashboardAvatar extends StatelessWidget {
  const _DashboardAvatar();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 44,
      height: 44,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: AppColors.primaryMaroon.withValues(alpha: 0.08),
        shape: BoxShape.circle,
        border: Border.all(color: AppColors.cardSurface, width: 2),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.controlShadowStrong,
            blurRadius: 12,
            spreadRadius: -4,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: const DashboardIcon(
        DashboardIconType.profile,
        size: 22,
        color: AppColors.primaryMaroon,
      ),
    );
  }
}

/// Notification bell of the dashboard header.
class _NotificationBell extends StatelessWidget {
  const _NotificationBell({required this.hasUnread, required this.onTap});

  /// Whether the unread dot is visible.
  final bool hasUnread;

  /// Invoked when the bell is tapped.
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: hasUnread
          ? 'Notifications, 1 unread'
          : 'Notifications, none unread',
      child: Material(
        color: Colors.transparent,
        shape: const CircleBorder(),
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          onTap: onTap,
          child: Container(
            width: 44,
            height: 44,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: AppColors.cardSurface.withValues(alpha: 0.6),
              shape: BoxShape.circle,
              border: Border.all(
                color: AppColors.cardSurface.withValues(alpha: 0.9),
              ),
              boxShadow: <BoxShadow>[
                BoxShadow(
                  color: AppColors.controlShadowStrong,
                  blurRadius: 14,
                  spreadRadius: -5,
                  offset: const Offset(0, 5),
                ),
              ],
            ),
            child: Stack(
              clipBehavior: Clip.none,
              children: <Widget>[
                const DashboardIcon(
                  DashboardIconType.bell,
                  size: 22,
                  color: AppColors.primaryMaroon,
                ),
                if (hasUnread)
                  Positioned(
                    top: -2,
                    right: -2,
                    child: Container(
                      width: 10,
                      height: 10,
                      decoration: BoxDecoration(
                        color: AppColors.amberWarning,
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: AppColors.canvasBackground,
                          width: 2,
                        ),
                      ),
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
