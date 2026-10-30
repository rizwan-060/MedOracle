import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Stacked report papers (design: v8 Step 6A card 2).
///
/// A deck of two translucent papers sits behind the front glass report; the
/// middle paper peeks out at the bottom with a "Next report" strip, and a
/// pill-style dot indicator marks the position in the deck.
class StackedReportsCard extends StatelessWidget {
  const StackedReportsCard({
    super.key,
    this.positionLabel = '1 of 2',
    this.nextReportName = 'Type 2 diabetes',
    this.nextReportRisk = 'High risk',
  });

  final String positionLabel;
  final String nextReportName;
  final String nextReportRisk;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(color: AppColors.borderSubtle, width: 1.5),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.textPrimary.withValues(alpha: 0.22),
          ),
          BoxShadow(
            color: AppColors.textPrimary.withValues(alpha: 0.06),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              const Expanded(
                child: Text(
                  'Below are estimates based on the details you entered',
                  style: TextStyle(
                    fontSize: 17,
                    height: 23 / 17,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textPrimary,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              _CountPill(label: positionLabel),
            ],
          ),
          const SizedBox(height: 6),
          const Text(
            'Tap the paper behind to read the next report.',
            style: TextStyle(
              fontSize: 13,
              height: 18 / 13,
              fontWeight: FontWeight.w500,
              color: AppColors.textMuted,
            ),
          ),
          const SizedBox(height: 16),
          _PaperStack(
            nextReportName: nextReportName,
            nextReportRisk: nextReportRisk,
          ),
          const SizedBox(height: 4),
          const Center(child: _DeckDots()),
        ],
      ),
    );
  }
}

class _CountPill extends StatelessWidget {
  const _CountPill({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 3),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Text(
        label,
        style: const TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.w800,
          color: AppColors.primaryMaroon,
        ),
      ),
    );
  }
}

class _PaperStack extends StatelessWidget {
  const _PaperStack({
    required this.nextReportName,
    required this.nextReportRisk,
  });

  final String nextReportName;
  final String nextReportRisk;

  @override
  Widget build(BuildContext context) {
    // The front paper reserves 52px at the bottom so the middle paper's
    // "Next report" strip can peek out beneath it.
    return Stack(
      clipBehavior: Clip.none,
      children: <Widget>[
        Positioned(
          left: 15,
          right: 15,
          top: 24,
          bottom: 8,
          child: Transform.rotate(
            angle: -1.1 * 3.141592 / 180,
            child: const _BlankPaper(
              colorAlpha: 0.30,
              shadowAlpha: 0.12,
            ),
          ),
        ),
        Positioned(
          left: 8,
          right: 8,
          top: 14,
          bottom: 24,
          child: Transform.rotate(
            angle: 0.9 * 3.141592 / 180,
            child: _PeekPaper(
              nextReportName: nextReportName,
              nextReportRisk: nextReportRisk,
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.only(bottom: 52),
          child: const _FrontReport(),
        ),
      ],
    );
  }
}

class _BlankPaper extends StatelessWidget {
  const _BlankPaper({required this.colorAlpha, required this.shadowAlpha});

  final double colorAlpha;
  final double shadowAlpha;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.cardSurface.withValues(alpha: colorAlpha),
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(
          color: AppColors.primaryMaroon.withValues(alpha: 0.16),
        ),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.primaryMaroon.withValues(alpha: shadowAlpha),
            blurRadius: 14,
            offset: const Offset(0, 6),
          ),
        ],
      ),
    );
  }
}

class _PeekPaper extends StatelessWidget {
  const _PeekPaper({
    required this.nextReportName,
    required this.nextReportRisk,
  });

