import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// What-if slider of the lifestyle simulation.
///
/// Reproduces the design reference's range input: a 4px track that fills with
/// the slate accent, a 28px white thumb with a soft drop shadow and a focus
/// ring
/// (design: v8 Step 6C range control).
class LifestyleSlider extends StatefulWidget {
  const LifestyleSlider({
    super.key,
    required this.value,
    required this.max,
    required this.onChanged,
    required this.semanticLabel,
  });

  /// Current value of the slider.
  final int value;

  /// Largest value the slider can take.
  final int max;

  /// Called with the new value while the slider is dragged.
  final ValueChanged<int> onChanged;

  /// Accessible name of the slider, e.g. `Weight reduction`.
  final String semanticLabel;

  @override
  State<LifestyleSlider> createState() => _LifestyleSliderState();
}

class _LifestyleSliderState extends State<LifestyleSlider> {
  bool _focused = false;

  @override
  Widget build(BuildContext context) {
    return Focus(
      onFocusChange: (bool focused) {
        if (focused != _focused) {
          setState(() => _focused = focused);
        }
      },
      child: SizedBox(
        height: 32,
        child: SliderTheme(
          data: SliderTheme.of(context).copyWith(
            trackHeight: 4,
            activeTrackColor: AppColors.refControlAccent,
            inactiveTrackColor: AppColors.refControlTrackIdle,
            trackShape: const RoundedRectSliderTrackShape(),
            thumbShape: _SimulationThumbShape(focused: _focused),
            overlayShape: const _NoOverlayShape(),
            showValueIndicator: ShowValueIndicator.never,
          ),
          child: Slider(
            value: widget.value.toDouble(),
            max: widget.max.toDouble(),
            divisions: widget.max,
            label: '${widget.value}',
            semanticFormatterCallback: (double value) =>
                '${widget.semanticLabel}: ${value.round()}',
            onChanged: (double value) => widget.onChanged(value.round()),
          ),
        ),
      ),
    );
  }
}

/// White thumb with a hairline edge and a soft drop shadow.
class _SimulationThumbShape extends SliderComponentShape {
  const _SimulationThumbShape({required this.focused});

  /// Whether the slider currently has keyboard focus.
  final bool focused;

  @override
  Size getPreferredSize(bool isEnabled, bool isDiscrete) {
    return const Size(28, 28);
  }

  @override
  void paint(
    PaintingContext context,
    Offset center, {
    required Animation<double> activationAnimation,
    required Animation<double> enableAnimation,
    required bool isDiscrete,
    required TextPainter labelPainter,
    required RenderBox parentBox,
    required Size sizeWithOverflow,
    required SliderThemeData sliderTheme,
    required TextDirection textDirection,
    required double textScaleFactor,
    required double value,
  }) {
    final Canvas canvas = context.canvas;

    if (focused) {
      canvas.drawCircle(
        center,
        18,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 4
          ..color = AppColors.refControlAccent.withValues(alpha: 0.45),
      );
    }

    canvas.drawCircle(
      center.translate(0, 2),
      14,
      Paint()
        ..color = AppColors.textPrimary.withValues(alpha: 0.32)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 3),
    );

    canvas.drawCircle(center, 14, Paint()..color = AppColors.cardSurface);

    canvas.drawCircle(
      center,
      14,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 0.5
        ..color = AppColors.textPrimary.withValues(alpha: 0.12),
    );
  }
}

/// Swallows the default drag overlay so the thumb keeps the reference look.
class _NoOverlayShape extends SliderComponentShape {
  const _NoOverlayShape();

  @override
  Size getPreferredSize(bool isEnabled, bool isDiscrete) => Size.zero;

  @override
  void paint(
    PaintingContext context,
    Offset center, {
    required Animation<double> activationAnimation,
    required Animation<double> enableAnimation,
    required bool isDiscrete,
    required TextPainter labelPainter,
    required RenderBox parentBox,
    required Size sizeWithOverflow,
    required SliderThemeData sliderTheme,
    required TextDirection textDirection,
    required double textScaleFactor,
    required double value,
  }) {}
}
