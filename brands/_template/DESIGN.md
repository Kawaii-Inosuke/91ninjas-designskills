---
version: alpha                 # design.md format version (google-labs-code/design.md)
name: <Client name>
brand_version: 1.0.0           # bump on every change; stored on each logged infographic
updated: YYYY-MM-DD
description: <one line on the brand's visual voice>
colors:
  primary: "#000000"
  secondary: "#000000"
  surface: "#FFFFFF"
  ink: "#000000"               # body text
  on-primary: "#FFFFFF"
typography:
  title:   {fontFamily: <Font>, fontSize: 48px, fontWeight: 500, lineHeight: 1.2}
  heading: {fontFamily: <Font>, fontSize: 32px, fontWeight: 600, lineHeight: 1.3}
  body:    {fontFamily: <Font>, fontSize: 28px, fontWeight: 400, lineHeight: 1.45}
rounded:
  sm: 12px
  lg: 24px
spacing:
  page: 80px                   # minimum outer padding
  section: 64px                # gap between blocks
  item: 24px                   # gap inside a block
infographic:
  canvas: {width: 1080, height: auto}   # height: auto = fits content
  device_scale_factor: 1
  layout_window: 1             # never reuse a layout used in the last N approved
  layouts: []                  # layout ids this brand allows (see skill/templates)
  icon: {style: line, color: primary, stroke: 2, scale: 0.6}   # icon = scale x item height
---

# <Client name>

## Overview
Personality, audience, how the infographics should feel. One paragraph.

## Colors
What each colour is for. Which colour text sits on which background.

## Typography
Font, where each style is used, any casing rules.

## Layout
Canvas, header/footer, content width, alignment, spacing rhythm.

## Elevation & Depth
Shadows or none; borders vs fills.

## Shapes
Radii, marker shapes (circle, hexagon...), connector style.

## Components
Header bar, cards, pills, markers, tables, takeaway box: one short rule each.

## Do's and Don'ts
- Do ...
- Don't ...
