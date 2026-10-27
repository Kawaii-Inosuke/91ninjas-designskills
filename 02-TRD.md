# Infographic Skill v1: TRD

## Stack
- **Runtime:** Claude Code with a project skill; Python 3.11+
- **Database:** Supabase (Postgres with the pgvector extension)
- **File storage:** Supabase Storage bucket named `infographics`
- **Embeddings:** sentence-transformers all-MiniLM-L6-v2 (384 dimensions, runs locally, no extra API key). Pinned in config so every designer uses the same model.
- **Visual hash:** imagehash (perceptual hash)
- **Render:** HTML and CSS template, Playwright (Chromium) to PNG
- **Brand packs:** Git repo, one DESIGN.md per client
- **DB access:** psycopg with a connection string in `.env`

## Repository layout

```text
infographic-skill/
  CLAUDE.md
  .env.example
  .gitignore
  requirements.txt
  reference/            # the 14 cloned repos, read-only inspiration
  brands/
    <client>/DESIGN.md
    <client>/past/      # old infographics for backfill
  skill/
    SKILL.md
    registry.py
    render.py
    analyze.py
    critic_rules.md     # distilled from Taste, Impeccable, Hallmark, Emil
    templates/          # HTML layouts
    config.yaml         # embedding model, thresholds, sizes
  sql/schema.sql
```

## Database schema

```sql
create extension if not exists vector;

create table infographics (
  id uuid primary key default gen_random_uuid(),
  client text not null,
  topic text not null,
  angle text,
  key_points text,
  layout_type text,
  brand_version text,
  embedding vector(384),
  phash text,
  png_url text,
  html_url text,
  status text not null default 'pending',  -- pending | approved | rejected | old_brand
  created_by text,
  created_at timestamptz default now()
);

create index on infographics using hnsw (embedding vector_cosine_ops);
create index on infographics (client, status);
```

## registry.py commands
- **check:** embed topic plus angle, query approved and pending rows for the same client, return matches above threshold plus recent layout types.
- **reserve:** insert a pending row.
- **log:** upload PNG and HTML, set status to approved with phash and brand version.
- **release:** remove a pending row if the designer abandons the job.
- **list:** show recent items for a client.
- **backfill:** run analyze.py on a folder of old PNGs and insert rows.

## Dedup rules
- **Content:** cosine similarity of topic plus angle at or above 0.85 is a block (starting value, tune with real data). Between 0.75 and 0.85 is a warning with the closest match shown.
- **Visual:** if the same layout_type appears in the last 4 approved items for that client, force a different layout.
- **Pending rows count** so two designers do not make the same piece at once.
- **Old brand rows** are excluded from style reference but still count for content dedup.

## Critic loop
1. Render the draft to PNG.
2. Claude views the PNG and scores it against the brand pack and critic_rules.md (contrast, hierarchy, spacing, font use, text overflow, generic AI look).
3. If any check fails, revise the HTML and re-render. Maximum 3 passes.
4. Show the final draft to the designer.

## Brand pack sync
- Skill runs `git pull` on the brands repo at the start of every job.
- Updates go to a branch and a pull request, merged by a reviewer.
- Each DESIGN.md has a version and date at the top. That version is stored on every logged row.

## Security
- Database credentials only in `.env`, which is in `.gitignore`.
- Use a restricted database role for designers (insert and select on infographics only), and keep the admin key out of the skill folder.
- Content parts may contain confidential client material, so the registry stores key points and links only, never full client documents.

## Testing
- Dedup test: feed a known past topic, expect a block.
- Concurrency test: two reservations of the same topic, expect the second to warn.
- Brand test: change a color in DESIGN.md, expect it in the next render.
- Three real content parts end to end before the team gets access.

## Milestones
1. Supabase and schema ready
2. Repo reference summary approved
3. registry.py working with tests
4. Backfill of one client complete
5. Render and critic loop working
6. SKILL.md assembled, trial with 2 designers
