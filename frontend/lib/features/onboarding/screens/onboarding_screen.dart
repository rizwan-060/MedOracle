import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/route_names.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// Comprehensive 3-slide MedOracle Onboarding Screen.
///
/// Encapsulates the entire onboarding experience in a single cohesive file:
/// - Slide 1: Welcome & Early Signals with animated ECG heartbeat over human silhouette.
/// - Slide 2: Multi-Agent Clinical Perspectives network with radiating interconnected nodes.
/// - Slide 3: Health Trajectory progression chart & interactive lifestyle scenario simulator.
///
/// Followed by seamless navigation to Auth (Login/Signup).
class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen>
    with TickerProviderStateMixin {
  late final PageController _pageController;
  int _currentPage = 0;

  // Animation controller for the rhythmic heartbeat on Slide 1
  late final AnimationController _heartbeatController;
  late final Animation<double> _heartPulseAnimation;
  late final Animation<double> _rippleAnimation;

  // Animation controller for the continuous scan along the ECG line
  late final AnimationController _ecgScanController;

  // Interactive state for Slide 3
  int _selectedTrajectoryHorizon = 1; // 0: 30 Days, 1: 6 Months, 2: 1 Year
  double _lifestyleSliderValue = 0.72; // "Most days"

  @override
  void initState() {
    super.initState();
    _pageController = PageController();

    // Natural cardiac heartbeat rhythm: dual systole pulse + rest pause
    _heartbeatController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1600),
    )..repeat();

    _heartPulseAnimation = TweenSequence<double>([
      TweenSequenceItem(
        tween: Tween<double>(begin: 1.0, end: 1.18)
            .chain(CurveTween(curve: Curves.easeOutCubic)),
        weight: 15,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: 1.18, end: 1.02)
            .chain(CurveTween(curve: Curves.easeInOut)),
        weight: 12,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: 1.02, end: 1.14)
            .chain(CurveTween(curve: Curves.easeOutCubic)),
        weight: 15,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: 1.14, end: 1.0)
            .chain(CurveTween(curve: Curves.easeInOutCubic)),
        weight: 18,
      ),
      TweenSequenceItem(
        tween: ConstantTween<double>(1.0),
        weight: 40,
      ),
    ]).animate(_heartbeatController);

    _rippleAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _heartbeatController,
        curve: const Interval(0.0, 0.65, curve: Curves.easeOut),
      ),
    );

    // Continuous sweep across ECG waveform
    _ecgScanController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2200),
    )..repeat();
  }

  @override
  void dispose() {
    _pageController.dispose();
    _heartbeatController.dispose();
    _ecgScanController.dispose();
    super.dispose();
  }

  void _onNext() {
    if (_currentPage < 2) {
      _pageController.animateToPage(
        _currentPage + 1,
        duration: const Duration(milliseconds: 450),
        curve: Curves.easeInOutCubic,
      );
    } else {
      _finishOnboarding();
    }
  }

  void _onBack() {
    if (_currentPage > 0) {
      _pageController.animateToPage(
        _currentPage - 1,
        duration: const Duration(milliseconds: 450),
        curve: Curves.easeInOutCubic,
      );
    }
  }

  void _finishOnboarding() {
    context.go(RouteNames.auth);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.canvasBackground,
      body: Stack(
        children: [
          // Ambient soft warm aura (Top-Left)
          Positioned(
            top: -120,
            left: -100,
            child: IgnorePointer(
              child: Container(
                width: 380,
                height: 380,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      AppColors.onboardingAuraTopLeft,
                      Colors.transparent,
                    ],
                  ),
                ),
              ),
            ),
          ),

          // Ambient soft peach aura (Bottom-Right)
          Positioned(
            bottom: -80,
            right: -80,
            child: IgnorePointer(
              child: Container(
                width: 360,
                height: 360,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      AppColors.onboardingAuraBottomRight,
                      Colors.transparent,
                    ],
                  ),
                ),
              ),
            ),
          ),

          // Main Content
          SafeArea(
            child: Column(
              children: [
                // Top Navigation Bar
                _buildTopBar(),

                // Page Carousel
                Expanded(
                  child: PageView(
                    controller: _pageController,
                    onPageChanged: (int page) {
                      setState(() {
                        _currentPage = page;
                      });
                    },
                    children: [
                      _buildSlide1(),
                      _buildSlide2(),
                      _buildSlide3(),
                    ],
                  ),
                ),

                // Bottom Controls (Dots + Next/Back Buttons)
                _buildBottomControls(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ===========================================================================
  // Top Navigation Bar
  // ===========================================================================
  Widget _buildTopBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 12.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Logo & App Wordmark
          Row(
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: AppColors.onboardingMaroon,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.onboardingMaroon.withValues(alpha: 0.25),
                      blurRadius: 10,
                      offset: const Offset(0, 3),
                    ),
                  ],
                ),
                child: Center(
                  child: CustomPaint(
                    size: const Size(20, 12),
                    painter: _MiniPulsePainter(color: Colors.white),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Text(
                'MedOracle',
                style: AppTextStyles.lexend(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: AppColors.onboardingTitle,
                  letterSpacing: -0.3,
                ),
              ),
            ],
          ),

          // Skip Button
          Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: _finishOnboarding,
              borderRadius: BorderRadius.circular(20),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
                decoration: BoxDecoration(
                  color: AppColors.onboardingCardSurface,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: AppColors.onboardingSkipBorder,
                    width: 1.2,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.03),
                      blurRadius: 6,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Text(
                  'Skip',
                  style: AppTextStyles.lexend(
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                    color: AppColors.onboardingSkipText,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ===========================================================================
  // Slide 1: Welcome & Early Signals
  // ===========================================================================
  Widget _buildSlide1() {
    return LayoutBuilder(
      builder: (context, constraints) {
        return SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          physics: const BouncingScrollPhysics(),
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top Hero Visual (Silhouette + Heartbeat + Badges)
                Center(
                  child: Padding(
                    padding: const EdgeInsets.only(top: 8.0, bottom: 20.0),
                    child: SizedBox(
                      width: 320,
                      height: 300,
                      child: Stack(
                        clipBehavior: Clip.none,
                        alignment: Alignment.center,
                        children: [
                          // Base Silhouette Card
                          Container(
                            width: 250,
                            height: 270,
                            decoration: BoxDecoration(
                              color: AppColors.onboardingCardSurface,
                              borderRadius: BorderRadius.circular(32),
                              border: Border.all(
                                color: AppColors.onboardingCardBorder,
                                width: 1.5,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withValues(alpha: 0.04),
                                  blurRadius: 24,
                                  offset: const Offset(0, 10),
                                ),
                              ],
                            ),
                            child: Stack(
                              alignment: Alignment.center,
                              children: [
                                // Human Silhouette Drawing
                                CustomPaint(
                                  size: const Size(200, 240),
                                  painter: _HumanSilhouettePainter(),
                                ),

                                // Cardiac pulse radial wave animation
                                AnimatedBuilder(
                                  animation: _heartbeatController,
                                  builder: (context, child) {
                                    final progress = _rippleAnimation.value;
                                    return Positioned(
                                      top: 140,
                                      child: Container(
                                        width: 20 + (progress * 60),
                                        height: 20 + (progress * 60),
                                        decoration: BoxDecoration(
                                          shape: BoxShape.circle,
                                          border: Border.all(
                                            color: AppColors.onboardingMaroon
                                                .withValues(
                                                    alpha: (1.0 - progress) * 0.4),
                                            width: 1.8,
                                          ),
                                        ),
                                      ),
                                    );
                                  },
                                ),

                                // Heartbeat pulse line across chest
                                Positioned(
                                  top: 135,
                                  left: 12,
                                  right: 12,
                                  child: AnimatedBuilder(
                                    animation: _ecgScanController,
                                    builder: (context, child) {
                                      return ScaleTransition(
                                        scale: _heartPulseAnimation,
                                        alignment: Alignment.center,
                                        child: CustomPaint(
                                          size: const Size(226, 44),
                                          painter: _HeartbeatEcgPainter(
                                            scanProgress:
                                                _ecgScanController.value,
                                          ),
                                        ),
                                      );
                                    },
                                  ),
                                ),
                              ],
                            ),
                          ),

                          // Floating Badge 1: Early signals (Top-Left)
                          Positioned(
                            top: 28,
                            left: 0,
                            child: _buildFloatingBadge(
                              icon: Icons.favorite_border_rounded,
                              label: 'Early signals',
                            ),
                          ),

                          // Floating Badge 2: Clear insights (Center-Right)
                          Positioned(
                            top: 130,
                            right: 0,
                            child: _buildFloatingBadge(
                              icon: Icons.science_outlined,
                              label: 'Clear insights',
                            ),
                          ),

                          // Floating Badge 3: Private by design (Bottom-Left)
                          Positioned(
                            bottom: 12,
                            left: 20,
                            child: _buildFloatingBadge(
                              icon: Icons.shield_outlined,
                              label: 'Private by design',
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),

                // Text Content
                Padding(
                  padding: const EdgeInsets.only(bottom: 24.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'WELCOME',
                        style: AppTextStyles.lexend(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: AppColors.onboardingOverline,
                          letterSpacing: 1.5,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        'Understand Your\nHealth, Earlier',
                        style: AppTextStyles.lexend(
                          fontSize: 30,
                          fontWeight: FontWeight.w700,
                          color: AppColors.onboardingTitle,
                          letterSpacing: -0.6,
                          height: 1.2,
                        ),
                      ),
                      const SizedBox(height: 14),
                      Text(
                        'Bring your symptoms, history and lab results together, and turn scattered health information into insights you can actually understand.',
                        style: AppTextStyles.lexend(
                          fontSize: 14.5,
                          fontWeight: FontWeight.w400,
                          color: AppColors.onboardingBody,
                          height: 1.5,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  // ===========================================================================
  // Slide 2: Multi-Agent Clinical Perspectives Network
  // ===========================================================================
  Widget _buildSlide2() {
    return LayoutBuilder(
      builder: (context, constraints) {
        return SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          physics: const BouncingScrollPhysics(),
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top Hero Visual (Multi-Agent Connected Network Diagram)
                Center(
                  child: Padding(
                    padding: const EdgeInsets.only(top: 8.0, bottom: 20.0),
                    child: SizedBox(
                      width: 320,
                      height: 310,
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          // Network Connection Lines
                          Positioned.fill(
                            child: CustomPaint(
                              painter: _NetworkLinesPainter(),
                            ),
                          ),

                          // Top-Left Node: Symptom Analysis
                          Positioned(
                            top: 10,
                            left: 0,
                            child: _buildPerspectiveNode(
                              icon: Icons.show_chart_rounded,
                              title: 'Symptom\nAnalysis',
                              subtitle: 'What you feel',
                            ),
                          ),

                          // Top-Right Node: Medical History
                          Positioned(
                            top: 10,
                            right: 0,
                            child: _buildPerspectiveNode(
                              icon: Icons.description_outlined,
                              title: 'Medical\nHistory',
                              subtitle: "Where you've\nbeen",
                            ),
                          ),

                          // Bottom-Left Node: Lab Analysis
                          Positioned(
                            bottom: 12,
                            left: 0,
                            child: _buildPerspectiveNode(
                              icon: Icons.science_outlined,
                              title: 'Lab Analysis',
                              subtitle: 'What tests show',
                            ),
                          ),

                          // Bottom-Right Node: Risk Prediction
                          Positioned(
                            bottom: 12,
                            right: 0,
                            child: _buildPerspectiveNode(
                              icon: Icons.trending_up_rounded,
                              title: 'Risk Prediction',
                              subtitle: 'What to watch',
                            ),
                          ),

                          // Center Hub: Health Assessment
                          Container(
                            width: 140,
                            padding: const EdgeInsets.symmetric(
                                horizontal: 12, vertical: 16),
                            decoration: BoxDecoration(
                              color: AppColors.onboardingCardSurface,
                              borderRadius: BorderRadius.circular(24),
                              border: Border.all(
                                color: AppColors.onboardingCardBorder,
                                width: 1.6,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withValues(alpha: 0.08),
                                  blurRadius: 20,
                                  offset: const Offset(0, 8),
                                ),
                              ],
                            ),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Container(
                                  width: 44,
                                  height: 44,
                                  decoration: BoxDecoration(
                                    color: AppColors.onboardingMaroon,
                                    shape: BoxShape.circle,
                                    boxShadow: [
                                      BoxShadow(
                                        color: AppColors.onboardingMaroon
                                            .withValues(alpha: 0.35),
                                        blurRadius: 10,
                                        offset: const Offset(0, 4),
                                      ),
                                    ],
                                  ),
                                  child: const Icon(
                                    Icons.add_rounded,
                                    color: Colors.white,
                                    size: 26,
                                  ),
                                ),
                                const SizedBox(height: 10),
                                Text(
                                  'Health\nAssessment',
                                  textAlign: TextAlign.center,
                                  style: AppTextStyles.lexend(
                                    fontSize: 13,
                                    fontWeight: FontWeight.w700,
                                    color: AppColors.onboardingTitle,
                                    height: 1.25,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'One explained view',
                                  textAlign: TextAlign.center,
                                  style: AppTextStyles.lexend(
                                    fontSize: 10.5,
                                    fontWeight: FontWeight.w400,
                                    color: AppColors.onboardingBody,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),

                // Text Content
                Padding(
                  padding: const EdgeInsets.only(bottom: 24.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'A COMPLETE PICTURE',
                        style: AppTextStyles.lexend(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: AppColors.onboardingOverline,
                          letterSpacing: 1.5,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        'Many Perspectives.\nOne Clear View.',
                        style: AppTextStyles.lexend(
                          fontSize: 30,
                          fontWeight: FontWeight.w700,
                          color: AppColors.onboardingTitle,
                          letterSpacing: -0.6,
                          height: 1.2,
                        ),
                      ),
                      const SizedBox(height: 14),
                      Text(
                        'Four focused analyses review your information side by side, then come together in a single assessment that explains its reasoning.',
                        style: AppTextStyles.lexend(
                          fontSize: 14.5,
                          fontWeight: FontWeight.w400,
                          color: AppColors.onboardingBody,
                          height: 1.5,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  // ===========================================================================
  // Slide 3: Trajectory & Lifestyle Scenario Simulation
  // ===========================================================================
  Widget _buildSlide3() {
    return LayoutBuilder(
      builder: (context, constraints) {
        return SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          physics: const BouncingScrollPhysics(),
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top Hero Visual (Health Trajectory Card + Lifestyle Scenario Card)
                Padding(
                  padding: const EdgeInsets.only(top: 8.0, bottom: 16.0),
                  child: Column(
                    children: [
                      // Card 1: Health Trajectory Card
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: AppColors.onboardingCardSurface,
                          borderRadius: BorderRadius.circular(24),
                          border: Border.all(
                            color: AppColors.onboardingCardBorder,
                            width: 1.5,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.04),
                              blurRadius: 16,
                              offset: const Offset(0, 6),
                            ),
                          ],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Header Row: Title + "ILLUSTRATIVE" Badge
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  'Health Trajectory',
                                  style: AppTextStyles.lexend(
                                    fontSize: 14,
                                    fontWeight: FontWeight.w700,
                                    color: AppColors.onboardingTitle,
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: AppColors.onboardingBadgeFill,
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text(
                                    'ILLUSTRATIVE',
                                    style: AppTextStyles.lexend(
                                      fontSize: 9.5,
                                      fontWeight: FontWeight.w700,
                                      color: AppColors.onboardingMaroon,
                                      letterSpacing: 0.8,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),

                            // Segmented Horizon Tabs
                            Container(
                              padding: const EdgeInsets.all(3),
                              decoration: BoxDecoration(
                                color: const Color(0xFFF1F5F9),
                                borderRadius: BorderRadius.circular(14),
                              ),
                              child: Row(
                                children: [
                                  _buildTrajectoryTab(0, '30 Days'),
                                  _buildTrajectoryTab(1, '6 Months'),
                                  _buildTrajectoryTab(2, '1 Year'),
                                ],
                              ),
                            ),
                            const SizedBox(height: 16),

                            // Trajectory Line Chart
                            SizedBox(
                              height: 64,
                              width: double.infinity,
                              child: CustomPaint(
                                painter: _TrajectoryChartPainter(
                                  progressFactor: _selectedTrajectoryHorizon == 0
                                      ? 0.5
                                      : (_selectedTrajectoryHorizon == 1
                                          ? 0.75
                                          : 1.0),
                                ),
                              ),
                            ),
                            const SizedBox(height: 8),

                            // Chart Legend
                            Row(
                              mainAxisAlignment: MainAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    CustomPaint(
                                      size: const Size(16, 2),
                                      painter: _DashedLinePainter(
                                        color: AppColors.onboardingInactiveLine,
                                      ),
                                    ),
                                    const SizedBox(width: 6),
                                    Text(
                                      'Current path',
                                      style: AppTextStyles.lexend(
                                        fontSize: 10.5,
                                        fontWeight: FontWeight.w500,
                                        color: AppColors.onboardingBody,
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(width: 18),
                                Row(
                                  children: [
                                    Container(
                                      width: 14,
                                      height: 2.2,
                                      decoration: BoxDecoration(
                                        color: AppColors.onboardingEcgLine,
                                        borderRadius: BorderRadius.circular(2),
                                      ),
                                    ),
                                    const SizedBox(width: 6),
                                    Text(
                                      'With your change',
                                      style: AppTextStyles.lexend(
                                        fontSize: 10.5,
                                        fontWeight: FontWeight.w500,
                                        color: AppColors.onboardingBody,
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 12),

                      // Card 2: Lifestyle Scenario Card
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 14),
                        decoration: BoxDecoration(
                          color: AppColors.onboardingCardSurface,
                          borderRadius: BorderRadius.circular(22),
                          border: Border.all(
                            color: AppColors.onboardingCardBorder,
                            width: 1.5,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.04),
                              blurRadius: 14,
                              offset: const Offset(0, 5),
                            ),
                          ],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Container(
                                  width: 36,
                                  height: 36,
                                  decoration: const BoxDecoration(
                                    color: AppColors.onboardingBadgeFill,
                                    shape: BoxShape.circle,
                                  ),
                                  child: const Icon(
                                    Icons.directions_walk_rounded,
                                    color: AppColors.onboardingMaroon,
                                    size: 20,
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'LIFESTYLE SCENARIO',
                                        style: AppTextStyles.lexend(
                                          fontSize: 9.5,
                                          fontWeight: FontWeight.w600,
                                          color: AppColors.onboardingBody,
                                          letterSpacing: 0.8,
                                        ),
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        '"What if I walked daily?"',
                                        style: AppTextStyles.lexend(
                                          fontSize: 13,
                                          fontWeight: FontWeight.w700,
                                          color: AppColors.onboardingTitle,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                Text(
                                  _lifestyleSliderValue > 0.6
                                      ? 'Most days'
                                      : (_lifestyleSliderValue > 0.3
                                          ? 'Few days'
                                          : 'Rarely'),
                                  style: AppTextStyles.lexend(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                    color: AppColors.onboardingMaroon,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),

                            // Interactive Scenario Slider
                            SliderTheme(
                              data: SliderThemeData(
                                trackHeight: 6,
                                activeTrackColor: AppColors.onboardingSliderActive,
                                inactiveTrackColor:
                                    AppColors.onboardingSliderInactive,
                                thumbColor: Colors.white,
                                overlayColor: AppColors.onboardingMaroon
                                    .withValues(alpha: 0.15),
                                thumbShape: const _CustomSliderThumbShape(
                                  enabledThumbRadius: 11,
                                  borderColor: AppColors.onboardingMaroon,
                                  borderWidth: 3,
                                ),
                                trackShape: const RoundedRectSliderTrackShape(),
                              ),
                              child: Slider(
                                value: _lifestyleSliderValue,
                                onChanged: (value) {
                                  setState(() {
                                    _lifestyleSliderValue = value;
                                  });
                                },
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                // Text Content & Medical Disclaimer
                Padding(
                  padding: const EdgeInsets.only(bottom: 24.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'LOOK AHEAD',
                        style: AppTextStyles.lexend(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: AppColors.onboardingOverline,
                          letterSpacing: 1.5,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        'Explore What Your\nChoices Could Change',
                        style: AppTextStyles.lexend(
                          fontSize: 30,
                          fontWeight: FontWeight.w700,
                          color: AppColors.onboardingTitle,
                          letterSpacing: -0.6,
                          height: 1.2,
                        ),
                      ),
                      const SizedBox(height: 14),
                      Text(
                        'See how your health may trend over time, and try simple lifestyle changes to explore how that path could shift.',
                        style: AppTextStyles.lexend(
                          fontSize: 14.5,
                          fontWeight: FontWeight.w400,
                          color: AppColors.onboardingBody,
                          height: 1.5,
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Medical disclaimer row
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Padding(
                            padding: EdgeInsets.only(top: 2.0),
                            child: Icon(
                              Icons.info_outline,
                              size: 14,
                              color: AppColors.onboardingInactiveLine,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Health projections are estimates for exploration only. They are not a diagnosis and do not replace advice from a qualified medical professional.',
                              style: AppTextStyles.lexend(
                                fontSize: 11,
                                fontWeight: FontWeight.w400,
                                color: AppColors.onboardingBody,
                                height: 1.4,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  // ===========================================================================
  // Bottom Controls (Animated Dots + Responsive CTA / Back)
  // ===========================================================================
  Widget _buildBottomControls() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 0, 24, 20),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Animated Pagination Dots
          Row(
            children: List.generate(3, (index) {
              final bool isActive = _currentPage == index;
              return AnimatedContainer(
                duration: const Duration(milliseconds: 350),
                curve: Curves.easeOutCubic,
                margin: const EdgeInsets.only(right: 6.0),
                width: isActive ? 26.0 : 6.0,
                height: 6.0,
                decoration: BoxDecoration(
                  color: isActive
                      ? AppColors.onboardingDotActive
                      : AppColors.onboardingDotInactive,
                  borderRadius: BorderRadius.circular(3.0),
                ),
              );
            }),
          ),

          // Action Buttons: Back + Next/Get Started
          Row(
            children: [
              // Back Button (shown on Slide 1 & 2)
              if (_currentPage > 0) ...[
                Material(
                  color: Colors.transparent,
                  child: InkWell(
                    onTap: _onBack,
                    borderRadius: BorderRadius.circular(26),
                    child: Container(
                      width: 52,
                      height: 52,
                      decoration: BoxDecoration(
                        color: AppColors.onboardingCardSurface,
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: AppColors.onboardingSkipBorder,
                          width: 1.2,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.04),
                            blurRadius: 10,
                            offset: const Offset(0, 3),
                          ),
                        ],
                      ),
                      child: const Center(
                        child: Icon(
                          Icons.chevron_left_rounded,
                          color: AppColors.onboardingTitle,
                          size: 24,
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
              ],

              // Next / Get Started Primary Button
              ElevatedButton(
                onPressed: _onNext,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.onboardingMaroon,
                  foregroundColor: Colors.white,
                  elevation: 0,
                  shadowColor:
                      AppColors.onboardingMaroon.withValues(alpha: 0.35),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(26),
                  ),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 26,
                    vertical: 16,
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      _currentPage == 2 ? 'Get Started' : 'Next',
                      style: AppTextStyles.lexend(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                        letterSpacing: 0.2,
                      ),
                    ),
                    const SizedBox(width: 6),
                    const Icon(
                      Icons.chevron_right_rounded,
                      size: 20,
                      color: Colors.white,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ===========================================================================
  // Helper Widgets
  // ===========================================================================

  Widget _buildFloatingBadge({
    required IconData icon,
    required String label,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.onboardingCardSurface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: AppColors.onboardingCardBorder,
          width: 1.2,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 14,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 28,
            height: 28,
            decoration: const BoxDecoration(
              color: AppColors.onboardingBadgeFill,
              shape: BoxShape.circle,
            ),
            child: Icon(
              icon,
              color: AppColors.onboardingMaroon,
              size: 16,
            ),
          ),
          const SizedBox(width: 10),
          Text(
            label,
            style: AppTextStyles.lexend(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: AppColors.onboardingTitle,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPerspectiveNode({
    required IconData icon,
    required String title,
    required String subtitle,
  }) {
    return Container(
      width: 142,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      decoration: BoxDecoration(
        color: AppColors.onboardingCardSurface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: AppColors.onboardingCardBorder,
          width: 1.4,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: const BoxDecoration(
              color: AppColors.onboardingBadgeFill,
              shape: BoxShape.circle,
            ),
            child: Icon(
              icon,
              color: AppColors.onboardingMaroon,
              size: 17,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTextStyles.lexend(
                    fontSize: 11.5,
                    fontWeight: FontWeight.w700,
                    color: AppColors.onboardingTitle,
                    height: 1.2,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  subtitle,
                  style: AppTextStyles.lexend(
                    fontSize: 10,
                    fontWeight: FontWeight.w400,
                    color: AppColors.onboardingBody,
                    height: 1.2,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTrajectoryTab(int index, String label) {
    final bool isSelected = _selectedTrajectoryHorizon == index;
    return Expanded(
      child: GestureDetector(
        onTap: () {
          setState(() {
            _selectedTrajectoryHorizon = index;
          });
        },
        behavior: HitTestBehavior.opaque,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 250),
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: isSelected
                ? AppColors.onboardingCardSurface
                : Colors.transparent,
            borderRadius: BorderRadius.circular(11),
            boxShadow: isSelected
                ? [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.06),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ]
                : null,
          ),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: AppTextStyles.lexend(
              fontSize: 12,
              fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
              color: isSelected
                  ? AppColors.onboardingMaroon
                  : AppColors.onboardingBody,
            ),
          ),
        ),
      ),
    );
  }
}

// =============================================================================
// Custom Painters & Shapes
// =============================================================================

/// Mini pulse painter for the MedOracle top brand logo
class _MiniPulsePainter extends CustomPainter {
  final Color color;

  const _MiniPulsePainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final path = Path();
    final h = size.height;
    final w = size.width;

    path.moveTo(0, h * 0.5);
    path.lineTo(w * 0.28, h * 0.5);
    path.lineTo(w * 0.42, h * 0.05);
    path.lineTo(w * 0.60, h * 0.95);
    path.lineTo(w * 0.74, h * 0.5);
    path.lineTo(w, h * 0.5);

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant _MiniPulsePainter oldDelegate) =>
      oldDelegate.color != color;
}

/// Stylized human silhouette painter matching Slide 1
class _HumanSilhouettePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    // Torso Fill Paint (soft blush gradient)
    final torsoPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          AppColors.onboardingSilhouette.withValues(alpha: 0.95),
          AppColors.onboardingSilhouette.withValues(alpha: 0.45),
        ],
      ).createShader(Rect.fromLTWH(0, 0, w, h))
      ..style = PaintingStyle.fill;

    // Torso Stroke Paint
    final strokePaint = Paint()
      ..color = AppColors.onboardingSilhouetteStroke
      ..strokeWidth = 1.4
      ..style = PaintingStyle.stroke;

    // Head Fill Paint
    final headPaint = Paint()
      ..color = AppColors.onboardingSilhouette
      ..style = PaintingStyle.fill;

    // Head Dot Paint
    final dotPaint = Paint()
      ..color = AppColors.onboardingMaroon.withValues(alpha: 0.65)
      ..style = PaintingStyle.fill;

    // 1. Head circle with central dot
    final headCenter = Offset(w * 0.5, h * 0.26);
    final headRadius = w * 0.17;
    canvas.drawCircle(headCenter, headRadius, headPaint);
    canvas.drawCircle(headCenter, headRadius, strokePaint);
    canvas.drawCircle(headCenter, 4.0, dotPaint);

    // 2. Torso shape
    final torsoPath = Path();
    torsoPath.moveTo(w * 0.16, h * 0.95);
    torsoPath.cubicTo(
      w * 0.16,
      h * 0.62,
      w * 0.28,
      h * 0.45,
      w * 0.5,
      h * 0.45,
    );
    torsoPath.cubicTo(
      w * 0.72,
      h * 0.45,
      w * 0.84,
      h * 0.62,
      w * 0.84,
      h * 0.95,
    );
    torsoPath.close();

    canvas.drawPath(torsoPath, torsoPaint);
    canvas.drawPath(torsoPath, strokePaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

/// Animated Heartbeat ECG line across chest
class _HeartbeatEcgPainter extends CustomPainter {
  final double scanProgress;

  const _HeartbeatEcgPainter({required this.scanProgress});

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    final dashedPaint = Paint()
      ..color = AppColors.onboardingMaroon
      ..strokeWidth = 2.2
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final path = Path();
    path.moveTo(0, h * 0.6);
    path.lineTo(w * 0.24, h * 0.6);

    // P-wave
    path.lineTo(w * 0.28, h * 0.5);
    path.lineTo(w * 0.33, h * 0.6);

    // QRS complex
    path.lineTo(w * 0.38, h * 0.75);
    path.lineTo(w * 0.46, h * 0.05); // High Systolic Peak
    path.lineTo(w * 0.54, h * 0.95); // Deep S deflection
    path.lineTo(w * 0.61, h * 0.6);

    // T-wave
    path.lineTo(w * 0.68, h * 0.45);
    path.lineTo(w * 0.74, h * 0.6);

    // Baseline continue
    path.lineTo(w, h * 0.6);

    // Draw dashed effect along path
    final metrics = path.computeMetrics().toList();
    if (metrics.isNotEmpty) {
      final metric = metrics.first;
      double distance = 0.0;
      const dashLength = 7.0;
      const dashSpace = 4.5;

      while (distance < metric.length) {
        final currentDash = math.min(dashLength, metric.length - distance);
        final extractPath = metric.extractPath(distance, distance + currentDash);
        canvas.drawPath(extractPath, dashedPaint);
        distance += dashLength + dashSpace;
      }
    }

    // Glowing travelling pulse beam
    final glowPaint = Paint()
      ..color = AppColors.onboardingMaroon.withValues(alpha: 0.6)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 6);

    final sweepX = w * scanProgress;
    canvas.drawCircle(Offset(sweepX, h * 0.6), 5.0, glowPaint);
  }

  @override
  bool shouldRepaint(covariant _HeartbeatEcgPainter oldDelegate) =>
      oldDelegate.scanProgress != scanProgress;
}

/// Dotted radiating lines between center card and four outer nodes in Slide 2
class _NetworkLinesPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    final linePaint = Paint()
      ..color = const Color(0xFFE8D5D0)
      ..strokeWidth = 1.4
      ..style = PaintingStyle.stroke;

    final center = Offset(w * 0.5, h * 0.5);

    // Four corner targets
    final targets = [
      Offset(w * 0.24, h * 0.22), // Top-Left
      Offset(w * 0.76, h * 0.22), // Top-Right
      Offset(w * 0.24, h * 0.78), // Bottom-Left
      Offset(w * 0.76, h * 0.78), // Bottom-Right
    ];

    for (final target in targets) {
      _drawDashedLine(canvas, center, target, linePaint);
    }
  }

  void _drawDashedLine(
      Canvas canvas, Offset p1, Offset p2, Paint paint) {
    final distance = (p2 - p1).distance;
    final normalized = (p2 - p1) / distance;
    const dashLength = 4.0;
    const dashSpace = 4.0;

    double current = 25.0; // Margin from center card
    while (current < distance - 20) {
      final start = p1 + normalized * current;
      final end = p1 + normalized * (current + dashLength);
      canvas.drawLine(start, end, paint);
      current += dashLength + dashSpace;
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

/// Trajectory comparison line chart with smooth curves and gradient fill
class _TrajectoryChartPainter extends CustomPainter {
  final double progressFactor;

  const _TrajectoryChartPainter({required this.progressFactor});

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    // Horizontal grid lines
    final gridPaint = Paint()
      ..color = const Color(0xFFF1F5F9)
      ..strokeWidth = 1.0;
    canvas.drawLine(Offset(0, h * 0.2), Offset(w, h * 0.2), gridPaint);
    canvas.drawLine(Offset(0, h * 0.6), Offset(w, h * 0.6), gridPaint);

    // 1. Dotted "Current path" line
    final currentPath = Path();
    currentPath.moveTo(0, h * 0.82);
    currentPath.quadraticBezierTo(w * 0.5, h * 0.78, w, h * 0.72);

    final dashedPaint = Paint()
      ..color = AppColors.onboardingInactiveLine
      ..strokeWidth = 1.8
      ..style = PaintingStyle.stroke;

    final metrics = currentPath.computeMetrics().toList();
    if (metrics.isNotEmpty) {
      final metric = metrics.first;
      double distance = 0.0;
      const dashLength = 5.0;
      const dashSpace = 3.5;
      while (distance < metric.length) {
        final currentDash = math.min(dashLength, metric.length - distance);
        final extract = metric.extractPath(distance, distance + currentDash);
        canvas.drawPath(extract, dashedPaint);
        distance += dashLength + dashSpace;
      }
    }

    // 2. Solid upward "With your change" line + Gradient Fill
    final changePath = Path();
    changePath.moveTo(0, h * 0.82);
    changePath.quadraticBezierTo(
      w * 0.45,
      h * 0.70,
      w,
      h * (0.82 - (0.48 * progressFactor)),
    );

    // Fill underneath the change curve
    final fillPath = Path.from(changePath)
      ..lineTo(w, h)
      ..lineTo(0, h)
      ..close();

    final fillPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          AppColors.onboardingMaroon.withValues(alpha: 0.16),
          AppColors.onboardingMaroon.withValues(alpha: 0.01),
        ],
      ).createShader(Rect.fromLTWH(0, 0, w, h))
      ..style = PaintingStyle.fill;

    canvas.drawPath(fillPath, fillPaint);

    final changeLinePaint = Paint()
      ..color = AppColors.onboardingEcgLine
      ..strokeWidth = 2.4
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    canvas.drawPath(changePath, changeLinePaint);
  }

  @override
  bool shouldRepaint(covariant _TrajectoryChartPainter oldDelegate) =>
      oldDelegate.progressFactor != progressFactor;
}

/// Dashed line painter for chart legends
class _DashedLinePainter extends CustomPainter {
  final Color color;

  const _DashedLinePainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 1.8
      ..style = PaintingStyle.stroke;

    canvas.drawLine(const Offset(0, 1), const Offset(5, 1), paint);
    canvas.drawLine(const Offset(8, 1), const Offset(13, 1), paint);
  }

  @override
  bool shouldRepaint(covariant _DashedLinePainter oldDelegate) =>
      oldDelegate.color != color;
}

/// Custom slider thumb with white center and crisp maroon outer border
class _CustomSliderThumbShape extends SliderComponentShape {
  final double enabledThumbRadius;
  final Color borderColor;
  final double borderWidth;

  const _CustomSliderThumbShape({
    this.enabledThumbRadius = 10.0,
    required this.borderColor,
    this.borderWidth = 3.0,
  });

  @override
  Size getPreferredSize(bool isEnabled, bool isDiscrete) =>
      Size.fromRadius(enabledThumbRadius);

  @override
  void paint(
    PaintingContext context,
    Offset center, {
    required Animation<double> activationAnimation,
    required Animation<double> enableAnimation,
    required bool isDiscrete,
    required TextPainter labelPainter,
    required RenderBox parentBox,
    required SliderThemeData sliderTheme,
    required TextDirection textDirection,
    required double value,
    required double textScaleFactor,
    required Size sizeWithOverflow,
  }) {
    final canvas = context.canvas;

    // Drop shadow
    final shadowPaint = Paint()
      ..color = Colors.black.withValues(alpha: 0.18)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4);
    canvas.drawCircle(center + const Offset(0, 2), enabledThumbRadius, shadowPaint);

    // Inner White Fill
    final fillPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, enabledThumbRadius, fillPaint);

    // Outer Maroon Border
    final borderPaint = Paint()
      ..color = borderColor
      ..strokeWidth = borderWidth
      ..style = PaintingStyle.stroke;
    canvas.drawCircle(center, enabledThumbRadius, borderPaint);
  }
}
