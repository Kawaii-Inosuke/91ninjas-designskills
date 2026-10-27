# Base critic rules (all brands)
Load order: `brands/<client>/critic_rules.md` first, then this file.
If a brand rule conflicts with a base rule, the brand rule wins and the base rule is skipped.
Each check is PASS/FAIL on the rendered PNG.

## Brand fidelity (details live in the brand's critic_rules.md)
1. Every brand-specific rule passes.
2. Only colours and fonts from the brand tokens; no literal hex outside the `:root` token block.
3. Layout type differs from the client's recent layouts (registry check).
4. Canvas size matches the brand pack.

## Hierarchy
5. One dominant element (title or key visual); the eye knows where to start in 2 seconds.
6. At most 3 visible text sizes doing the work; 5 is the ceiling.
7. Heading vs body differ clearly by weight or size, not by colour alone.
8. Reading order matches the content order (top-down or left-right, no zig-zag).

## Spacing and alignment
9. Equal outer margins; content respects the brand's minimum padding.
10. Gaps between sections clearly larger than gaps inside a section.
11. Everything snaps to one grid; equal items have equal size and spacing.
12. More space above a heading than below it.
13. Markers/icons optically centred with their text line.

## Legibility
14. Body text contrast >= 4.5:1, large text >= 3:1 against its actual background.
15. No text overflow, clipping, orphaned single words or overlapping elements.
16. Line length <= ~60 characters for body; no paragraph longer than 3 lines.
17. Text on coloured fills uses the brand's specified on-colour.

## Content honesty
18. Every number, claim and name comes from the content part. No invented stats.
19. Copy is tightened, not padded: ~80 words or fewer per panel, one idea per panel.
20. No filler labels: no eyebrow/kicker above headings, no tracked all-caps labels.

## Anti-generic (refuse unless the brand asks for it)
21. No identical icon+heading+text card grid as the default structure.
22. No card inside a card; no gradient text; no glass/blur; no purple-blue gradients.
23. No emoji or unicode glyphs as icons; icons from one set, one stroke weight.
24. No heavy or hard-offset drop shadows; elevation is a tone step or subtle shadow.
25. No coloured side-stripe borders thicker than 1px on cards.
26. No decorative chrome (fake charts, sparklines, progress rings) standing in for content.

## Output
27. Height fits content with no dead space at the bottom.
28. Renders crisply at export scale; no blurry rasters, no broken images.

## Critic report format
Per pass: list only FAILs as `rule# | what is wrong | fix`. Stop when 0 FAILs or after 3 revisions.
