---
version: alpha
name: Flipkart Commerce Cloud (FCC)
brand_version: 1.0.0
updated: 2026-10-27
description: Clean, airy B2B commerce explainers. One blue family on white, Inter throughout, generous whitespace.
colors:
  primary: "#0164F0"           # title, column headers, filled pills, connectors
  accent: "#4E93F5"            # number markers, outlines, card header bars, icons
  secondary: "#2872ED"         # rare accent fills
  tint: "#E6F0FE"              # card / panel fill, label cells
  header-bar: "#0164F01A"      # primary at 10% opacity
  ink: "#383838"               # all body text
  surface: "#FFFFFF"
  cell: "#F2F2F2"              # neutral table / card cells
  line: "#888888"              # neutral outlines (used at ~50% opacity)
  on-primary: "#FFFFFF"
typography:
  title:   {fontFamily: Inter, fontSize: 48px, fontWeight: 500, lineHeight: 1.2}
  heading: {fontFamily: Inter, fontSize: 32px, fontWeight: 500, lineHeight: 1.3}
  body:    {fontFamily: Inter, fontSize: 30px, fontWeight: 400, lineHeight: 1.45}
  label:   {fontFamily: Inter, fontSize: 30px, fontWeight: 600, lineHeight: 1.3}
  marker:  {fontFamily: Inter, fontSize: 44px, fontWeight: 600, lineHeight: 1}
rounded:
  sm: 15px
  md: 20px
  lg: 28px
  full: 999px
spacing:
  page: 80px
  section: 72px
  item: 28px
components:
  header-bar: {backgroundColor: "{colors.header-bar}", height: 118px, typography: "{typography.title}", textColor: "{colors.primary}"}
  card-tint: {backgroundColor: "{colors.tint}", rounded: "{rounded.md}"}
  card-outline: {backgroundColor: "{colors.surface}", borderColor: "{colors.accent}", borderWidth: 3px, rounded: "{rounded.md}"}
  pill: {backgroundColor: "{colors.primary}", textColor: "{colors.on-primary}", rounded: "{rounded.md}"}
  marker: {borderColor: "{colors.accent}", borderWidth: 3px, textColor: "{colors.accent}"}
  takeaway: {backgroundColor: "{colors.tint}", borderColor: "{colors.accent}", borderWidth: 2px, rounded: "{rounded.sm}"}
infographic:
  canvas: {width: 1920, height: auto}
  device_scale_factor: 1
  content_max_width: 1500       # content is a centred block, not full bleed
  layout_window: 1              # never repeat the previous layout
  layouts:                      # family/variant; rotation compares the family
    - vertical_list/icon        # icon tiles + connector, title + description
    - vertical_list/number      # circle or hexagon numbers + dashed connector
    - vertical_list/side_rail   # numbers in a tinted rail, text beside
    - horizontal_timeline/arrow
    - horizontal_timeline/alternating   # labels alternate above / below
    - s_curve_steps
    - hex_zigzag_row
    - central_spine
    - comparison_cards/pill_header
    - comparison_cards/outline
    - comparison_cards/vs
    - comparison_cards/divider
    - cell_table
    - card_list/check
    - card_list/number
    - three_column_grid
    - hub_and_spoke
    - pyramid
    - before_after
    - stat_callout_grid
  icon: {style: line, color: accent, stroke: 1.5, scale: 0.6, container: [none, tint_square, hexagon]}
---

# Flipkart Commerce Cloud (FCC)

Source: `source/FCC_rules.md`, corrected against the 20 past infographics in `past/`.
Where they disagree, the past work wins (it is what clients approved).

## Overview
Explainers for B2B commerce topics (pricing, ads, procurement, visual commerce).
Calm, precise, airy. One idea per infographic, short phrases, no decoration for its own sake.

## Colors
- **Primary blue (#0164F0):** title text, table header cells, filled pills, VS circle.
- **Accent blue (#4E93F5):** number markers, card outlines, card header bars, icons, connectors.
- **Tint (#E6F0FE):** card and rail fills, label cells, takeaway box.
- **Ink (#383838):** every piece of body text. Never grey text.
- **Cell grey (#F2F2F2):** neutral table cells and checklist cards.
- Text on primary/accent fills is white. Text on tint is ink or primary.

## Typography
Inter only. Title 48px Medium in the header bar. Item headings ~32px Medium, body ~30px Regular,
table header cells 30px SemiBold white. Sentence case everywhere; never all caps.
FCC_rules.md lists 34-36px body; past work measures ~30px. Use 30px unless a designer says otherwise.

## Layout
Canvas 1920px wide, height fits content. Header bar 1920x118 at the top, title centred.
Content is a centred block up to 1500px wide with >= 80px padding. Generous whitespace between items.
Never repeat the previous infographic's layout family.

## Elevation & Depth
Flat. No drop shadows. Separation comes from tint fills and thin outlines.

## Shapes
Radius 20px for cards and pills, 15px for small cells, circles for markers.
Hexagons are an alternative marker and icon container. Connectors: thin dashed or solid accent lines.

## Components
- **Header bar:** primary at 10%, 118px, title only.
- **Markers:** "01"-style two-digit numbers in accent, inside a 3px accent circle or hexagon.
- **Icons:** line icons recoloured to accent; size scales with the item (about 0.6 x item height).
- **Comparison cards:** tint fill or white with outline; pill header in primary with white text.
- **Cell table:** separate rounded cells with gaps; header row primary/white; label column tint or grey.
- **Takeaway box:** optional one-sentence summary at the bottom, tint fill, accent outline, centred text.

## Do's and Don'ts
- Do keep each item to a short heading plus one line.
- Do centre the content block and keep both side margins equal.
- Don't add shadows, gradients, emoji, or extra colours.
- Don't invent numbers; every figure comes from the content part.
- Don't reuse the previous layout family.
