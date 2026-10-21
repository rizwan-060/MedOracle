import 'dart:ui' show PathMetric;
import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// Button styling variants supported by [AppButton].
enum AppButtonVariant {
  /// Primary CTA button with maroon vertical gradient and subtle drop shadow.
  gradient,

  /// Dashed outline button, typically used for additive actions (+ Add Condition).
  dashed,

  /// Compact rounded pill button, typically used in section headers.
  pill,

  /// Bordered outline button.
  outline,

  /// Flat subtle text button, typically used for secondary "Back" actions.
  text,
}

/// Generic, highly reusable button component for MedOracle.
///
/// Encapsulates all button design patterns across the application, supporting
/// custom colors, icons, loading indicators, and tactile feedback.
class AppButton extends StatefulWidget {
  const AppButton({
    super.key,
    required this.label,
    this.onTap,
    this.variant = AppButtonVariant.gradient,
    this.icon,
    this.isLoading = false,
    this.height,
    this.width,
    this.backgroundColor,
    this.textColor,
    this.borderColor,
    this.gradientColors,
    this.borderRadius,
    this.fontSize,
  });

  final String label;
  final VoidCallback? onTap;
  final AppButtonVariant variant;
  final Widget? icon;
  final bool isLoading;
  final double? height;
  final double? width;
  final Color? backgroundColor;
  final Color? textColor;
  final Color? borderColor;
  final List<Color>? gradientColors;
  final double? borderRadius;
  final double? fontSize;

  @override
  State<AppButton> createState() => _AppButtonState();
}

class _AppButtonState extends State<AppButton> {
  bool _pressed = false;

  void _onTapDown(TapDownDetails details) {
    if (widget.onTap != null && !widget.isLoading) {
      setState(() => _pressed = true);
    }
  }

  void _onTapUp(TapUpDetails details) {
    if (_pressed) {
      setState(() => _pressed = false);
    }
  }

