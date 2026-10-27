import os
import sys
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skill"))
import registry  # noqa: E402

TOPIC = "How FCC cuts checkout drop-off with one-tap UPI"
ANGLE = "Retailer view: fewer steps, higher conversion"


def test_verdict_rules():
    block, warn = registry.DEDUP["block"], registry.DEDUP["warn"]
    assert registry.verdict([]) == "ok"
    assert registry.verdict([{"sim": block, "status": "approved"}]) == "block"
    assert registry.verdict([{"sim": block, "status": "old_brand"}]) == "block"
    assert registry.verdict([{"sim": (block + warn) / 2, "status": "approved"}]) == "warn"
    assert registry.verdict([{"sim": 0.99, "status": "pending"}]) == "warn"
    assert registry.verdict([{"sim": warn - 0.01, "status": "approved"}]) == "ok"


needs_db = pytest.mark.skipif(not os.getenv("DATABASE_URL"), reason="DATABASE_URL not set")


@pytest.fixture
def db():
    client = f"__pytest_{uuid.uuid4().hex[:8]}"
    with registry.connect() as conn:
        yield conn, client
        conn.execute("delete from infographics where client = %s", (client,))


@needs_db
def test_known_topic_is_blocked(db):
    conn, client = db
    registry.backfill(conn, client, [{"topic": TOPIC, "angle": ANGLE, "layout_type": "vertical_checklist",
                                      "source": "test.png"}])
    res = registry.check(conn, client, TOPIC, ANGLE)
    assert res["verdict"] == "block"
    assert res["matches"][0]["topic"] == TOPIC
    assert res["avoid_layouts"] == ["vertical_checklist"]
    assert "id" not in registry.reserve(conn, client, TOPIC, ANGLE)  # reserve refuses too


@needs_db
def test_duplicate_pending_reservation_warns(db):
    conn, client = db
    first = registry.reserve(conn, client, TOPIC, ANGLE)
    assert first["verdict"] == "ok"
    second = registry.reserve(conn, client, TOPIC, ANGLE)
    assert second["verdict"] == "warn"
    assert second["matches"][0]["id"] == first["id"]
    assert second["matches"][0]["status"] == "pending"
    assert registry.release(conn, second["id"])["released"]


@needs_db
def test_unrelated_topic_is_ok(db):
    conn, client = db
    registry.backfill(conn, client, [{"topic": TOPIC, "angle": ANGLE}])
    assert registry.check(conn, client, "Warehouse robotics for same-day delivery")["verdict"] == "ok"
