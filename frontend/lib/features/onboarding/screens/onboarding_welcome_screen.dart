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
/// Three fixed cards are stacked on top of each other. Only one is interactive
/// and fully visible; the other two fade, slide and scale out of the way.
class OnboardingWelcomeScreen extends StatefulWidget {
  const OnboardingWelcomeScreen({super.key});

  static const String routePath = RouteNames.onboardingWelcome;

  @override
  State<OnboardingWelcomeScreen> createState() => _OnboardingWelcomeScreenState();
}

class _OnboardingWelcomeScreenState extends State<OnboardingWelcomeScreen> {
  static const Duration _cardDuration = Duration(milliseconds: 700);
  static const Duration _autoAdvanceDelay = Duration(milliseconds: 4500);
  static const double _cardHeight = 404;
  static const double _hiddenSlidePixels = 18;

  static const List<_WelcomeCardData> _cards = <_WelcomeCardData>[
    _WelcomeCardData(
      title: 'Data & Report',
      subtitle: 'Your health, in one clear report',
      body: 'Answer simple questions about your body, habits and health history. '
          'We turn them into a complete report that explains your heart health '
          'in plain words.',
      pills: <String>['About 5 minutes', 'Lab values optional'],
      painter: ReportIllustrationPainter(),
    ),
    _WelcomeCardData(
      title: 'AI Team Consensus',
      subtitle: 'Five AI doctors review your case',
      body: 'Five expert AI doctor agents study your answers and debate them. '
          'You see where they agree, where they differ, and exactly why.',
      pills: <String>['Full debate shown', 'Reasons in plain words'],
      painter: ConsensusIllustrationPainter(),
    ),
    _WelcomeCardData(
      title: 'Future & Lifestyle Simulator',
      subtitle: 'See how small habits change your future',
      body: 'Try changes like walking more or quitting smoking, and watch your '
          'future heart-health path move before you commit to anything.',
      pills: <String>['Try what-if changes', 'Stays on your device'],
      painter: TrajectoryIllustrationPainter(),
    ),
  ];

  int _current = 0;
  Timer? _timer;
  double? _pointerDownDx;

  @override
  void initState() {
    super.initState();
    _restartTimer();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _restartTimer() {
    _timer?.cancel();
    _timer = Timer(_autoAdvanceDelay, () {
      if (!mounted) return;
      setState(() => _current = (_current + 1) % _cards.length);
      _restartTimer();
    });
  }

  void _goTo(int index) {
    setState(() => _current = index % _cards.length);
    _restartTimer();
  }

  void _next() => _goTo(_current + 1);

  void _previous() => _goTo(_current + _cards.length - 1);

  void _onPointerDown(PointerDownEvent event) {
    _pointerDownDx = event.localPosition.dx;
  }

  void _onPointerUp(PointerUpEvent event) {
    final double? downDx = _pointerDownDx;
    _pointerDownDx = null;
    if (downDx == null) return;

    final double deltaX = event.localPosition.dx - downDx;
    if (deltaX > 40) {
      _previous();
    } else {
      _next();
    }
  }

  @override
  Widget build(BuildContext context) {
    return OnboardingShell(
      step: 1,
      title: 'Welcome to MedOracle',
      subtitle: 'Prevention is far better than diagnosis.',
      ctaLabel: 'Get started',
      // The reference shows a back affordance with no destination.
      onBack: () {},
      onCta: () => OnboardingNavigation.next(
        context,
        RouteNames.onboardingCareTeam,
      ),
      child: Padding(
        // OnboardingShell supplies the shared 20px horizontal padding.
        padding: const EdgeInsets.only(top: 16),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: <Widget>[
              Listener(
                behavior: HitTestBehavior.opaque,
                onPointerDown: _onPointerDown,
                onPointerUp: _onPointerUp,
                onPointerCancel: (_) => _pointerDownDx = null,
                child: SizedBox(
                  width: double.infinity,
                  height: _cardHeight,
                  child: Stack(
                    children: <Widget>[
                      for (int index = 0; index < _cards.length; index++)
                        _stackedCard(index),
                    ],
                  ),
                ),
              ),
              OnboardingDots(index: _current, onTap: _goTo),
            ],
          ),
        ),
      ),
    );
  }

  Widget _stackedCard(int index) {
    final bool visible = index == _current;

    return Positioned.fill(
      child: IgnorePointer(
        ignoring: !visible,
        child: AnimatedOpacity(
          opacity: visible ? 1 : 0,
          duration: _cardDuration,
          curve: Curves.ease,
          child: AnimatedSlide(
            offset: visible
                ? Offset.zero
                : Offset(0, _hiddenSlidePixels / _cardHeight),
            duration: _cardDuration,
            curve: Curves.ease,
            child: AnimatedScale(
              scale: visible ? 1 : 0.98,
              duration: _cardDuration,
              curve: Curves.ease,
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                child: _WelcomeCard(data: _cards[index]),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _WelcomeCardData {
  const _WelcomeCardData({
    required this.title,
    required this.subtitle,
    required this.body,
    required this.pills,
    required this.painter,
  });

  final String title;
  final String subtitle;
  final String body;
  final List<String> pills;
  final CustomPainter painter;
}

class _WelcomeCard extends StatelessWidget {
  const _WelcomeCard({required this.data});

  final _WelcomeCardData data;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        WelcomeIllustration(painter: data.painter),
        const SizedBox(height: 16),
        Text(
          data.title,
          style: OnboardingType.serif(
            23,
            FontWeight.w600,
            AppColors.deepInk,
            height: 28 / 23,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          data.subtitle,
          style: OnboardingType.sans(
            15,
            FontWeight.w500,
            AppColors.headerText,
            height: 22 / 15,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          data.body,
          style: OnboardingType.sans(
            14.5,
            FontWeight.w300,
            AppColors.deepInk.withValues(alpha: 0.8),
            height: 22 / 14.5,
          ),
        ),
        const SizedBox(height: 16),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: data.pills
              .map((String label) => _Pill(label: label))
              .toList(),
        ),
      ],
    );
  }
}

class _Pill extends StatelessWidget {
  const _Pill({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.onboardingPeachSurface,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(
          color: AppColors.onboardingPeachBorder,
          width: 1.5,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          const CustomPaint(
            painter: PillCheckPainter(),
            size: Size(14, 14),
          ),
          const SizedBox(width: 6),
          Text(
            label,
            style: OnboardingType.sans(
              12.5,
              FontWeight.w500,
              AppColors.deepInk,
            ),
          ),
        ],
      ),
    );
  }
}
