# MedOracle Frontend Rules

## 1. Architecture & Modularity
- **Framework:** Flutter (Dart).
- **Structure:** Use a feature-first architecture. Isolate screens in `lib/features/` and shared elements in `lib/core/`.
- **State & Routing:** Use `flutter_riverpod` for state management and `go_router` for navigation.
- **Modularity:** Extract repetitive UI elements into reusable widgets inside `lib/core/widgets/`. Do not write monolithic screen files.

## 2. UI & Strict Color Palette
Always import and use `AppColors` from `lib/core/theme/app_colors.dart`. Do NOT hardcode hex values in individual widget files. 
- **Canvas Background:** `#FAF9F5` (Warm cream / ecru background)
- **Card Surface:** `#FFFFFF` (Core reasoning cards, white pill buttons)
- **Text Primary:** `#2C2520` (Earth brown text)
- **Header Text:** `#4D738F` (Soft Slate / Powder Blue for headers)
- **Primary Accent:** `#E04E26` (Burnt Orange active elements/buttons)
- **Alert Medium:** `#E89A3E` (Ochre / Amber indicators)
- **Border Subtle:** `#D6CFC4` (Subtle neutral container outlines)

## 3. Layout, Spacing & Form Standards (MANDATORY)
- **Screen Padding:** Uniform horizontal padding of `20.0`.
- **Vertical Gaps:** Use `16.0` (tight), `24.0` (standard form elements), or `40.0` (major sections).
- **Text Fields:** Must be a single clean container with an `AppColors.border`. **Never** nest text fields inside other boxes (no box-inside-a-box bug).
- **Primary Buttons:** Fixed height of `56.0`, radius `12.0`.
- **Cards & Containers:** Uniform border radius of `12.0` with `AppColors.border`.

## 4. Typography Standards for Mobile
- **Headings:** **Instrument Serif** (`28.0` screen titles, `24.0` card titles).
- **Body & Inputs:** **Lexend** (`14.0` labels/body, `12.0` helpers).