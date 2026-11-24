import 'package:google_fonts/google_fonts.dart';
import 'package:material_ui/material_ui.dart';

import '../../../core/theme/app_colors.dart';

/// Shared native chrome for the Step 2B–5 intake screens.
abstract final class IntakeType {
  static TextStyle sans(
    double size,
    FontWeight weight,
    Color color, {
    double? height,
    double? spacing,
  }) =>
      GoogleFonts.lexend(
        fontSize: size,
        fontWeight: weight,
        color: color,
        height: height,
        letterSpacing: spacing,
      );

  static TextStyle serif(
    double size,
    FontWeight weight,
    Color color, {
    double? height,
  }) =>
      GoogleFonts.newsreader(
        fontSize: size,
        fontWeight: weight,
        color: color,
        height: height,
      );

  static TextStyle jakarta(
    double size,
    FontWeight weight,
    Color color, {
    double? height,
    double? spacing,
  }) =>
      TextStyle(
        fontFamily: 'Plus Jakarta Sans',
        fontSize: size,
        fontWeight: weight,
        color: color,
        height: height,
        letterSpacing: spacing,
      );
}

/// Slate intake header with autosave status, wordmark, save/exit pill and the
/// five-segment progress rail.
class IntakeHeader extends StatelessWidget {
  const IntakeHeader({super.key, required this.step});

  /// 1-based step number shown in the progress rail.
  final int step;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.headerText,
        borderRadius: const BorderRadius.vertical(bottom: Radius.circular(28)),
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: <Color>[
            AppColors.cardSurface.withValues(alpha: 0.1),
            AppColors.cardSurface.withValues(alpha: 0),
            AppColors.deepInk.withValues(alpha: 0.2),
          ],
          stops: const <double>[0, 0.45, 1],
        ),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.deepInk.withValues(alpha: 0.5),
            blurRadius: 32,
            spreadRadius: -20,
            offset: const Offset(0, 18),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            SizedBox(
              height: 24,
              child: Row(
                children: <Widget>[
                  SizedBox(
                    width: 92,
                    child: Row(
                      children: <Widget>[
                        Icon(
                          Icons.check,
                          size: 16,
                          color: AppColors.pastelSage,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          'Autosaved',
                          style: IntakeType.sans(
                            11,
                            FontWeight.w500,
                            AppColors.pastelSage,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const Expanded(child: Center(child: _Brand())),
                  SizedBox(
                    width: 92,
                    child: Align(
                      alignment: Alignment.centerRight,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: AppColors.cardSurface.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(999),
                          border: Border.all(
                            color: AppColors.cardSurface.withValues(alpha: 0.4),
                          ),
                        ),
                        child: Text(
                          'Save & exit',
                          style: IntakeType.sans(
                            12,
                            FontWeight.w500,
                            AppColors.cardSurface,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: <Widget>[
                for (int i = 1; i <= 5; i++) ...<Widget>[
                  if (i > 1) const SizedBox(width: 6),
                  Expanded(
                    child: Container(
                      height: 4,
                      decoration: BoxDecoration(
                        color: i <= step
                            ? AppColors.cardSurface
                            : AppColors.cardSurface.withValues(alpha: 0.3),
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _Brand extends StatelessWidget {
  const _Brand();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        Icon(Icons.health_and_safety_outlined,
            size: 20, color: AppColors.cardSurface),
        const SizedBox(width: 6),
        Text(
          'MedOracle',
          style: IntakeType.sans(
            16,
            FontWeight.w600,
            AppColors.cardSurface,
          ),
        ),
      ],
    );
  }
}

/// White action bar used at the bottom of every Step 3–5 screen.
class IntakeFooter extends StatelessWidget {
  const IntakeFooter({
    super.key,
    required this.ctaLabel,
    required this.onBack,
    required this.onContinue,
    this.backLabel = 'Back',
  });

  final String backLabel;
  final String ctaLabel;
  final VoidCallback onBack;
  final VoidCallback onContinue;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 12),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        border: Border(top: BorderSide(color: AppColors.borderSubtle)),
      ),
      child: Row(
        children: <Widget>[
          Expanded(child: _FooterPill(label: backLabel, onTap: onBack)),
          const SizedBox(width: 12),
          Expanded(
            flex: 2,
            child: _FooterPill(
              label: ctaLabel,
              filled: true,
              onTap: onContinue,
            ),
          ),
        ],
      ),
    );
  }
}

class _FooterPill extends StatelessWidget {
  const _FooterPill({
    required this.label,
    required this.onTap,
    this.filled = false,
  });

  final String label;
  final VoidCallback onTap;
  final bool filled;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 44,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(999),
          child: Container(
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: filled ? AppColors.terraCotta : AppColors.cardSurface,
              borderRadius: BorderRadius.circular(999),
              border: filled
                  ? null
                  : Border.all(color: AppColors.headerText.withValues(alpha: 0.4)),
            ),
            child: Text(
              label,
              style: IntakeType.sans(
                14,
                FontWeight.w500,
                filled ? AppColors.cardSurface : AppColors.headerText,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Thin divider used between intake sections.
class SectionDivider extends StatelessWidget {
  const SectionDivider({super.key});

  @override
  Widget build(BuildContext context) => Container(
        height: 1,
        color: AppColors.headerText.withValues(alpha: 0.4),
      );
}

/// Round outlined/solid stepper button (− / +) used by the intake forms.
class StepperButton extends StatelessWidget {
  const StepperButton({
    super.key,
    required this.icon,
    required this.onTap,
    this.filled = false,
    this.size = 40,
  });

  final IconData icon;
  final VoidCallback onTap;
  final bool filled;
  final double size;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(999),
          child: Container(
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: filled ? AppColors.headerText : AppColors.cardSurface,
              shape: BoxShape.circle,
              border: Border.all(color: AppColors.headerText.withValues(alpha: 0.35)),
            ),
            child: Icon(
              icon,
              size: 16,
              color: filled ? AppColors.cardSurface : AppColors.headerText,
            ),
          ),
        ),
      ),
    );
  }
}
