import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

/// Frosted button used for secondary actions
/// (`Save & exit` in the header, `Back` in the footer).
/// Standardized with AGENTS.md tokens (footer height 56.0, radius 12.0).
class GlassPillButton extends StatelessWidget {
  /// Translucent white pill on the header (100 x 40).
  const GlassPillButton.header({
    super.key,
    required this.label,
    required this.onTap,
    this._width = 100,
  })  : _fillColor = const Color(0x2EFFFFFF),
        _borderColor = const Color(0x4DFFFFFF),
        _dropShadow = const Color(0x4DFFFFFF),
        _height = 40.0,
        _radius = 12.0,
        _textStyle = AppTextStyles.headerAction;

  /// Secondary action button for the footer (full width, fixed height 56.0, radius 12.0).
  const GlassPillButton.footer({
    super.key,
    required this.label,
    required this.onTap,
    this._width,
  })  : _fillColor = AppColors.cardSurface,
        _borderColor = AppColors.borderSubtle,
        _dropShadow = AppColors.glassPillShadow,
        _height = 56.0,
        _radius = 12.0,
        _textStyle = const TextStyle(
          fontFamily: 'Lexend',
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
        );

  final String label;
  final VoidCallback? onTap;

  final Color _fillColor;
  final Color _borderColor;
  final Color _dropShadow;
  final TextStyle _textStyle;
  final double? _width;
  final double _height;
  final double _radius;

  @override
  Widget build(BuildContext context) {
    final Widget button = Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(_radius),
        child: Ink(
          height: _height,
          decoration: BoxDecoration(
            color: _fillColor,
            border: Border.all(color: _borderColor, width: 1.5),
            borderRadius: BorderRadius.circular(_radius),
            boxShadow: <BoxShadow>[
              BoxShadow(
                color: _dropShadow,
                offset: const Offset(0, 2),
                blurRadius: 8,
              ),
            ],
          ),
          child: Center(
            child: Text(label, style: _textStyle, maxLines: 1),
          ),
        ),
      ),
    );

    if (_width == null) {
      return SizedBox(width: double.infinity, child: button);
    }
    return SizedBox(width: _width, child: button);
  }
}
