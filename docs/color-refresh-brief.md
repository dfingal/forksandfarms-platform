# Goal

Refresh the existing website using Laurel Green as the primary page
background, while preserving the current forest-green typography and
brand identity. Use Sage Green sparingly as an accent and warm off-white
for cards. This is a color-only update, not a redesign.

# Approved palette

| Role                                 | Color          | Value                          |
|--------------------------------------|----------------|--------------------------------|
| Primary page background              | Laurel Green   | \#A9BA9D                       |
| Primary text, logo, headings         | Forest Green   | \#304F3B                       |
| Card and content surfaces            | Warm Off-White | \#F7F6F0                       |
| Accent / featured card               | Sage Green     | \#9DC183                       |
| Secondary text (on light cards only) | Muted Green    | \#526B59                       |
| Borders / separators                 | Tonal Green    | Choose accessible subtle shade |

Color values are starting tokens. Preserve the current forest green if
the codebase already defines an authoritative brand token; avoid
introducing near-duplicate greens.

# Implementation instructions

**Global canvas:** Replace the existing cream page background with
\#A9BA9D on the body, app shell, and normal section backgrounds. Avoid
stray cream strips or gaps.

**Navbar (updated 2026-11-12):** The header is sticky and sits above
the Google Map. It keeps the existing logo, wordmark, links, icons and
hamburger, and has two looks:
- **lg (1024px) and up:** a floating, rounded bar inset from the top
  and sides.
  - Max width 1440px, centred, with 24px side margins on narrower
    screens. It's wider than the page content, which keeps its own
    width.
  - At the top of the page it's Warm Off-White \#F7F6F0. After about
    20px of scrolling it changes to Nav Scrolled \#E0E6DB (token
    `nav-scrolled`) with a subtle shadow.
  - The change is a 200ms transition, or instant under
    prefers-reduced-motion.
  - Laurel shows around the bar.
- **Below 1024px:** a regular full-width sticky header, edge to edge,
  with no rounded corners or side gaps.
  - Warm Off-White \#F7F6F0 with a subtle bottom border, and no scroll
    colour change.
  - The mobile menu panel opens full width below it.

**Footer:** Use Laurel Green for the default footer background; retain
the existing logo, green wordmark, links, and icon styling. Keep subtle
separators where needed.

**Hero:** Keep the existing copy, imagery, spacing, typography, and CTA
layout. Set the hero surface to Laurel Green; keep headings and primary
body copy in Forest Green.

**Cards:** Use \#F7F6F0 for standard cards, including “What We Do,”
venue cards, and partner-service cards. Keep existing radius, shadows,
dimensions, and spacing.

**Accent treatment:** Use \#9DC183 selectively for one featured card,
callout, or accent surface at a time. Do not turn every card green.
Retain existing primary dark-green buttons.

**Map and venue listings:** Do not change map tiles, markers, map
behavior, photos, or venue data. Update only surrounding section
surfaces and card backgrounds.

**Text and contrast:** Forest Green \#304F3B should be the default text
on Laurel and Sage surfaces. Muted secondary text should be tested and
darkened if needed. Keep white/off-white button labels on dark-green
buttons.

**Responsive states:** Apply the same palette on mobile and desktop.
Verify navigation menus, focus states, hover states, badges, inputs, and
sticky elements.

# Technical constraints

- Implement via existing CSS variables, theme tokens, or component theme
  definitions; avoid scattered hardcoded replacements.

- Do not change logos, font families, text case, copy, layout, spacing,
  imagery, functionality, or component hierarchy.

- Preserve semantic states (success, error, disabled) and verify WCAG AA
  text contrast, including secondary text and interactive controls.

- Keep changes scoped and easy to revert. Do not modify third-party map
  styling or assets.

# Acceptance checklist

☐ Laurel Green is the dominant site background, including navbar and
major page sections.

☐ Forest Green remains the primary brand and text color.

☐ Standard cards are warm off-white; Sage Green appears only as a
deliberate accent.

☐ No accidental cream gaps, low-contrast labels, or unreadable buttons.

☐ Desktop and mobile layouts and all interactions are unchanged.

☐ Provide a concise summary of files/tokens changed and screenshots of
desktop/mobile for review.

# Instruction to implementing AI

Make only the color-scheme changes specified above. If a component
requires an additional color for accessibility, choose the smallest
necessary adjustment and report it. Do not independently redesign the
website.

# Addendum (decisions after contrast check — 2026-11-12)

- **Forest Green token:** keep the existing site token `#365540` (matches the logo). Do NOT add `#304F3B`; the two are near-duplicates (contrast 1.10:1).
- **Contrast finding:** `#365540` on Laurel `#A9BA9D` is 4.03:1 and on Sage `#9DC183` is 4.11:1 — below WCAG AA (4.5:1) for normal-size text (passes only for large text ≥24px, or ≥18.66px bold). Muted Green `#526B59` on Laurel is 2.83:1 — only use it on off-white cards (5.38:1 there).
- **Fix to apply (smallest adjustment, keeps one brand green):** lighten the page background slightly from `#A9BA9D` to `#B8C7AE` (brand green on it = 4.67:1). Sage accent surfaces must only carry large text, or use off-white text-free accents, unless contrast is otherwise met.
- **Update (2026-11-12):** the page background is now `#C6D2BE`, a few shades lighter again, and the scrolled navbar is `#E0E6DB`. Re-verified:
  - Brand green is 5.28:1 on the background and 6.53:1 on the scrolled navbar.
  - Muted Green is 3.71:1 on the background, so it is still for off-white cards only (5.38:1 there).
  - Terracotta `#743b1b` (links, errors, focus ring) is 5.61:1 on the background and 6.93:1 on the scrolled navbar.
  - Off-white labels on the green buttons are 7.67:1, and 6.29:1 on hover.
- Report any other accessibility adjustments in the summary.
