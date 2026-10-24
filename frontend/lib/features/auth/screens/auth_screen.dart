import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import 'package:medoracle/features/auth/widgets/auth_header.dart'; 
/// Unified Authentication Screen supporting seamless toggle between
/// "Sign In" and "Create Account" using local state.
class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  // Local state for toggling between Sign In and Sign Up
  bool _isLogin = true;

  // Controllers for Sign In
  final TextEditingController _loginIdentifierController = TextEditingController();
  final TextEditingController _loginPasswordController = TextEditingController();

  // Controllers for Sign Up
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _signUpEmailController = TextEditingController();
  final TextEditingController _signUpPasswordController = TextEditingController();

  // Password visibility & Terms states
  bool _showLoginPassword = false;
  bool _showSignUpPassword = false;
  bool _agreeToTerms = false;

  final _formKey = GlobalKey<FormState>();

  @override
  void dispose() {
    _loginIdentifierController.dispose();
    _loginPasswordController.dispose();
    _nameController.dispose();
    _signUpEmailController.dispose();
    _signUpPasswordController.dispose();
    super.dispose();
  }

  void _handleSubmit() {
    // Route forward to the dashboard via go_router
    context.go(RouteNames.dashboard);
  }

  void _toggleAuthMode(bool isLogin) {
    if (_isLogin != isLogin) {
      setState(() {
        _isLogin = isLogin;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.canvas,
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Top Main Header with consistent header color and comfortable padding
              AuthHeader(isLogin: _isLogin),

              // Comfortable vertical gap (24.0) between header and primary card
              const SizedBox(height: 24.0),

              // Form Card Container
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20.0),
                child: Container(
                  decoration: BoxDecoration(
                    color: AppColors.card,
                    borderRadius: BorderRadius.circular(12.0),
                    border: Border.all(color: AppColors.borderSubtle, width: 1.5),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.textPrimary.withValues(alpha: 0.04),
                        blurRadius: 16,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 24.0),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Segmented Mode Switcher (Sign In / Create Account)
                        _SegmentedSwitcher(
                          isLogin: _isLogin,
                          onTabSelected: _toggleAuthMode,
                        ),

                        const SizedBox(height: 24.0),

                        // Animated Switcher between Sign In and Sign Up Forms
                        AnimatedCrossFade(
                          firstChild: _LoginForm(
                            identifierController: _loginIdentifierController,
                            passwordController: _loginPasswordController,
                            showPassword: _showLoginPassword,
                            onTogglePassword: () {
                              setState(() {
                                _showLoginPassword = !_showLoginPassword;
                              });
                            },
                          ),
                          secondChild: _SignUpForm(
                            nameController: _nameController,
                            emailController: _signUpEmailController,
                            passwordController: _signUpPasswordController,
                            showPassword: _showSignUpPassword,
                            onTogglePassword: () {
                              setState(() {
                                _showSignUpPassword = !_showSignUpPassword;
                              });
                            },
                            agreeToTerms: _agreeToTerms,
                            onToggleTerms: (val) {
                              setState(() {
                                _agreeToTerms = val;
                              });
                            },
                          ),
                          crossFadeState: _isLogin
                              ? CrossFadeState.showFirst
                              : CrossFadeState.showSecond,
                          duration: const Duration(milliseconds: 250),
                        ),

                        const SizedBox(height: 24.0),

                        // Primary Action Button (Sign In / Create Account)
                        _PrimaryButton(
                          label: _isLogin ? 'Sign In' : 'Create Account',
                          onPressed: _handleSubmit,
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 24.0),

              // Footer Switcher & Disclaimers
              _AuthFooter(
                isLogin: _isLogin,
                onToggleMode: () => _toggleAuthMode(!_isLogin),
              ),

              const SizedBox(height: 32.0),
            ],
          ),
        ),
      ),
    );
  }
}

/// Top Main Header displaying Logo, Header Text color, and Instrument Serif title

/// Segmented Switcher for toggling "Sign In" and "Create Account"
class _SegmentedSwitcher extends StatelessWidget {
  final bool isLogin;
  final ValueChanged<bool> onTabSelected;

  const _SegmentedSwitcher({
    required this.isLogin,
    required this.onTabSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.lightNeutralFill,
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(color: AppColors.borderSubtle, width: 1),
      ),
      padding: const EdgeInsets.all(4),
      child: Row(
        children: [
          Expanded(
            child: _SegmentTab(
              title: 'Sign In',
              isSelected: isLogin,
              onTap: () => onTabSelected(true),
            ),
          ),
          const SizedBox(width: 6),
          Expanded(
            child: _SegmentTab(
              title: 'Create Account',
              isSelected: !isLogin,
              onTap: () => onTabSelected(false),
            ),
          ),
        ],
      ),
    );
  }
}

class _SegmentTab extends StatelessWidget {
  final String title;
  final bool isSelected;
  final VoidCallback onTap;

