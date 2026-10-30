import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// Maroon header band of the lifestyle simulation screen.
///
/// Shows the "Completed - MedOracle" status, the screen title and subtitle
/// and a glass "Close" pill
/// (design: v8 Step 6C "Simulate Lifestyle Changes" band).
class SimulationBand extends StatelessWidget {
  const SimulationBand({
    super.key,
    required this.title,
    required this.subtitle,
    this.onClose,
  });

  /// Screen title, e.g. `Simulate Lifestyle Changes`.
  final String title;

  /// One-line explanation of what the controls do.
  final String subtitle;

  /// Leaves the simulation (wired by the router).
  final VoidCallback? onClose;

  @override
  Widget build(BuildContext context) {
    return Padding(
      // The band bleeds to the screen edges, the content around it is inset.
      padding: const EdgeInsets.symmetric(horizontal: -20),
      child: DecoratedBox(
        decoration: const BoxDecoration(
          color: AppColors.headerBg,
          borderRadius: BorderRadius.vertical(bottom: Radius.circular(28)),
          boxShadow: <BoxShadow>[
            BoxShadow(
              color: AppColors.headerShadow,
              offset: Offset(0, 18),
              blurRadius: 32,
              spreadRadius: -20,
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: const BorderRadius.vertical(bottom: Radius.circular(28)),
          child: Stack(
            children: <Widget>[
              const Positioned.fill(
                child: DecoratedBox(
                  decoration: BoxDecoration(gradient: AppColors.headerSheenGradient),
                ),
              ),
              const Positioned.fill(
                child: DecoratedBox(
                  decoration: BoxDecoration(gradient: AppColors.headerGlowGradient),
                ),
              ),
              const Positioned(
                top: 0,
                left: 0,
                right: 0,
                child: ColoredBox(
                  color: AppColors.headerHighlight,
                  child: SizedBox(height: 1),
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 8, 20, 22),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: <Widget>[
                    SizedBox(
                      height: 56,
                      child: Row(
                        children: <Widget>[
                          const _StatusDot(),
                          const SizedBox(width: 8),
                          const Expanded(
                            child: Text(
                              'Completed \u00B7 MedOracle',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: AppTextStyles.simulationBandStatus,
                            ),
                          ),
                          _ClosePill(onTap: onClose),
                        ],
                      ),
                    ),
                    const SizedBox(height: 18),
                    Text(
                      title,
                      style: AppTextStyles.instrumentSerif(
                        fontSize: 28,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(subtitle, style: AppTextStyles.simulationSubtitle),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Green status dot of the band, ringed with a soft halo.
class _StatusDot extends StatelessWidget {
  const _StatusDot();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 8,
      height: 8,
      decoration: BoxDecoration(
        color: AppColors.refAutosaveCircle,
        shape: BoxShape.circle,
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.refAutosaveCircle.withValues(alpha: 0.25),
            spreadRadius: 4,
          ),
        ],
      ),
    );
  }
}

/// Glass "Close" pill of the band.
class _ClosePill extends StatelessWidget {
  const _ClosePill({this.onTap});

  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: 'Close',
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: onTap,
        child: Container(
          height: 44,
          padding: const EdgeInsets.symmetric(horizontal: 18),
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: AppColors.cardSurface.withValues(alpha: 0.14),
            borderRadius: BorderRadius.circular(999),
            border: Border.all(
              color: AppColors.cardSurface.withValues(alpha: 0.30),
            ),
          ),
          child: const Text(
            'Close',
            style: TextStyle(
              fontFamily: AppTextStyles.fontFamily,
              fontSize: 13,
              fontWeight: FontWeight.w800,
              color: AppColors.cardSurface,
            ),
          ),
        ),
      ),
    );
  }
}
