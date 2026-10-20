import 'package:flutter/material.dart';

import '../theme/app_text_styles.dart';

/// Frosted "glass" pill used for secondary actions
/// (`Save & exit` in the header, `Back` in the footer).
class GlassPillButton extends StatelessWidget {
  /// Translucent white pill on the maroon header (100 x 44).
  const GlassPillButton.header({
    super.key,
    required this.label,
    required this.onTap,
    this._width = 100,
  })  : _topColor = const Color(0x2EFFFFFF),
        _bottomColor = const Color(0x24FFFFFF),
        _borderColor = const Color(0x4DFFFFFF),
        _dropShadow = const Color(0x4DFFFFFF),
        _textStyle = AppTextStyles.headerAction;

  /// Light glass pill used by the footer `Back` action (full width, 44 tall).
  const GlassPillButton.footer({
    super.key,
    required this.label,
    required this.onTap,
    this._width,
  })  : _topColor = const Color(0xE6FFFFFF),
        _bottomColor = const Color(0x8CFFFFFF),
        _borderColor = const Color(0xE6FFFFFF),
        _dropShadow = const Color(0x61614051),
        _textStyle = AppTextStyles.secondaryAction;

  final String label;
  final VoidCallback? onTap;

  final Color _topColor;
  final Color _bottomColor;
  final Color _borderColor;
  final Color _dropShadow;
  final TextStyle _textStyle;
  final double? _width;

  @override
  Widget build(BuildContext context) {
    final Widget button = Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        // Ink splashes are painted on the nearest Material, so paint the
        // decoration into it instead of using a nested `Ink`.
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Ink(
            height: 44,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: <Color>[_topColor, _bottomColor],
              ),
              border: Border.all(color: _borderColor),
              borderRadius: BorderRadius.circular(999),
              boxShadow: <BoxShadow>[
                BoxShadow(
                  color: _dropShadow,
                  offset: const Offset(0, 5),
                  blurRadius: 14,
                  spreadRadius: -5,
                ),
              ],
            ),
            child: Center(
              child: Text(label, style: _textStyle, maxLines: 1),
            ),
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
