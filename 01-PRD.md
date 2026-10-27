# Infographic Skill v1: PRD

Prepared for 91Ninjas design team | October 27, 2026

## Problem
The design team turns content parts into client infographics by hand. Each client has its own design language, several designers work on the same clients, and nothing stops the same infographic (or a near copy) from being made twice.

## Goal
A Claude Code skill that takes a content part plus a client brand pack and produces an on-brand infographic PNG, checks it against all past infographics for that client, and logs it only after a designer approves.

## Users
- **Designers:** paste a content part, review a draft, approve.
- **Admin:** one-time setup, maintains brand packs and the registry.

## User flow
1. Designer picks the client and pastes the content part.
2. Skill pulls the latest brand pack from Git.
3. Skill extracts topic, angle and key points, then runs the dedup check against the shared registry.
4. If too similar to existing work, skill stops and shows the match. Otherwise it reserves a pending row.
5. Skill proposes an outline and layout. **Designer approves.**
6. Skill renders the infographic, runs the critic loop, shows the result.
7. **Designer approves** (or asks for changes).
8. Skill saves the PNG and source, and logs the row as approved.

## In scope (v1)
- Static infographics (PNG, plus the HTML source)
- One brand pack per client in DESIGN.md format
- Backfill analysis of old infographics into the registry
- Content-level and visual-level dedup
- Shared registry for the whole team
- Brand pack updates through Git with versioning

## Out of scope (v1)
- Animated or web infographics (React Bits, Magic UI, GSAP, Scroll World, Canvas UI)
- Web UI or standalone app (Strands Agents is a later option)
- Auto-publishing to social channels

## Success metrics
- Zero approved duplicates in a 4-week trial
- Draft ready in under 5 minutes from pasted content
- At least 80 percent of drafts approved within 2 revisions
- A new designer is productive within 15 minutes of setup

## Functional requirements
- **FR1:** Accept a content part as plain text, with the client name.
- **FR2:** Load and respect the client DESIGN.md (colors, type, spacing, tone, layout rules).
- **FR3:** Dedup check on content and layout before any rendering.
- **FR4:** Pending reservation visible to all designers.
- **FR5:** Critic loop with a maximum of 3 revisions.
- **FR6:** Nothing is final or logged without explicit designer approval.
- **FR7:** Each logged infographic records which brand pack version it used.
- **FR8:** Old infographics can be flagged as old brand after a rebrand.

## Open questions
- Output sizes needed per channel (LinkedIn square, portrait, blog wide)?
- Is there a minimum number of past infographics per client to backfill?
- Who approves brand pack changes (PR reviewer)?
