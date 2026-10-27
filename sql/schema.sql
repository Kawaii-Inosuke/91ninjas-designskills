-- Infographic registry. Safe to re-run.
create extension if not exists vector;

create table if not exists infographics (
  id            uuid primary key default gen_random_uuid(),
  client        text not null,
  topic         text not null,
  angle         text,
  key_points    text,                 -- newline-separated; never the full client document
  layout_type   text,
  brand_version text,
  embedding     vector(384),          -- topic + angle
  topic_embedding vector(384),        -- topic only
  phash         text,
  png_url       text,
  html_url      text,
  source        text,                 -- e.g. Figma frame URL or file name for backfilled rows
  status        text not null default 'pending'
                check (status in ('pending', 'approved', 'rejected', 'old_brand')),
  created_by    text,
  created_at    timestamptz not null default now()
);

-- Upgrade tables created from the earlier TRD draft.
alter table infographics add column if not exists source text;
alter table infographics add column if not exists topic_embedding vector(384);
do $$ begin
  alter table infographics add constraint infographics_status_check
    check (status in ('pending', 'approved', 'rejected', 'old_brand'));
exception when duplicate_object then null; end $$;

create index if not exists infographics_embedding_idx
  on infographics using hnsw (embedding vector_cosine_ops);
create index if not exists infographics_client_status_idx
  on infographics (client, status, created_at desc);

-- Block access through Supabase's public Data API (publishable key).
-- registry.py connects directly via DATABASE_URL, which is not subject to RLS as owner.
alter table infographics enable row level security;

-- Optional, admin runs once: restricted role for designers (insert/select/update only).
-- create role designer login password '...';
-- grant usage on schema public to designer;
-- grant select, insert, update on infographics to designer;
-- grant delete on infographics to designer;  -- needed for `release`
