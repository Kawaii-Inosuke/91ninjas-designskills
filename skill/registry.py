"""Shared infographic registry (Supabase Postgres + pgvector). Every command prints JSON.

  registry.py init                                  apply sql/schema.sql
  registry.py check    --client C --topic T [--angle A] [--window N]
  registry.py reserve  --client C --topic T [--angle A] [--key-points K] [--layout L] [--brand-version V] [--force]
  registry.py release  --id ID
  registry.py log      --id ID --png P --html H [--layout L] [--brand-version V] [--force]
  registry.py list     --client C [--status S] [--limit N]
  registry.py backfill --client C --file rows.json [--status approved|old_brand]
  registry.py reembed  --client C                  refresh vectors after a model/topic change
"""
import argparse
import getpass
import json
import os
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import imagehash
import psycopg
import requests
import yaml
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from PIL import Image
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
CFG = yaml.safe_load((ROOT / "skill/config.yaml").read_text())
DEDUP = CFG["dedup"]


def connect():
    conn = psycopg.connect(os.environ["DATABASE_URL"], autocommit=True, row_factory=dict_row)
    register_vector(conn)
    return conn


@lru_cache(maxsize=1)
def _model():
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
    os.environ.setdefault("HF_HUB_VERBOSITY", "error")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")  # model is cached after first install
    import logging
    logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(CFG["embedding"]["model"])


def embed(topic, angle=""):
    return _model().encode(f"{topic}. {angle or ''}".strip(" ."), normalize_embeddings=True)


def embeds(topic, angle=""):
    """(topic+angle, topic-only) vectors; check compares both so a bare topic still matches."""
    return embed(topic, angle), embed(topic)


def designer():
    if os.getenv("DESIGNER"):
        return os.environ["DESIGNER"]
    name = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True).stdout.strip()
    return name or getpass.getuser()


def verdict(rows, block=DEDUP["block"], warn=DEDUP["warn"]):
    """Finished work (approved/old_brand) at >= block blocks; anything else at >= warn warns.
    Pending rows only warn: a colleague is working on it, the designer decides."""
    hits = [r for r in rows if r["sim"] >= warn]
    if any(r["status"] != "pending" and r["sim"] >= block for r in hits):
        return "block"
    return "warn" if hits else "ok"


def similar(conn, client, vecs, exclude_id=None, limit=5):
    v, t = vecs
    return conn.execute(
        """select * from (
             select id, topic, angle, status, layout_type, created_by, created_at,
                    round(greatest(1 - (embedding <=> %(v)s),
                                   coalesce(1 - (topic_embedding <=> %(t)s), 0))::numeric, 3)::float as sim
             from infographics
             where client = %(c)s and status <> 'rejected' and embedding is not null
               and (status <> 'pending' or created_at > now() - make_interval(days => %(ttl)s))
               and id is distinct from %(x)s::uuid) m
           order by sim desc limit %(n)s""",
        {"v": v, "t": t, "c": client, "ttl": DEDUP["pending_ttl_days"], "x": exclude_id, "n": limit},
    ).fetchall()


def recent_layouts(conn, client, n):
    rows = conn.execute(
        """select layout_type from infographics where client = %s and status = 'approved'
           and layout_type is not null order by created_at desc limit %s""", (client, n)).fetchall()
    return [r["layout_type"] for r in rows]


def check(conn, client, topic, angle="", window=None):
    rows = similar(conn, client, embeds(topic, angle))
    return {"verdict": verdict(rows),
            "matches": [r for r in rows if r["sim"] >= DEDUP["warn"]] or rows[:1],
            "avoid_layouts": recent_layouts(conn, client, window or DEDUP["layout_window"])}


def reserve(conn, client, topic, angle="", key_points="", layout=None, brand_version=None, force=False):
    res = check(conn, client, topic, angle)
    if res["verdict"] == "block" and not force:
        return res
    res["id"] = conn.execute(
        """insert into infographics (client, topic, angle, key_points, layout_type, brand_version,
                                     embedding, topic_embedding, status, created_by)
           values (%s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s) returning id""",
        (client, topic, angle, key_points, layout, brand_version, *embeds(topic, angle), designer()),
    ).fetchone()["id"]
    return res


def release(conn, id_):
    row = conn.execute("delete from infographics where id = %s and status = 'pending' returning id", (id_,)).fetchone()
    return {"released": bool(row), "id": id_}


CONTENT_TYPES = {".png": "image/png", ".html": "text/html", ".svg": "image/svg+xml", ".jpg": "image/jpeg",
                 ".pdf": "application/pdf"}


def upload(path, key):
    secret = os.environ["SUPABASE_SECRET_KEY"]
    bucket = CFG["storage"]["bucket"]
    r = requests.post(
        f"{os.environ['SUPABASE_URL']}/storage/v1/object/{bucket}/{key}",
        data=Path(path).read_bytes(), timeout=60,
        headers={"apikey": secret, "Authorization": f"Bearer {secret}", "x-upsert": "true",
                 "Content-Type": CONTENT_TYPES.get(Path(key).suffix, "application/octet-stream")})
    r.raise_for_status()
    return f"{bucket}/{key}"


def phash_of(png):
    return str(imagehash.phash(Image.open(png)))


