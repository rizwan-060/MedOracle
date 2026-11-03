import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../widgets/auth_footer_prompt.dart';
import '../widgets/auth_hero_header.dart';
import '../widgets/auth_page_shell.dart';
import '../widgets/auth_pill_text_field.dart';
import '../widgets/auth_primary_button.dart';
import '../widgets/auth_social_row.dart';

/// Login screen matching `designs-refs/Login.dc.html`.
///
/// Required fields only: email and password. Submitting navigates to the
/// dashboard, exactly like the previous unified auth screen.
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final FocusNode _emailFocus = FocusNode();
  final FocusNode _passwordFocus = FocusNode();

  bool _showPassword = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _emailFocus.dispose();
    _passwordFocus.dispose();
    super.dispose();
  }

  String? _required(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Required';
    }
    return null;
  }

  void _submit() {
    FocusScope.of(context).unfocus();
    if (_formKey.currentState?.validate() ?? false) {
      context.go(RouteNames.dashboard);
    }
  }

  void _comingSoon(String feature) {
    FocusScope.of(context).unfocus();
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text('$feature is coming soon.')));
  }

  @override
  Widget build(BuildContext context) {
    return AuthPageShell(
      header: const AuthHeroHeader(title: 'Hello!', subtitle: 'Welcome back'),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            AuthPillTextField(
              controller: _emailController,
              focusNode: _emailFocus,
              hintText: 'name@example.com',
              icon: Icons.mail_outline_rounded,
              keyboardType: TextInputType.emailAddress,
              textInputAction: TextInputAction.next,
              autofillHints: const <String>[
                AutofillHints.username,
                AutofillHints.email,
              ],
              validator: _required,
              onFieldSubmitted: (_) => _passwordFocus.requestFocus(),
            ),
            const SizedBox(height: 20),
            AuthPillTextField(
              controller: _passwordController,
              focusNode: _passwordFocus,
              hintText: 'Enter password',
              icon: Icons.lock_outline_rounded,
              obscureText: !_showPassword,
              onToggleVisibility: () {
                setState(() {
                  _showPassword = !_showPassword;
                });
              },
              textInputAction: TextInputAction.done,
              autofillHints: const <String>[AutofillHints.password],
              validator: _required,
              onFieldSubmitted: (_) => _submit(),
            ),
            const SizedBox(height: 12),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () => _comingSoon('Password reset'),
                style: TextButton.styleFrom(
                  foregroundColor: AppColors.headerText,
                  minimumSize: const Size(0, 36),
                  padding: EdgeInsets.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                child: Text(
                  'Forgot Password?',
                  style: AppTextStyles.authForgot(),
                ),
              ),
            ),
            const SizedBox(height: 16),
            AuthPrimaryButton(label: 'Log In', onPressed: _submit),
            const SizedBox(height: 32),
            AuthSocialRow(
              onGoogle: () => _comingSoon('Google sign-in'),
              onApple: () => _comingSoon('Apple sign-in'),
            ),
            const SizedBox(height: 32),
            AuthFooterPrompt(
              prompt: 'New to MedOracle? ',
              actionLabel: 'Sign Up',
              onAction: () => context.push(RouteNames.signup),
            ),
          ],
        ),
      ),
    );
  }
}
