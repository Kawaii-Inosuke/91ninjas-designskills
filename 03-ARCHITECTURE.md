# Infographic Skill v1: Architecture

```text
Designer (Claude Code)
        |
        v
   skill/SKILL.md  (workflow + rules)
        |
  +-----+------------------+------------------+
  |                        |                  |
  v                        v                  v
brands repo (Git)     registry.py         render.py
DESIGN.md per client      |               HTML -> Playwright -> PNG
                          v                      |
                 Supabase Postgres               v
                 (pgvector registry)      critic loop (Claude views PNG)
                          |                      |
                          v                      v
                 Supabase Storage  <---- approved PNG + HTML
```

## Components
- **SKILL.md:** the workflow Claude follows, including the two approval gates.
- **Brand repo:** single source of truth for design language, pulled fresh each job.
- **registry.py:** the only code that touches the database.
- **analyze.py:** vision pass that turns an old infographic into topic, angle, layout and palette usage.
- **render.py:** fills an HTML template with content and brand tokens, screenshots it.
- **critic_rules.md:** the design quality rules distilled from the reference repos.
- **Supabase:** shared registry and file storage, so every designer sees the same state.

## What we take from each repo
- **Google DESIGN.md and Awesome DESIGN.md:** brand pack format and examples
- **UI/UX Pro Max:** palette, style and font pairing knowledge for thin brand packs
- **Taste Skill, Impeccable, Hallmark, Emil Kowalski skills:** critic rules
- **Open Design:** workflow structure reference
- **React Bits, Magic UI, GSAP Skills, Scroll World, Canvas UI, Dimensional Drawing:** parked for v2

## Build order with approval gates
1. Supabase setup (you)
2. Claude Code reads the repos and summarizes. **Approve.**
3. Claude Code proposes the folder structure. **Approve.**
4. Schema and registry.py with tests. **Approve.**
5. DESIGN.md template and backfill for one client. **Approve.**
6. Render and critic loop. **Approve.**
7. SKILL.md and a trial run. **Approve.**
