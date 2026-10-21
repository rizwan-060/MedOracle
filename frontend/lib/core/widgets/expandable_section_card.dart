import 'dart:ui' as ui;

import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';
import 'ref_chevron.dart';

/// Expandable white card used for every intake step section
/// (`Personal Details`, `Body Measurements`, `Lifestyle`, ...).
///
/// The section that is currently open also receives the soft blurred glow
/// painted behind it, exactly like the `.w.a::before` layer of the reference.
class ExpandableSectionCard extends StatelessWidget {
  const ExpandableSectionCard({
    super.key,
    required this.title,
    required this.isExpanded,
    required this.onToggle,
    required this.child,
    this.subtitle,
    this.showGlow = true,
  });

  final String title;
  final String? subtitle;
  final bool isExpanded;
  final VoidCallback onToggle;

  /// Content revealed while the section is expanded.
  final Widget child;

  /// Whether the blurred glow is painted behind the card while expanded.
  final bool showGlow;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 12),
      child: _SectionGlow(
        active: isExpanded && showGlow,
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: const BoxDecoration(
            color: AppColors.cardSurface,
            borderRadius: BorderRadius.all(Radius.circular(16)),
            boxShadow: <BoxShadow>[
              BoxShadow(
                color: AppColors.refCardRing,
                blurRadius: 0,
                spreadRadius: 1,
              ),
              BoxShadow(
                color: AppColors.refCardShadow,
                offset: Offset(0, 2),
                blurRadius: 8,
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: <Widget>[
              _SectionHeader(
                title: title,
                subtitle: subtitle,
                expanded: isExpanded,
                onTap: onToggle,
              ),
              if (isExpanded)
                Padding(
                  padding: const EdgeInsets.only(top: 6),
                  child: child,
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({
    required this.title,
    required this.subtitle,
    required this.expanded,
    required this.onTap,
  });

  final String? title;
  final String? subtitle;
  final bool expanded;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      expanded: expanded,
      label: title,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: ConstrainedBox(
            constraints: const BoxConstraints(minHeight: 44),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: <Widget>[
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      Text(title ?? '', style: AppTextStyles.sectionTitle),
                      if (subtitle != null) ...<Widget>[
                        const SizedBox(height: 2),
                        Text(subtitle!, style: AppTextStyles.sectionSubtitle),
                      ],
                    ],
                  ),
                ),
                const SizedBox(width: 10),
                RefChevron(rotated: expanded),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Paints the blurred two-tint glow that sits behind the active card.
class _SectionGlow extends StatelessWidget {
  const _SectionGlow({required this.active, required this.child});

  final bool active;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    if (!active) {
      return child;
    }
    return Stack(
      clipBehavior: Clip.none,
      children: <Widget>[
        Positioned(
          left: -8,
          right: -8,
          top: -16,
          bottom: -16,
          child: ImageFiltered(
            imageFilter: ui.ImageFilter.blur(sigmaX: 14, sigmaY: 14),
            child: const CustomPaint(painter: _GlowPainter()),
          ),
        ),
        child,
      ],
    );
  }
}

class _GlowPainter extends CustomPainter {
  const _GlowPainter();

  @override
  void paint(Canvas canvas, Size size) {
    if (size.isEmpty) {
      return;
    }

    final Rect rect = Offset.zero & size;
    final RRect rrect =
        RRect.fromRectAndRadius(rect, const Radius.circular(34));

    canvas.save();
    canvas.clipRRect(rrect);

    // Reference: two radial gradients (circle at 90% -10% and 15% 25%).
    final Offset centerB = Offset(size.width * 0.90, size.height * 0.85);
    final double radiusB = (Offset(size.width, 0) - centerB).distance;
    _drawRadial(canvas, rect, centerB, radiusB, AppColors.refGlowB);

    final Offset centerA = Offset(size.width * 0.15, size.height * 0.25);
    final double radiusA = (Offset(size.width, size.height) - centerA).distance;
    _drawRadial(canvas, rect, centerA, radiusA, AppColors.refGlowA);

    canvas.restore();
  }

  void _drawRadial(
    Canvas canvas,
    Rect rect,
    Offset center,
    double radius,
    Color color,
  ) {
    final Paint paint = Paint()
      ..shader = ui.Gradient.radial(
        center,
        radius,
        <Color>[color, color.withValues(alpha: 0)],
        const <double>[0, 0.55],
      );
    canvas.drawRect(rect, paint);
  }

  @override
  bool shouldRepaint(_GlowPainter oldDelegate) => false;
}
