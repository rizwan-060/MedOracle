# MedOracle Frontend Architecture

This codebase implements the MedOracle multi-agent disease forecasting mobile application using **Flutter (Dart)**, **flutter_riverpod** for state management, and **go_router** for navigation.

Strict adherence to [`AGENTS.md`](../../AGENTS.md) is enforced across all screens, widgets, design tokens, and typography.

---

## 1. Directory Structure

```text
frontend/
├── assets/                  # Static fonts, icons, images
├── lib/
│   ├── core/                # Shared application infrastructure
│   │   ├── routing/         # GoRouter setup & RouteNames constants
│   │   ├── theme/           # AppColors, AppTextStyles, AppTheme
│   │   └── widgets/         # Globally shared widgets (GlassPill, CTAs, Cards, etc.)
│   ├── data/                # Data layer
│   │   └── models/          # Domain data models (Doctor, etc.)
│   ├── features/            # Feature-first modular screens & widgets
│   │   ├── assessment/      # AI Diagnostics & Consensus Output Screens (Reports, Reasoning, Trajectory)
│   │   ├── auth/            # Authentication & Onboarding
│   │   ├── dashboard/       # Home Dashboard & Metric Overview
│   │   ├── doctors/         # Specialist Care Finder & Recommendations
│   │   ├── intake/          # 5-Step Clinical Intake Flow (Clinical Status, Meds, Symptoms, Labs, Review)
│   │   └── simulation/      # Counterfactual Lifestyle Simulator
│   └── main.dart            # Application entry point
└── test/                    # Unit and widget tests
```

---

## 2. Design System & Tokens (`lib/core/theme/`)

All colors and text styles must reference tokens declared in `app_colors.dart` and `app_text_styles.dart`. **Never hardcode hex values or raw text styles in widget files.**

### Strict Color Palette

| Token | Hex | Visual Identity | Usage |
|---|---|---|---|
| `AppColors.canvasBackground` | `#FAF9F5` | Warm cream / ecru | Main background across all app screens |
| `AppColors.cardSurface` | `#FFFFFF` | Pure white | Reasoning cards, form cards, pill surfaces |
| `AppColors.textPrimary` | `#2C2520` | Earth brown | Main readable text, headings, body copy |
| `AppColors.headerText` | `#4D738F` | Soft Slate / Powder Blue | Screen titles, wizard header background, major section titles |
| `AppColors.primaryAccent` | `#E04E26` | Burnt Orange | Primary interactive elements, CTA buttons, active states |
| `AppColors.alertMedium` | `#E89A3E` | Ochre / Amber | Warning badges, caution indicators, doubt alerts |
| `AppColors.borderSubtle` | `#D6CFC4` | Neutral outline | Container borders, dividers, subtle card outlines |

### Typography Scale

- **Headings:** **Instrument Serif** (`28.0` screen titles, `24.0` card titles).
- **Body & Inputs:** **Lexend** (`14.0` labels/body, `12.0` helpers, `16.0` primary CTAs).

---

## 3. Screen Routing Map (`lib/core/routing/`)

All routes are defined statically in `RouteNames` (`lib/core/routing/route_names.dart`).

```text
/ (Auth)
└── /dashboard (Home Dashboard)
    │
    ├── /intake/step-1     -> Step1ChronicConditionsAndHistoryInputScreen (Chronic Conditions & Surgeries)
    ├── /intake/step-2     -> Step2MedicationsAndFamilyHistoryInputScreen (Medications & Family History)
    ├── /intake/step-3     -> Step3SymptomsAndSeverityInputScreen (Active Symptoms & Severity)
    ├── /intake/step-4     -> Step4VitalsAndBloodTestsInputScreen (Vitals & Lab Biomarkers)
    └── /intake/step-5     -> Step5DataReviewAndSubmissionScreen (Summary & Submission)
        │
        └── /results/reports     -> AssessmentPrimaryFindingScreen (Primary Finding & Stacked Reports)
            ├── /results/reasoning   -> AssessmentAiReasoningConsensusScreen (AI Reasoning Map & Consensus)
            ├── /results/trajectory  -> AssessmentRiskTrajectoryForecastScreen (10-Year Risk Trajectory & Actions)
            ├── /results/simulate    -> SimulateLifestyleScreen (Counterfactual Simulator)
            └── /results/care-finder -> DoctorRecommendationScreen (Specialist Finder)
```

---

## 4. Reusable Widgets (`lib/core/widgets/`)

| Widget | Purpose |
|---|---|
| `GlassPillButton` | Glassmorphic pills for header actions (`Save & exit`) and footer secondary buttons (`Back`). |
| `GradientCtaButton` | Primary action button with fixed 56.0 height, 12.0 radius, and `AppColors.primaryAccent`. |
| `AssessmentSectionCard` | Base white card container with `AppColors.borderSubtle` and 12.0 radius. |
| `ExpandableSectionCard` | Accordion card container with expand/collapse animations. |
| `DisclaimerText` | Mandatory clinical disclaimer footnote on AI decision-support screens. |
| `ChoiceSegment` | Segmented choice toggle with active Burnt Orange highlight. |
| `UnitTextField` | Numeric input container with integrated unit label (`cm`, `kg`, `mmHg`). |
| `TappableValueField` | Labeled selector row with trailing chevron for bottom-sheet pickers. |