  const _SegmentTab({
    required this.title,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      behavior: HitTestBehavior.opaque,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        height: 40,
        decoration: BoxDecoration(
          color: isSelected ? AppColors.headerText : Colors.transparent,
          borderRadius: BorderRadius.circular(10.0),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: AppColors.headerText.withValues(alpha: 0.25),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ]
              : null,
        ),
        alignment: Alignment.center,
        child: Text(
          title,
          style: AppTextStyles.lexend(
            fontSize: 14.0,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
            color: isSelected ? Colors.white : AppColors.textSecondary,
          ),
        ),
      ),
    );
  }
}

/// Login Form View
class _LoginForm extends StatelessWidget {
  final TextEditingController identifierController;
  final TextEditingController passwordController;
  final bool showPassword;
  final VoidCallback onTogglePassword;

  const _LoginForm({
    required this.identifierController,
    required this.passwordController,
    required this.showPassword,
    required this.onTogglePassword,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _FormFieldLabel(label: 'Email or phone number'),
        const SizedBox(height: 8.0),
        _AuthTextField(
          controller: identifierController,
          hintText: 'name@example.com',
          prefixIcon: Icons.mail_outline_rounded,
          keyboardType: TextInputType.emailAddress,
        ),
        const SizedBox(height: 24.0),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const _FormFieldLabel(label: 'Password'),
            GestureDetector(
              onTap: () {
                // Future expansion: Forgot Password handler
              },
              child: Text(
                'Forgot password?',
                style: AppTextStyles.lexend(
                  fontSize: 13.0,
                  fontWeight: FontWeight.w600,
                  color: AppColors.headerText,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8.0),
        _AuthTextField(
          controller: passwordController,
          hintText: 'Enter your password',
          prefixIcon: Icons.lock_outline_rounded,
          obscureText: !showPassword,
          suffixIcon: IconButton(
            icon: Icon(
              showPassword
                  ? Icons.visibility_outlined
                  : Icons.visibility_off_outlined,
              color: AppColors.textSecondary,
              size: 20,
            ),
            onPressed: onTogglePassword,
          ),
        ),
      ],
    );
  }
}

/// Sign Up Form View
class _SignUpForm extends StatelessWidget {
  final TextEditingController nameController;
  final TextEditingController emailController;
  final TextEditingController passwordController;
  final bool showPassword;
  final VoidCallback onTogglePassword;
  final bool agreeToTerms;
  final ValueChanged<bool> onToggleTerms;

