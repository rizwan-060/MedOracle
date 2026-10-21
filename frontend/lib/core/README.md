# Front end - shared foundation

Screens live in `lib/features/<feature>/`; anything reusable lives in
`lib/core/`. This file is the map of what already exists so new screens reuse
it instead of re-inventing patterns.

## Design tokens

| File | Contents |
| --- | --- |
| `core/theme/app_colors.dart` | **The only place hex values are allowed.** Brand palette + the exact tokens of the `MedOracle v3.1 - Intake Flow` reference, plus every gradient. |
| `core/theme/app_text_styles.dart` | Plus Jakarta Sans type scale (sizes / line heights / weights measured from the reference frames). |
| `core/theme/app_theme.dart` | `ThemeData`, input decoration, snack bar, selection colours. |

Fonts: `assets/fonts/PlusJakartaSans.ttf` (SIL OFL 1.1), registered in
`pubspec.yaml` as the `Plus Jakarta Sans` family.

## Routing (`core/routing`)

`route_names.dart` holds every path; `app_router.dart` builds the `GoRouter`.

```
/patient-profile        -> ProfileScreen          (built)
/clinical-status        -> ClinicalStatusScreen   (built)
/medications-family     -> MedicationsFamilyScreen(built)
/symptoms               -> SymptomsScreen         (built)
/laboratory-vitals      -> LabsVitalsScreen       (built)
/assessment-review      -> ReviewConfirmScreen    (built)
/results/reports        -> Clinical Reports       (pending)
```

`initialLocation` is `/patient-profile`. All assessment sections navigate via `RouteNames`.

## Reusable widgets (`core/widgets`)

| Widget | Use |
| --- | --- |
| `step_scaffold.dart` | Whole intake page: maroon header + scroll area + CTA/Back footer. |
| `step_header.dart` | Header only (autosave badge, wordmark, `Save & exit`, progress rails). `StepScaffold` uses it. |
| `expandable_section_card.dart` | Collapsible white card with the blurred glow while expanded. |
| `field_group.dart` | Label + control with the reference's 12px/4px rhythm. |
| `choice_segment.dart` | Pill-row single select (`Male / Female / Other`). |
| `unit_text_field.dart` | Numeric field with unit suffix (`170 cm`). |
| `tappable_value_field.dart` | Read-only select/date field (chevron or caret suffix). |
| `tag_chips_field.dart` | Removable chip list + `+ Add ...` affordance. |
| `gradient_cta_button.dart` | Primary maroon pill CTA. |
| `glass_pill_button.dart` | `.header` (glass, on maroon) and `.footer` (`Back`) pills. |
| `brand_logo.dart` | `BrandShield` (vector mark) and `BrandLogo` (mark + wordmark). |
| `autosave_badge.dart` | "Autosaved" / "Saving..." micro status. |
| `ref_chevron.dart` | The 18px painted chevron used everywhere. |
| `disclaimer_text.dart` | Standard non-diagnostic footnote. |

**Rule:** any widget needing a `Material` ancestor for `InkWell` must provide
its own `Material(color: Colors.transparent)` - `StepScaffold` deliberately
does not wrap the page in a `Scaffold`.

## State (`flutter_riverpod`)

- Repository providers: `lib/data/providers/repository_providers.dart`.
- `MockIntakeRepository` (`lib/data/repositories/intake_repository.dart`) holds
  the demo patient from the design reference; swap for an HTTP implementation
  without touching the UI.
- `SectionAccordionController`
  (`lib/features/intake/providers/section_accordion_controller.dart`) keeps
  exactly one accordion section open. Because Riverpod uses the unnamed
  constructor, each screen defines a tiny subclass and overrides
  `sectionAccordionProvider` inside a local `ProviderScope` - see
  `_ProfileAccordion` in `features/profile/screens/profile_screen.dart`.

## Adding the next intake screen

1. Add/extend the model in `lib/data/models/` (mirror the backend schema).
2. Extend `IntakeRepository` + `MockIntakeRepository`.
3. Add a `Notifier` controller under `features/<feature>/providers/`.
4. Split the screen body into section widgets under `features/<feature>/widgets/`.
5. Build the page with `StepScaffold` and one `ExpandableSectionCard` per
   section; keep the screen file to composition only.
6. Swap the `PendingStepScreen` route in `app_router.dart`.
