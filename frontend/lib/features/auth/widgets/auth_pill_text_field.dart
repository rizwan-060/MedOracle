import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// Single-container pill input from the authentication references.
///
/// The 56px field is one bordered surface (no nested boxes) with a slate icon,
/// an optional password visibility toggle and inline required-field errors.
class AuthPillTextField extends StatelessWidget {
  const AuthPillTextField({
    super.key,
    required this.controller,
    required this.hintText,
    required this.icon,
    this.obscureText = false,
    this.onToggleVisibility,
    this.validator,
    this.keyboardType = TextInputType.text,
    this.textInputAction = TextInputAction.next,
    this.autofillHints,
    this.focusNode,
    this.onFieldSubmitted,
  });

  final TextEditingController controller;
  final String hintText;
  final IconData icon;
  final bool obscureText;
  final VoidCallback? onToggleVisibility;
  final String? Function(String?)? validator;
  final TextInputType keyboardType;
  final TextInputAction textInputAction;
  final Iterable<String>? autofillHints;
  final FocusNode? focusNode;
  final ValueChanged<String>? onFieldSubmitted;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(28),
        boxShadow: const <BoxShadow>[
          BoxShadow(
            color: AppColors.authFieldShadow,
            offset: Offset(0, 10),
            blurRadius: 22,
            spreadRadius: -12,
          ),
          BoxShadow(
            color: AppColors.authFieldShadowSoft,
            offset: Offset(0, 1),
            blurRadius: 3,
          ),
        ],
      ),
      child: TextFormField(
        controller: controller,
        focusNode: focusNode,
        obscureText: obscureText,
        keyboardType: keyboardType,
        textInputAction: textInputAction,
        autofillHints: autofillHints,
        onFieldSubmitted: onFieldSubmitted,
        validator: validator,
        autovalidateMode: AutovalidateMode.onUserInteraction,
        textAlignVertical: TextAlignVertical.center,
        style: AppTextStyles.authFieldValue(),
        cursorColor: AppColors.headerText,
        decoration: InputDecoration(
          filled: true,
          fillColor: AppColors.authInputSurface,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 17,
          ),
          constraints: const BoxConstraints(minHeight: 56),
          hintText: hintText,
          hintStyle: AppTextStyles.authFieldHint(),
          errorStyle: AppTextStyles.authError(),
          prefixIcon: Icon(icon, size: 20, color: AppColors.headerText),
          prefixIconConstraints: const BoxConstraints(
            minWidth: 48,
            minHeight: 48,
          ),
          suffixIcon: onToggleVisibility == null
              ? null
              : IconButton(
                  onPressed: onToggleVisibility,
                  tooltip: obscureText ? 'Show password' : 'Hide password',
                  iconSize: 20,
                  color: AppColors.headerText,
                  icon: Icon(
                    obscureText
                        ? Icons.visibility_off_outlined
                        : Icons.visibility_outlined,
                  ),
                ),
          suffixIconConstraints: const BoxConstraints(
            minWidth: 48,
            minHeight: 48,
          ),
          border: _border(AppColors.authSlateRing),
          enabledBorder: _border(AppColors.authSlateRing),
          focusedBorder: _border(AppColors.headerText, width: 2),
          errorBorder: _border(AppColors.primaryAccent),
          focusedErrorBorder: _border(AppColors.primaryAccent, width: 2),
        ),
      ),
    );
  }

  static OutlineInputBorder _border(Color color, {double width = 1}) {
    return OutlineInputBorder(
      borderRadius: BorderRadius.circular(28),
      borderSide: BorderSide(color: color, width: width),
    );
  }
}
