import 'dart:async';

import 'package:material_ui/material_ui.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../navigation/onboarding_navigation.dart';
import '../widgets/onboarding_illustrations.dart';
import '../widgets/onboarding_progress.dart';
import '../widgets/onboarding_shell.dart';
import '../widgets/onboarding_type.dart';

/// Onboarding 1 — Welcome.
///
/// The reference shows three stacked feature cards with an automatic 4.5s
/// carousel, tappable dots and horizontal swipe support.
class OnboardingWelcomeScreen extends StatefulWidget {
  const OnboardingWelcomeScreen({super.key});

  static const String routePath = RouteNames.onboardingWelcome;

  @override
  State<OnboardingWelcomeScreen> createState() => _OnboardingWelcomeScreenState();
}

class _OnboardingWelcomeScreenState extends State<OnboardingWelcomeScreen> {
  int _card = 0;
  Timer? _timer;

  static const List<_Feature> _features = <_Feature>[
    _Feature(
      title: 'Data & Report',
      subtitle: 'Your health, in one clear report',
      body: 'Answer simple questions about your body, habits and health history. '
          'We turn them into a complete report that explains your heart health '
          'in plain words.',
      chips: <String>['About 5 minutes', 'Lab values optional'],
      illustration: ReportIllustration(),
    ),
    _Feature(
      title: 'AI Team Consensus',
      subtitle: 'Five AI doctors review your case',
      body: 'Five expert AI doctor agents study your answers and debate them. '
          'You see where they agree, where they differ, and exactly why.',
      chips: <String>['Full debate shown', 'Reasons in plain words'],
      illustration: ConsensusIllustration(),
    ),
    _Feature(
      title: 'Future & Lifestyle Simulator',
      subtitle: 'See how small habits change your future',
      body: 'Try changes like walking more or quitting smoking, and watch your '
          'future heart-health path move before you commit to anything.',
      chips: <String>['Try what-if changes', 'Stays on your device'],
      illustration: TrajectoryIllustration(),
    ),
  ];

  @override
  void initState() {
    super.initState();
    _startTimer();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _startTimer() {
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(milliseconds: 4500), (_) {
      if (mounted) {
        setState(() => _card = (_card + 1) % _features.length);
      }
    });
  }

  void _select(int index) {
    setState(() => _card = index % _features.length);
    _startTimer();
  }

  void _handleSwipe(DragEndDetails details) {
    final double velocity = details.primaryVelocity ?? 0;
    if (velocity.abs() < 200) return;
    final int next = velocity < 0
        ? (_card + 1) % _features.length
        : (_card + _features.length - 1) % _features.length;
    _select(next);
  }

  @override
  Widget build(BuildContext context) {
    return OnboardingShell(
      step: 1,
      title: 'Welcome to MedOracle',
      subtitle: 'Prevention is far better than diagnosis.',
      ctaLabel: 'Get started',
      onCta: () => OnboardingNavigation.next(
        context,
        RouteNames.onboardingCareTeam,
      ),
      child: LayoutBuilder(
        builder: (BuildContext context, BoxConstraints constraints) {
          return SingleChildScrollView(
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: <Widget>[
                    GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onHorizontalDragEnd: _handleSwipe,
                      child: AnimatedSwitcher(
                        duration: const Duration(milliseconds: 700),
                        child: _FeatureCard(
                          key: ValueKey<int>(_card),
                          feature: _features[_card],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    OnboardingDots(index: _card, onTap: _select),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

class _Feature {
  const _Feature({
    required this.title,
    required this.subtitle,
    required this.body,
    required this.chips,
    required this.illustration,
  });

  final String title;
  final String subtitle;
  final String body;
  final List<String> chips;
  final Widget illustration;
}

class _FeatureCard extends StatelessWidget {
  const _FeatureCard({super.key, required this.feature});

  final _Feature feature;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 404,
      width: double.infinity,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          feature.illustration,
          const SizedBox(height: 16),
          Text(
            feature.title,
            style: OnboardingType.serif(
              23,
              FontWeight.w600,
              AppColors.textPrimary,
              height: 28 / 23,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            feature.subtitle,
            style: OnboardingType.sans(
              15,
              FontWeight.w500,
              AppColors.headerText,
              height: 22 / 15,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            feature.body,
            style: OnboardingType.sans(
              14,
              FontWeight.w300,
              AppColors.textPrimary.withValues(alpha: 0.82),
              height: 22 / 14,
            ),
          ),
          const Spacer(),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: feature.chips
                .map((String label) => _FeatureChip(label: label))
                .toList(),
          ),
        ],
      ),
    );
  }
}

class _FeatureChip extends StatelessWidget {
  const _FeatureChip({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.onboardingPeachSurface,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppColors.onboardingPeachBorder, width: 1.5),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Icon(
            Icons.check_rounded,
            size: 13,
            color: AppColors.mutedGreen,
          ),
          const SizedBox(width: 5),
          Text(
            label,
            style: OnboardingType.sans(
              12,
              FontWeight.w500,
              AppColors.textPrimary,
            ),
          ),
        ],
      ),
    );
  }
}
