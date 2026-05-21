"""Events durability tests. Architecture §8a.

Verifies:
  - emit_event appends to events.jsonl
  - tail_to_sqlite ingests JSONL into the SQLite projection
  - Re-running tail is idempotent (no duplicate rows)
  - JSONL is the source of truth: drop SQLite events table, rebuild from JSONL
"""
from __future__ import annotations

import json

from sovereign_agent.config import SETTINGS
from sovereign_agent.events import (
    emit_event,
    force_fsync,
    init_events_db,
    tail_to_sqlite,
)


def test_emit_appends_to_jsonl():
    eid = emit_event(
        "test-d", plane="control", trace_id="t1", payload={"k": "v"}
    )
    force_fsync()
    path = SETTINGS.paths.events_jsonl
    assert path.exists()
    lines = path.read_text().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["event_id"] == eid
    assert rec["flag"] == "test-d"
    assert rec["payload"] == {"k": "v"}


def test_tail_ingests_into_sqlite():
    e1 = emit_event("a-d", plane="control", trace_id="t1")
    e2 = emit_event("b-d", plane="tool", trace_id="t1")
    force_fsync()

    conn = init_events_db()
    inserted = tail_to_sqlite(conn)
    assert inserted >= 2

    rows = conn.execute(
        "SELECT event_id, flag FROM events ORDER BY event_id"
    ).fetchall()
    ids = [r[0] for r in rows]
    flags = [r[1] for r in rows]
    assert e1 in ids
    assert e2 in ids
    assert "a-d" in flags
    assert "b-d" in flags


def test_tail_is_idempotent():
    emit_event("once-d", plane="control", trace_id="t-idem")
    force_fsync()
    conn = init_events_db()

    n1 = tail_to_sqlite(conn)
    # Re-running tail without new events should insert zero new rows
    # (cursor advanced last time)
    n2 = tail_to_sqlite(conn)
    assert n2 == 0
    # And no duplicate rows
    count = conn.execute(
        "SELECT COUNT(*) FROM events WHERE flag='once-d'"
    ).fetchone()[0]
    assert count == 1


def test_rebuild_from_jsonl_after_dropping_table():
    emit_event("survive-d", plane="control", trace_id="t-rebuild")
    force_fsync()
    conn = init_events_db()
    tail_to_sqlite(conn)
    # Wipe the SQLite projection
    conn.execute("DELETE FROM events")
    conn.execute("DELETE FROM ingest_cursor")
    # Rebuild from JSONL
    inserted = tail_to_sqlite(conn)
    assert inserted >= 1
    count = conn.execute(
        "SELECT COUNT(*) FROM events WHERE flag='survive-d'"
    ).fetchone()[0]
    assert count == 1


def test_partial_trailing_line_does_not_corrupt_ingest():
    """If the JSONL has a partial trailing line (e.g., write interrupted),
    tail_to_sqlite must stop cleanly and not advance past it."""
    emit_event("clean-d", plane="control", trace_id="t-partial")
    force_fsync()
    # Append a deliberately broken trailing line
    path = SETTINGS.paths.events_jsonl
    with path.open("ab") as f:
        f.write(b'{"event_id": "broken", "flag": "incomplete-')  # no newline, no closing brace

    conn = init_events_db()
    # Should ingest the good line but stop at the broken one
    n = tail_to_sqlite(conn)
    assert n >= 1
    count = conn.execute(
        "SELECT COUNT(*) FROM events WHERE flag='clean-d'"
    ).fetchone()[0]
    assert count == 1
    # The broken record must NOT have been inserted
    bad = conn.execute(
        "SELECT COUNT(*) FROM events WHERE event_id='broken'"
    ).fetchone()[0]
    assert bad == 0
