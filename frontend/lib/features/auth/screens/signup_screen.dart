import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_text_styles.dart';
import '../widgets/auth_hero_header.dart';
import '../widgets/auth_page_shell.dart';
import '../widgets/auth_pill_text_field.dart';
import '../widgets/auth_primary_button.dart';

/// Sign Up screen matching `designs-refs/SignUp.dc.html`.
///
/// Required fields only: email, password and confirmation. Submitting
/// navigates to the dashboard, exactly like the previous unified auth screen.
class SignUpScreen extends StatefulWidget {
  const SignUpScreen({super.key});

  @override
  State<SignUpScreen> createState() => _SignUpScreenState();
}

class _SignUpScreenState extends State<SignUpScreen> {
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _confirmPasswordController =
      TextEditingController();
  final FocusNode _emailFocus = FocusNode();
  final FocusNode _passwordFocus = FocusNode();
  final FocusNode _confirmPasswordFocus = FocusNode();

  bool _showPassword = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _emailFocus.dispose();
    _passwordFocus.dispose();
    _confirmPasswordFocus.dispose();
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

  void _backToLogin() {
    if (context.canPop()) {
      context.pop();
    } else {
      context.go(RouteNames.login);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AuthPageShell(
      header: AuthHeroHeader(
        title: 'Sign Up',
        subtitle: 'Create your account',
        onBack: _backToLogin,
      ),
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
              autofillHints: const <String>[AutofillHints.email],
              validator: _required,
              onFieldSubmitted: (_) => _passwordFocus.requestFocus(),
            ),
            const SizedBox(height: 20),
            AuthPillTextField(
              controller: _passwordController,
              focusNode: _passwordFocus,
              hintText: 'Create password',
              icon: Icons.lock_outline_rounded,
              obscureText: !_showPassword,
              onToggleVisibility: () {
                setState(() {
                  _showPassword = !_showPassword;
                });
              },
              autofillHints: const <String>[AutofillHints.newPassword],
              validator: _required,
              onFieldSubmitted: (_) => _confirmPasswordFocus.requestFocus(),
            ),
            const SizedBox(height: 20),
            AuthPillTextField(
              controller: _confirmPasswordController,
              focusNode: _confirmPasswordFocus,
              hintText: 'Confirm password',
              icon: Icons.lock_outline_rounded,
              obscureText: !_showPassword,
              onToggleVisibility: () {
                setState(() {
                  _showPassword = !_showPassword;
                });
              },
              textInputAction: TextInputAction.done,
              autofillHints: const <String>[AutofillHints.newPassword],
              validator: _required,
              onFieldSubmitted: (_) => _submit(),
            ),
            const SizedBox(height: 24),
            AuthPrimaryButton(label: 'Sign Up', onPressed: _submit),
            const SizedBox(height: 32),
            Text.rich(
              TextSpan(
                style: AppTextStyles.authTerms(),
                children: <InlineSpan>[
                  const TextSpan(text: 'By signing up, you agree to our '),
                  TextSpan(
                    text: 'Terms',
                    style: AppTextStyles.authTermsStrong(),
                  ),
                  const TextSpan(text: ' and '),
                  TextSpan(
                    text: 'Privacy Policy',
                    style: AppTextStyles.authTermsStrong(),
                  ),
                  const TextSpan(text: '.'),
                ],
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