  void _onTapCancel() {
    if (_pressed) {
      setState(() => _pressed = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    switch (widget.variant) {
      case AppButtonVariant.gradient:
        return _buildGradientButton();
      case AppButtonVariant.dashed:
        return _buildDashedButton();
      case AppButtonVariant.pill:
        return _buildPillButton();
      case AppButtonVariant.outline:
        return _buildOutlineButton();
      case AppButtonVariant.text:
        return _buildTextButton();
    }
  }

  Widget _buildGradientButton() {
    final double h = widget.height ?? 48.0;
    final double r = widget.borderRadius ?? 999.0;
    final List<Color> colors = widget.gradientColors ??
        const <Color>[
          AppColors.primaryMaroon,
          AppColors.primaryMaroon,
          AppColors.maroonDark,
        ];

    return GestureDetector(
      onTapDown: _onTapDown,
      onTapUp: _onTapUp,
      onTapCancel: _onTapCancel,
      onTap: widget.isLoading ? null : widget.onTap,
      child: AnimatedScale(
        duration: const Duration(milliseconds: 90),
        scale: _pressed ? 0.98 : 1.0,
        child: Container(
          height: h,
          width: widget.width,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: colors,
              stops: const <double>[0, 0.55, 1],
            ),
            borderRadius: BorderRadius.circular(r),
            border: Border.all(
              color: AppColors.cardSurface.withValues(alpha: 0.22),
            ),
            boxShadow: <BoxShadow>[
              BoxShadow(
                color: AppColors.maroonDark.withValues(alpha: 0.7),
                blurRadius: 24,
                spreadRadius: -8,
                offset: const Offset(0, 12),
              ),
              BoxShadow(
                color: AppColors.textPrimary.withValues(alpha: 0.3),
                blurRadius: 3,
                offset: const Offset(0, 1),
              ),
            ],
          ),
          alignment: Alignment.center,
          child: widget.isLoading
              ? const SizedBox(
                  height: 18,
                  width: 18,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                  ),
                )
              : Row(
                  mainAxisSize: MainAxisSize.min,
                  children: <Widget>[
                    if (widget.icon != null) ...[
                      widget.icon!,
                      const SizedBox(width: 8),
                    ],
                    Text(
                      widget.label,
                      style: TextStyle(
                        fontSize: widget.fontSize ?? 16,
                        fontWeight: FontWeight.w700,
                        color: widget.textColor ?? AppColors.cardSurface,
                      ),
                    ),
                  ],
                ),
        ),
      ),
    );
  }

  Widget _buildDashedButton() {
    final double h = widget.height ?? 44.0;
    final double r = widget.borderRadius ?? 12.0;
    final Color stroke = widget.borderColor ?? AppColors.dustyTaupe;
    final Color text = widget.textColor ?? AppColors.primaryMaroon;

    return GestureDetector(
      onTapDown: _onTapDown,
      onTapUp: _onTapUp,
      onTapCancel: _onTapCancel,
      onTap: widget.isLoading ? null : widget.onTap,
      child: AnimatedScale(
        duration: const Duration(milliseconds: 90),
        scale: _pressed ? 0.98 : 1.0,
        child: CustomPaint(
          painter: _DashedBorderPainter(
            color: stroke,
            radius: Radius.circular(r),
          ),
          child: Container(
            height: h,
            width: widget.width,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: widget.backgroundColor ??
                  AppColors.cardSurface.withValues(alpha: 0.55),
              borderRadius: BorderRadius.circular(r),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: <Widget>[
                if (widget.icon != null) ...[
                  widget.icon!,
                  const SizedBox(width: 6),
                ],
                Text(
                  widget.label,
                  style: TextStyle(
                    fontSize: widget.fontSize ?? 14,
                    fontWeight: FontWeight.w800,
                    color: text,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPillButton() {
    final double h = widget.height ?? 26.0;
    final double r = widget.borderRadius ?? 13.0;

    return GestureDetector(
      onTap: widget.isLoading ? null : widget.onTap,
      child: Container(
        height: h,
        padding: const EdgeInsets.symmetric(horizontal: 10),
        decoration: BoxDecoration(
          color: widget.backgroundColor ?? AppColors.cardSurface,
          borderRadius: BorderRadius.circular(r),
          border: Border.all(
            color: widget.borderColor ?? AppColors.borderSubtle,
            width: 1.0,
          ),
        ),
        alignment: Alignment.center,
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            if (widget.icon != null) ...[
              widget.icon!,
              const SizedBox(width: 4),
            ],
            Text(
              widget.label,
              style: TextStyle(
                fontSize: widget.fontSize ?? 11,
                fontWeight: FontWeight.w600,
                color: widget.textColor ?? AppColors.primaryMaroon,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOutlineButton() {
    final double h = widget.height ?? 40.0;
    final double r = widget.borderRadius ?? 12.0;

    return GestureDetector(
      onTap: widget.isLoading ? null : widget.onTap,
      child: Container(
        height: h,
        width: widget.width,
        decoration: BoxDecoration(
          color: widget.backgroundColor ?? Colors.transparent,
          borderRadius: BorderRadius.circular(r),
          border: Border.all(
            color: widget.borderColor ?? AppColors.borderSubtle,
            width: 1.5,
          ),
        ),
        alignment: Alignment.center,
        child: Text(
          widget.label,
          style: TextStyle(
            fontSize: widget.fontSize ?? 13,
            fontWeight: FontWeight.w600,
            color: widget.textColor ?? AppColors.textPrimary,
          ),
        ),
      ),
    );
  }

  Widget _buildTextButton() {
    return GestureDetector(
      onTap: widget.isLoading ? null : widget.onTap,
      child: Container(
        height: widget.height ?? 44.0,
        margin: const EdgeInsets.only(top: 4),
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: widget.backgroundColor ??
              AppColors.cardSurface.withValues(alpha: 0.55),
          borderRadius: BorderRadius.circular(widget.borderRadius ?? 999.0),
          border: Border.all(
            color: widget.borderColor ??
                AppColors.cardSurface.withValues(alpha: 0.9),
          ),
        ),
        child: Text(
          widget.label,
          style: TextStyle(
            fontSize: widget.fontSize ?? 14,
            fontWeight: FontWeight.w700,
            color: widget.textColor ?? AppColors.primaryMaroon,
          ),
        ),
      ),
    );
  }
}

class _DashedBorderPainter extends CustomPainter {
  const _DashedBorderPainter({required this.color, required this.radius});

  final Color color;
  final Radius radius;

  @override
  void paint(Canvas canvas, Size size) {
    final RRect rrect = RRect.fromRectAndRadius(
      Offset.zero & size,
      radius,
    );
    final Path path = Path()..addRRect(rrect);
    final Paint paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;

    const double dash = 6;
    const double gap = 4;
    for (final PathMetric metric in path.computeMetrics()) {
      double distance = 0;
      while (distance < metric.length) {
        canvas.drawPath(
          metric.extractPath(distance, distance + dash),
          paint,
        );
        distance += dash + gap;
      }
    }
  }

  @override
  bool shouldRepaint(_DashedBorderPainter oldDelegate) =>
      oldDelegate.color != color || oldDelegate.radius != radius;
}