  const _SignUpForm({
    required this.nameController,
    required this.emailController,
    required this.passwordController,
    required this.showPassword,
    required this.onTogglePassword,
    required this.agreeToTerms,
    required this.onToggleTerms,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _FormFieldLabel(label: 'Full name'),
        const SizedBox(height: 8.0),
        _AuthTextField(
          controller: nameController,
          hintText: 'Your full name',
          prefixIcon: Icons.person_outline_rounded,
          keyboardType: TextInputType.name,
        ),
        const SizedBox(height: 24.0),
        const _FormFieldLabel(label: 'Email'),
        const SizedBox(height: 8.0),
        _AuthTextField(
          controller: emailController,
          hintText: 'name@example.com',
          prefixIcon: Icons.mail_outline_rounded,
          keyboardType: TextInputType.emailAddress,
        ),
        const SizedBox(height: 24.0),
        const _FormFieldLabel(label: 'Password'),
        const SizedBox(height: 8.0),
        _AuthTextField(
          controller: passwordController,
          hintText: 'Create a password',
          prefixIcon: Icons.lock_outline_rounded,
          obscureText: !showPassword,
          suffixIcon: IconButton(
            icon: Icon(
              showPassword
                  ? Icons.visibility_outlined
                  : Icons.visibility_off_outlined,
              color: AppColors.textSecondary,
              size: 20,
            ),
            onPressed: onTogglePassword,
          ),
        ),
        const SizedBox(height: 8.0),
        Text(
          'Use at least 8 characters, including a number.',
          style: AppTextStyles.lexend(
            fontSize: 12.0,
            fontWeight: FontWeight.w400,
            color: AppColors.textSecondary,
          ),
        ),
        const SizedBox(height: 24.0),
        // Terms of Service agreement checkbox
        GestureDetector(
          onTap: () => onToggleTerms(!agreeToTerms),
          behavior: HitTestBehavior.opaque,
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 22,
                height: 22,
                margin: const EdgeInsets.only(top: 2),
                decoration: BoxDecoration(
                  color: agreeToTerms ? AppColors.headerText : AppColors.card,
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(
                    color: agreeToTerms ? AppColors.headerText : AppColors.borderSubtle,
                    width: 1.5,
                  ),
                ),
                child: agreeToTerms
                    ? const Icon(
                        Icons.check,
                        size: 16,
                        color: Colors.white,
                      )
                    : null,
              ),
              const SizedBox(width: 10),
              Expanded(
                child: RichText(
                  text: TextSpan(
                    style: AppTextStyles.lexend(
                      fontSize: 13.0,
                      fontWeight: FontWeight.w400,
                      color: AppColors.textSecondary,
                      height: 1.4,
                    ),
                    children: [
                      const TextSpan(text: 'I agree to the '),
                      TextSpan(
                        text: 'Terms of Service',
                        style: AppTextStyles.lexend(
                          fontSize: 13.0,
                          fontWeight: FontWeight.w600,
                          color: AppColors.headerText,
                        ),
                      ),
                      const TextSpan(text: ' and '),
                      TextSpan(
                        text: 'Privacy Policy',
                        style: AppTextStyles.lexend(
                          fontSize: 13.0,
                          fontWeight: FontWeight.w600,
                          color: AppColors.headerText,
                        ),
                      ),
                      const TextSpan(text: '.'),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// Custom modular label widget using Lexend (14.0 labels/body per AGENTS.md)
class _FormFieldLabel extends StatelessWidget {
  final String label;

  const _FormFieldLabel({required this.label});

  @override
  Widget build(BuildContext context) {
    return Text(
      label,
      style: AppTextStyles.lexend(
        fontSize: 14.0,
        fontWeight: FontWeight.w600,
        color: AppColors.textPrimary,
      ),
    );
  }
}

/// Standard mobile single-container input field with AppColors.borderSubtle
/// and proper internal padding matching native iOS/Android inputs (no nested boxes).
class _AuthTextField extends StatelessWidget {
  final TextEditingController controller;
  final String hintText;
  final IconData prefixIcon;
  final bool obscureText;
  final Widget? suffixIcon;
  final TextInputType keyboardType;

  const _AuthTextField({
    required this.controller,
    required this.hintText,
    required this.prefixIcon,
    this.obscureText = false,
    this.suffixIcon,
    this.keyboardType = TextInputType.text,
  });

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      obscureText: obscureText,
      keyboardType: keyboardType,
      style: AppTextStyles.lexend(
        fontSize: 14.0,
        fontWeight: FontWeight.w500,
        color: AppColors.textPrimary,
      ),
      cursorColor: AppColors.cta,
      decoration: InputDecoration(
        filled: true,
        fillColor: AppColors.lightNeutralFill.withValues(alpha: 0.5),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 16.0),
        hintText: hintText,
        hintStyle: AppTextStyles.lexend(
          fontSize: 14.0,
          fontWeight: FontWeight.w400,
          color: AppColors.textSecondary,
        ),
        prefixIcon: Icon(
          prefixIcon,
          color: AppColors.textSecondary,
          size: 20,
        ),
        suffixIcon: suffixIcon,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12.0),
          borderSide: const BorderSide(color: AppColors.borderSubtle, width: 1.5),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12.0),
          borderSide: const BorderSide(color: AppColors.borderSubtle, width: 1.5),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12.0),
          borderSide: const BorderSide(color: AppColors.cta, width: 1.5),
        ),
      ),
    );
  }
}

/// Primary CTA Button (#E04E26) with fixed height 56.0 and radius 12.0
class _PrimaryButton extends StatelessWidget {
  final String label;
  final VoidCallback onPressed;

  const _PrimaryButton({
    required this.label,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 56.0,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.cta,
          foregroundColor: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12.0),
          ),
          shadowColor: AppColors.cta.withValues(alpha: 0.4),
        ),
        child: Text(
          label,
          style: AppTextStyles.lexend(
            fontSize: 16.0,
            fontWeight: FontWeight.w600,
            color: Colors.white,
            letterSpacing: 0.2,
          ),
        ),
      ),
    );
  }
}

/// Footer switch link and disclaimer
class _AuthFooter extends StatelessWidget {
  final bool isLogin;
  final VoidCallback onToggleMode;

  const _AuthFooter({
    required this.isLogin,
    required this.onToggleMode,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              isLogin ? 'New to MedOracle? ' : 'Already have an account? ',
              style: AppTextStyles.lexend(
                fontSize: 14.0,
                fontWeight: FontWeight.w400,
                color: AppColors.textSecondary,
              ),
            ),
            GestureDetector(
              onTap: onToggleMode,
              child: Text(
                isLogin ? 'Create an account' : 'Sign in',
                style: AppTextStyles.lexend(
                  fontSize: 14.0,
                  fontWeight: FontWeight.w700,
                  color: AppColors.headerText,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12.0),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32.0),
          child: Text(
            'By continuing, you agree to our Terms and Privacy Policy.',
            textAlign: TextAlign.center,
            style: AppTextStyles.lexend(
              fontSize: 12.0,
              fontWeight: FontWeight.w400,
              color: AppColors.textSecondary.withValues(alpha: 0.85),
              height: 1.4,
            ),
          ),
        ),
      ],
    );
  }
}
