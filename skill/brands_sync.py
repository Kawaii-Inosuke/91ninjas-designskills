"""Share brand packs through Supabase so designers need no GitHub. Every command prints JSON.

  brands_sync.py pull                               install the newest approved pack of every client into brands/
  brands_sync.py submit  --client C                 upload brands/C (without past/) for admin review
  brands_sync.py list    [--status pending]
  brands_sync.py review  --client C --version V     (admin) download a submitted pack into brands/C to inspect/render
  brands_sync.py approve --client C --version V     (admin) make it live; C's backfill rows in review become approved
  brands_sync.py reject  --client C --version V --note "why"   (admin) C's backfill rows in review are deleted

Admin commands need BRAND_ADMIN=1 in .env. Storage: bucket `brands`, files at <client>/<version>/<path>.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import brand  # noqa: E402
import registry  # noqa: E402

BUCKET = "brands"
SKIP = {"past"}            # old work stays local; its records are in the registry


def ensure_bucket():
    url = f"{os.environ['SUPABASE_URL']}/storage/v1/bucket"
    names = [b["name"] for b in requests.get(url, headers=registry.storage_headers(), timeout=30).json()]
    if BUCKET not in names:
        requests.post(url, json={"id": BUCKET, "name": BUCKET, "public": False},
                      headers=registry.storage_headers(), timeout=30).raise_for_status()


def pack_files(client):
    d = registry.ROOT / "brands" / client
    return sorted(str(p.relative_to(d)) for p in d.rglob("*")
                  if p.is_file() and p.relative_to(d).parts[0] not in SKIP and not p.name.startswith("."))


def local_version(client):
    try:
        return str(brand.load(client).get("brand_version"))
    except (FileNotFoundError, ValueError):
        return None


def install(conn, client, version):
    row = conn.execute("select files from brand_packs where client = %s and brand_version = %s",
                       (client, version)).fetchone()
    d = registry.ROOT / "brands" / client
    for rel in row["files"]:
        dst = d / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(registry.download(f"{client}/{version}/{rel}", BUCKET))
    return len(row["files"])


def pull(conn):
    live = conn.execute("""select distinct on (client) client, brand_version from brand_packs
                           where status = 'approved' order by client, reviewed_at desc""").fetchall()
    out = {}
    for r in live:
        c, v = r["client"], r["brand_version"]
        mine = local_version(c)
        approved_before = {x["brand_version"] for x in conn.execute(
            "select brand_version from brand_packs where client = %s and status = 'approved'", (c,)).fetchall()}
        if mine == v:
            out[c] = f"up to date ({v})"
        elif mine and mine not in approved_before:
            out[c] = f"kept local {mine} (not approved yet); live is {v}"
        else:
            out[c] = f"installed {v} ({install(conn, c, v)} files)"
    return out


def submit(conn, client):
    v = local_version(client)
    if not v:
        return {"error": f"brands/{client}/DESIGN.md missing or has no brand_version"}
    if conn.execute("select 1 from brand_packs where client = %s and brand_version = %s and status = 'approved'",
                    (client, v)).fetchone():
        return {"error": f"{client} {v} is already approved; bump brand_version and updated in DESIGN.md first"}
    ensure_bucket()
    files = pack_files(client)
    for rel in files:
        registry.upload(registry.ROOT / "brands" / client / rel, f"{client}/{v}/{rel}", BUCKET)
    conn.execute("""insert into brand_packs (client, brand_version, status, files, created_by)
                    values (%s, %s, 'pending', %s, %s)
                    on conflict (client, brand_version) do update
                    set status = 'pending', files = excluded.files, created_by = excluded.created_by,
                        created_at = now(), notes = null, reviewed_by = null, reviewed_at = null""",
                 (client, v, json.dumps(files), registry.designer()))
    return {"submitted": client, "version": v, "files": len(files), "status": "pending review by admin"}


def list_packs(conn, status=None):
    return conn.execute("""select client, brand_version, status, created_by, created_at, reviewed_by, notes
                           from brand_packs where (%s::text is null or status = %s)
                           order by created_at desc""", (status, status)).fetchall()


def require_admin():
    if os.getenv("BRAND_ADMIN") != "1":
        raise SystemExit(json.dumps({"error": "admin only: set BRAND_ADMIN=1 in .env on the admin's machine"}))


def decide(conn, client, version, approve, note=None):
    require_admin()
    row = conn.execute("""update brand_packs set status = %s, notes = %s, reviewed_by = %s, reviewed_at = now()
                          where client = %s and brand_version = %s returning client""",
                       ("approved" if approve else "rejected", note, registry.designer(), client, version)).fetchone()
    if not row:
        return {"error": f"no submitted pack {client} {version}"}
    if approve:
        n = conn.execute("update infographics set status = 'approved' where client = %s and status = 'review'",
                         (client,)).rowcount
        return {"approved": client, "version": version, "backfill_rows_approved": n}
    n = conn.execute("delete from infographics where client = %s and status = 'review'", (client,)).rowcount
    return {"rejected": client, "version": version, "backfill_rows_deleted": n}


def main():
    p = argparse.ArgumentParser(description="Share brand packs via Supabase")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pull")
    sub.add_parser("list").add_argument("--status", choices=["pending", "approved", "rejected"])
    for name in ("submit", "review", "approve", "reject"):
        s = sub.add_parser(name)
        s.add_argument("--client", required=True)
        if name != "submit":
            s.add_argument("--version", required=True)
        if name == "reject":
            s.add_argument("--note", required=True)
    a = p.parse_args()
    with registry.connect() as conn:
        if a.cmd == "pull":
            out = pull(conn)
        elif a.cmd == "list":
            out = list_packs(conn, a.status)
        elif a.cmd == "submit":
            out = submit(conn, a.client)
        elif a.cmd == "review":
            require_admin()
            out = {"installed_for_review": a.client, "files": install(conn, a.client, a.version),
                   "next": "read DESIGN.md + critic_rules.md, render a sample, then approve or reject"}
        else:
            out = decide(conn, a.client, a.version, a.cmd == "approve", getattr(a, "note", None))
    print(json.dumps(out, default=str, indent=1))
    sys.exit(1 if isinstance(out, dict) and "error" in out else 0)


if __name__ == "__main__":
    main()
