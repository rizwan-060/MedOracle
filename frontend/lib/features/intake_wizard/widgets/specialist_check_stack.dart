import 'package:flutter/material.dart';
import 'package:medoracle/core/theme/app_colors.dart';
import 'package:medoracle/core/theme/app_text_styles.dart';
import 'package:medoracle/features/intake_wizard/models/assessment_data.dart';

/// Stack of "paper" cards holding the specialist checks.
///
/// The top card shows the selected check while the sheets peeking out from
/// behind it expose the next checks - tapping a sheet jumps straight to it.
class SpecialistCheckStack extends StatefulWidget {
  const SpecialistCheckStack({
    super.key,
    required this.checks,
    this.onIndexChanged,
  });

  /// The specialist checks, in reading order.
  final List<SpecialistCheck> checks;

  /// Notified whenever the visible check changes.
  final ValueChanged<int>? onIndexChanged;

  @override
  State<SpecialistCheckStack> createState() => _SpecialistCheckStackState();
}

class _SpecialistCheckStackState extends State<SpecialistCheckStack> {
  int _index = 0;

  void _select(int index) {
    if (index < 0 || index >= widget.checks.length || index == _index) {
      return;
    }
    setState(() => _index = index);
    widget.onIndexChanged?.call(index);
  }

  @override
  Widget build(BuildContext context) {
    final List<SpecialistCheck> checks = widget.checks;
    final SpecialistCheck? next =
        _index + 1 < checks.length ? checks[_index + 1] : null;
    final SpecialistCheck? afterNext =
        _index + 2 < checks.length ? checks[_index + 2] : null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        _CheckCard(check: checks[_index]),
        SizedBox(
          height: 108,
          child: ClipRect(
            child: Stack(
              children: <Widget>[
                if (afterNext != null)
                  Positioned(
                    left: 28,
                    right: 28,
                    top: 38,
                    child: _PeekSheet(
                      check: afterNext,
                      onTap: () => _select(_index + 2),
                    ),
                  ),
                if (next != null)
                  Positioned(
                    left: 14,
                    right: 14,
                    top: -16,
                    child: _PeekSheet(
                      check: next,
                      onTap: () => _select(_index + 1),
                    ),
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 8),
        _IndicatorDots(
          count: checks.length,
          activeIndex: _index,
          onSelected: _select,
        ),
      ],
    );
  }
}

/// The fully visible card of the stack.
class _CheckCard extends StatelessWidget {
  const _CheckCard({required this.check});

  final SpecialistCheck check;

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: const BoxConstraints(minHeight: 330),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: <Color>[AppColors.cardSurface, AppColors.canvasBackground],
        ),
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(color: AppColors.refCardRing),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: AppColors.refPlum.withValues(alpha: 0.14),
            blurRadius: 24,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Expanded(
                child: Text(check.title, style: AppTextStyles.sectionTitle),
              ),
              const SizedBox(width: 10),
              _ConfidencePill(badge: check.badge),
            ],
          ),
          const SizedBox(height: 12),
          Text(check.headline, style: AppTextStyles.cardHeadline),
          if (check.tags.isNotEmpty) ...<Widget>[
            const SizedBox(height: 12),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: <Widget>[
                for (final String tag in check.tags) _TagChip(label: tag),
              ],
            ),
          ],
          const SizedBox(height: 16),
          const Text(
            'FROM YOUR DETAILS',
            style: AppTextStyles.eyebrow,
          ),
          const SizedBox(height: 6),
          if (check.grid)
            _FactGrid(facts: check.facts)
          else
            _FactRow(facts: check.facts),
        ],
      ),
    );
  }
}

/// Confidence label rendered on the top right of a check card.
class _ConfidencePill extends StatelessWidget {
  const _ConfidencePill({required this.badge});

  final String badge;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      decoration: BoxDecoration(
        color: AppColors.canvasBackground,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.refCardRing, width: 1.5),
      ),
      child: Text(
        badge,
        style: AppTextStyles.chipLabel.copyWith(
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}

/// Short supporting phrase.
class _TagChip extends StatelessWidget {
  const _TagChip({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: AppColors.cardSurface,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Text(label, style: AppTextStyles.chipLabel),
    );
  }
}

/// Detail tiles laid out in a single row.
class _FactRow extends StatelessWidget {
  const _FactRow({required this.facts});

  final List<DetailFact> facts;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        for (int index = 0; index < facts.length; index++)
          Expanded(
            child: Padding(
              padding: EdgeInsets.only(
                right: index == facts.length - 1 ? 0 : 8,
              ),
              child: _FactTile(fact: facts[index]),
            ),
          ),
      ],
    );
  }
}

/// Detail tiles laid out in a two column grid.
class _FactGrid extends StatelessWidget {
  const _FactGrid({required this.facts});

  final List<DetailFact> facts;

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: facts.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        mainAxisSpacing: 8,
        crossAxisSpacing: 8,
        mainAxisExtent: 64,
      ),
      itemBuilder: (BuildContext context, int index) =>
          _FactTile(fact: facts[index]),
    );
  }
}

/// One labelled value tile.
class _FactTile extends StatelessWidget {
  const _FactTile({required this.fact});

  final DetailFact fact;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.canvasBackground,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          Text(fact.label, style: AppTextStyles.statLabel),
          Text(fact.value, style: AppTextStyles.statValue),
        ],
      ),
    );
  }
}

/// A sheet peeking out from behind the visible check.
class _PeekSheet extends StatelessWidget {
  const _PeekSheet({required this.check, required this.onTap});

  final SpecialistCheck check;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      type: MaterialType.transparency,
      child: InkWell(
        onTap: onTap,
        borderRadius: const BorderRadius.vertical(
          bottom: Radius.circular(14),
        ),
        child: Container(
          height: 70,
          padding: const EdgeInsets.fromLTRB(14, 22, 14, 8),
          decoration: BoxDecoration(
            color: AppColors.cardSurface,
            borderRadius: const BorderRadius.vertical(
              bottom: Radius.circular(14),
            ),
            border: Border.all(color: AppColors.borderSubtle),
            boxShadow: <BoxShadow>[
              BoxShadow(
                color: AppColors.refPlum.withValues(alpha: 0.10),
                blurRadius: 14,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Row(
            children: <Widget>[
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: <Widget>[
                    Text(
                      'Next check',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: AppTextStyles.statLabel,
                    ),
                    Text(
                      check.title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: AppTextStyles.chipLabel.copyWith(
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 10),
              Text(
                check.badge,
                style: AppTextStyles.chipLabel.copyWith(
                  color: AppColors.refSubtitle,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Pagination dots under the stack.
class _IndicatorDots extends StatelessWidget {
  const _IndicatorDots({
    required this.count,
    required this.activeIndex,
    required this.onSelected,
  });

  final int count;
  final int activeIndex;
  final ValueChanged<int> onSelected;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        for (int index = 0; index < count; index++)
          SizedBox(
            width: 30,
            height: 44,
            child: Material(
              type: MaterialType.transparency,
              child: InkWell(
                onTap: () => onSelected(index),
                borderRadius: BorderRadius.circular(999),
                child: Center(
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 180),
                    width: 10,
                    height: 10,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: index == activeIndex
                          ? AppColors.refPlum
                          : AppColors.cardSurface.withValues(alpha: 0.00),
                      border: Border.all(
                        color: index == activeIndex
                            ? AppColors.refPlum
                            : AppColors.dustyTaupe,
                        width: 2,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}