def visual_dupes(conn, client, ph, exclude_id):
    rows = conn.execute(
        """select id, topic, phash from infographics where client = %s and phash is not null
           and status in ('approved', 'old_brand') and id <> %s""", (client, exclude_id)).fetchall()
    h = imagehash.hex_to_hash(ph)
    return [{"id": r["id"], "topic": r["topic"], "distance": h - imagehash.hex_to_hash(r["phash"])}
            for r in rows if h - imagehash.hex_to_hash(r["phash"]) <= DEDUP["phash_max_distance"]]


def log(conn, id_, png, html, layout=None, brand_version=None, force=False):
    row = conn.execute("select client from infographics where id = %s and status = 'pending'", (id_,)).fetchone()
    if not row:
        return {"error": f"no pending row {id_}"}
    ph = phash_of(png)
    dupes = visual_dupes(conn, row["client"], ph, id_)
    if dupes and not force:
        return {"logged": False, "visual_duplicates": dupes}
    key = f"{row['client']}/{id_}"
    conn.execute(
        """update infographics set status = 'approved', phash = %s, png_url = %s, html_url = %s,
                  layout_type = coalesce(%s, layout_type), brand_version = coalesce(%s, brand_version)
           where id = %s""",
        (ph, upload(png, f"{key}.png"), upload(html, f"{key}.html"), layout, brand_version, id_))
    # exports from `render.py export` sit next to the PNG; stored at the same key with their own extension
    extras = [upload(p, f"{key}{p.suffix}") for p in (Path(png).with_suffix(s) for s in (".svg", ".jpg", ".pdf"))
              if p.exists()]
    return {"logged": True, "id": id_, "phash": ph, "exports": extras}


def list_rows(conn, client, status=None, limit=20):
    return conn.execute(
        """select id, topic, angle, layout_type, status, brand_version, created_by, created_at
           from infographics where client = %s and (%s::text is null or status = %s)
           order by created_at desc limit %s""", (client, status, status, limit)).fetchall()


def backfill(conn, client, rows, status="approved"):
    """rows: dicts from analyze.py. Skips rows whose `source` is already registered."""
    added = 0
    for r in rows:
        if r.get("source") and conn.execute(
                "select 1 from infographics where client = %s and source = %s", (client, r["source"])).fetchone():
            continue
        kp = r.get("key_points") or ""
        conn.execute(
            """insert into infographics (client, topic, angle, key_points, layout_type, brand_version,
                                         embedding, topic_embedding, phash, png_url, source, status, created_by)
               values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (client, r["topic"], r.get("angle"), "\n".join(kp) if isinstance(kp, list) else kp,
             r.get("layout_type"), r.get("brand_version"), *embeds(r["topic"], r.get("angle")),
             r.get("phash"), r.get("png_url"), r.get("source"), status, designer()))
        added += 1
    return {"added": added, "skipped": len(rows) - added}


def reembed(conn, client):
    rows = conn.execute("select id, topic, angle from infographics where client = %s", (client,)).fetchall()
    for r in rows:
        conn.execute("update infographics set embedding = %s, topic_embedding = %s where id = %s",
                     (*embeds(r["topic"], r["angle"]), r["id"]))
    return {"reembedded": len(rows)}


def main(argv=None):
    p = argparse.ArgumentParser(description="Infographic registry")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    for name in ("check", "reserve"):
        s = sub.add_parser(name)
        s.add_argument("--client", required=True)
        s.add_argument("--topic", required=True)
        s.add_argument("--angle", default="")
        if name == "check":
            s.add_argument("--window", type=int)
        else:
            s.add_argument("--key-points", default="")
            s.add_argument("--layout")
            s.add_argument("--brand-version")
            s.add_argument("--force", action="store_true")
    sub.add_parser("release").add_argument("--id", required=True)
    sub.add_parser("reembed").add_argument("--client", required=True)
    s = sub.add_parser("log")
    for a in ("--id", "--png", "--html"):
        s.add_argument(a, required=True)
    s.add_argument("--layout")
    s.add_argument("--brand-version")
    s.add_argument("--force", action="store_true")
    s = sub.add_parser("list")
    s.add_argument("--client", required=True)
    s.add_argument("--status")
    s.add_argument("--limit", type=int, default=20)
    s = sub.add_parser("backfill")
    s.add_argument("--client", required=True)
    s.add_argument("--file", required=True)
    s.add_argument("--status", default="approved", choices=["approved", "old_brand"])
    a = p.parse_args(argv)

    with connect() if a.cmd != "init" else psycopg.connect(os.environ["DATABASE_URL"], autocommit=True) as conn:
        if a.cmd == "init":
            conn.execute((ROOT / "sql/schema.sql").read_text())
            out = {"schema": "applied"}
        elif a.cmd == "check":
            out = check(conn, a.client, a.topic, a.angle, a.window)
        elif a.cmd == "reserve":
            out = reserve(conn, a.client, a.topic, a.angle, a.key_points, a.layout, a.brand_version, a.force)
        elif a.cmd == "release":
            out = release(conn, a.id)
        elif a.cmd == "log":
            out = log(conn, a.id, a.png, a.html, a.layout, a.brand_version, a.force)
        elif a.cmd == "reembed":
            out = reembed(conn, a.client)
        elif a.cmd == "list":
            out = list_rows(conn, a.client, a.status, a.limit)
        else:
            out = backfill(conn, a.client, json.loads(Path(a.file).read_text()), a.status)
    print(json.dumps(out, default=str, indent=1))
    blocked = isinstance(out, dict) and (out.get("verdict") == "block" and "id" not in out
                                         or out.get("logged") is False or "error" in out)
    sys.exit(2 if blocked else 0)


if __name__ == "__main__":
    main()
