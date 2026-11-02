import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

/// Greedy chip field used for free-text lists (conditions, allergies, tags).
///
/// Renders existing values as removable chips with an inline "add" affordance,
/// matching the `+ Add Condition` rows of the design reference.
class TagChipsField extends StatelessWidget {
  const TagChipsField({
    super.key,
    required this.label,
    required this.tags,
    required this.onAdd,
    required this.onRemove,
    this.emptyLabel,
  });

  /// Field label shown above the chips.
  final String label;

  /// Current chip values.
  final List<String> tags;

  /// Called with free text entered by the user.
  final ValueChanged<String> onAdd;

  /// Called when the user taps the remove affordance on a chip.
  final ValueChanged<String> onRemove;

  /// Label of the "add" pill; defaults to `+ Add <label>`.
  final String? emptyLabel;

  @override
  Widget build(BuildContext context) {
    final String addLabel = emptyLabel ?? '+ Add $label';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        if (tags.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: <Widget>[
                for (final String tag in tags)
                  _RemovableChip(
                    label: tag,
                    onRemove: () => onRemove(tag),
                  ),
              ],
            ),
          ),
        _AddChipButton(
          label: addLabel,
          onSubmit: onAdd,
        ),
      ],
    );
  }
}

class _RemovableChip extends StatelessWidget {
  const _RemovableChip({required this.label, required this.onRemove});

  final String label;
  final VoidCallback onRemove;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 34,
      padding: const EdgeInsets.only(left: 12, right: 6),
      decoration: BoxDecoration(
        color: AppColors.refMint,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.mutedGreen.withValues(alpha: 0.35)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Text(label, style: AppTextStyles.fieldValue.copyWith(fontSize: 13)),
          const SizedBox(width: 4),
          InkWell(
            onTap: onRemove,
            borderRadius: BorderRadius.circular(999),
            child: const SizedBox(
              width: 22,
              height: 22,
              child: Icon(Icons.close, size: 14, color: AppColors.refInk),
            ),
          ),
        ],
      ),
    );
  }
}

class _AddChipButton extends StatelessWidget {
  const _AddChipButton({required this.label, required this.onSubmit});

  final String label;
  final ValueChanged<String> onSubmit;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: InkWell(
        borderRadius: BorderRadius.circular(999),
        onTap: () => _prompt(context),
        child: Container(
          height: 34,
          padding: const EdgeInsets.symmetric(horizontal: 14),
          decoration: BoxDecoration(
            color: AppColors.cardSurface,
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: AppColors.refFieldBorder),
          ),
          child: Center(
            child: Text(
              label,
              style: AppTextStyles.fieldValue.copyWith(fontSize: 13),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _prompt(BuildContext context) async {
    final TextEditingController controller = TextEditingController();
    final String? value = await showDialog<String>(
      context: context,
      builder: (BuildContext context) => AlertDialog(
        title: Text(label.replaceFirst('+ Add ', 'Add ')),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: const InputDecoration(hintText: 'Type a value'),
          onSubmitted: (String text) => Navigator.of(context).pop(text),
        ),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(controller.text),
            child: const Text('Add'),
          ),
        ],
      ),
    );
    controller.dispose();
    final String trimmed = value?.trim() ?? '';
    if (trimmed.isNotEmpty) {
      onSubmit(trimmed);
    }
  }
}