  final String nextReportName;
  final String nextReportRisk;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.cardSurface.withValues(alpha: 0.46),
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(
          color: AppColors.primaryMaroon.withValues(alpha: 0.18),
        ),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.primaryMaroon.withValues(alpha: 0.16),
            blurRadius: 18,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      alignment: Alignment.bottomCenter,
      child: Container(
        height: 28,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: <Widget>[
            Flexible(
              child: Text(
                'Next report',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: AppColors.primaryMaroon.withValues(alpha: 0.75),
                ),
              ),
            ),
            const SizedBox(width: 6),
            Flexible(
              child: Text(
                nextReportName,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w800,
                  color: AppColors.textPrimary,
                ),
              ),
            ),
            const SizedBox(width: 6),
            Text(
              nextReportRisk,
              maxLines: 1,
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: AppColors.primaryMaroon,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _FrontReport extends StatelessWidget {
  const _FrontReport();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 14),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(
          color: AppColors.primaryMaroon.withValues(alpha: 0.22),
        ),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.primaryMaroon.withValues(alpha: 0.20),
            blurRadius: 24,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              const Expanded(
                child: Text(
                  'Heart attack or stroke',
                  style: TextStyle(
                    fontSize: 17,
                    height: 24 / 17,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textPrimary,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 2),
                decoration: BoxDecoration(
                  color: AppColors.amberSurface,
                  borderRadius: BorderRadius.circular(999),
                  border: Border.all(color: AppColors.amberWarning),
                ),
                child: const Text(
                  'High risk',
                  style: TextStyle(
                    fontSize: 12,
                    height: 18 / 12,
                    fontWeight: FontWeight.w800,
                    color: AppColors.primaryMaroon,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          // Wraps instead of overflowing: value first, caption beside it.
          Wrap(
            spacing: 8,
            runSpacing: 4,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: <Widget>[
              const Text(
                'About 24 in 100',
                style: TextStyle(
                  fontSize: 26,
                  height: 32 / 26,
                  fontWeight: FontWeight.w800,
                  color: AppColors.textPrimary,
                ),
              ),
              const Text(
                'people like you, within 10 years',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textMuted,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text.rich(
            TextSpan(
              children: <TextSpan>[
                const TextSpan(
                  text: 'Based on: ',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textPrimary,
                  ),
                ),
                const TextSpan(
                  text: 'age 54, blood pressure 146, cholesterol 242, '
                      'HDL 37, smoker',
                  style: TextStyle(
                    fontSize: 13,
                    height: 19 / 13,
                    fontWeight: FontWeight.w500,
                    color: AppColors.textPrimary,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.only(left: 14, top: 6, bottom: 6),
            decoration: const BoxDecoration(
              border: Border(
                left: BorderSide(color: AppColors.dustyTaupe, width: 3),
              ),
              borderRadius: BorderRadius.horizontal(
                right: Radius.circular(12),
              ),
              gradient: LinearGradient(
                begin: Alignment.centerLeft,
                end: Alignment.centerRight,
                colors: <Color>[
                  AppColors.dustyTaupe,
                  AppColors.dustyTaupe,
                ],
                stops: <double>[0.0, 0.85],
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const <Widget>[
                Text(
                  'Calculated from your numbers',
                  style: TextStyle(
                    fontSize: 11,
                    height: 15 / 11,
                    letterSpacing: 0.99,
                    fontWeight: FontWeight.w800,
                    color: AppColors.primaryMaroon,
                  ),
                ),
                SizedBox(height: 2),
                Text(
                  'Framingham 10-Year General CVD',
                  style: TextStyle(
                    fontSize: 14,
                    height: 19 / 14,
                    fontWeight: FontWeight.w700,
                    color: AppColors.primaryMaroon,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _DeckDots extends StatelessWidget {
  const _DeckDots();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        Container(
          width: 22,
          height: 7,
          decoration: const BoxDecoration(
            color: AppColors.primaryMaroon,
            borderRadius: BorderRadius.all(Radius.circular(4)),
          ),
        ),
        const SizedBox(width: 6),
        Container(
          width: 7,
          height: 7,
          decoration: BoxDecoration(
            color: AppColors.textPrimary.withValues(alpha: 0.30),
            borderRadius: BorderRadius.circular(4),
          ),
        ),
      ],
    );
  }
}
