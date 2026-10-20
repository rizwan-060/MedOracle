---
trigger: always_on
---

# MedOracle Frontend Rules

## 1. Architecture & Modularity
- **Framework:** Flutter (Dart).
- **Structure:** Use a feature-first architecture. Isolate screens in `lib/features/` and shared elements in `lib/core/`.
- **State & Routing:** Use `flutter_riverpod` for state management and `go_router` for navigation.
- **Modularity:** Extract repetitive UI elements into reusable widgets inside `lib/core/widgets/`. Do not write monolithic screen files.

## 2. UI & Strict Color Palette
Always import and use `AppColors` from `lib/core/theme/app_colors.dart`. Do NOT hardcode hex values in individual widget files. 
- **Primary Maroon:** `#6C3B43` (Headers, primary buttons, active tracks, numbered step badges)
- **Maroon Dark:** `#4E2831` (Bottom gradient stops on primary CTA buttons)
- **Dusty Taupe:** `#B49C91` (Inactive tracks, secondary borders)
- **Muted Green:** `#526853` (Completed status indicators, positive delta badges)
- **Green Surface:** `#EAF1EB` (Validation card backgrounds)
- **Amber Warning:** `#C4822B` (Doubt raised/caution callout borders)
- **Amber Surface:** `#FBF5EB` (Doubt raised/caution card backgrounds)
- **Canvas Background:** `#F7F5F5` (App background behind scrollable cards)
- **Card Surface:** `#FFFFFF` (Core reasoning cards, white pill buttons)
- **Border Subtle:** `#E8E2E1` (Subtle container outlines, chart divider lines)
- **Text Primary:** `#1C1819` (Main findings, bold percentages, primary labels)
- **Text Muted:** `#6F6567` (Descriptive subtexts, helper footnotes, timestamps)

## 3. Design Translation Workflow
- Web-based HTML/Tailwind reference codes are stored in the `@design_refs/` folder.
- When instructed to build a screen based on a design reference, translate the exact layout, padding, fonts, and colors 1:1 into native Flutter Dart code.
- **CRITICAL:** Do NOT generate web HTML or CSS in this project. You must output pure Dart widgets (`Container`, `Column`, `Row`, `BoxDecoration`, etc.).
