"""Event log — architecture §8a.

Contract:
  events.jsonl is the durable source of truth.
  The SQLite events table is a derived projection, rebuilt by tail_to_sqlite().

Write path:
  emit_event(...) -> ULID -> JSON -> O_APPEND to today's events.jsonl -> batched fsync().

Read paths:
  Hot path:  query SQLite events table (after tail-consumer has caught up).
  Audit:     read events.jsonl directly. JSONL wins on disagreement.
"""
from __future__ import annotations

import contextlib
import json
import os
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ulid import ULID

from .config import SETTINGS

_LOCK = threading.Lock()
_PENDING_FSYNC = 0
_LAST_FSYNC_AT = 0.0


def _utc_now_rfc3339() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def emit_event(
    flag: str,
    *,
    plane: str,
    trace_id: str,
    parent_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> str:
    """Append one event to events.jsonl. Returns the event ULID.

    Atomicity guarantee:
      O_APPEND is atomic for writes < PIPE_BUF (4096 bytes on Linux).
      Payloads larger than SETTINGS.event_max_inline_bytes are written to the blob
      store and the event references the blob hash instead of inlining.
    """
    global _PENDING_FSYNC, _LAST_FSYNC_AT
    payload = payload or {}
    event_id = str(ULID())
    record = {
        "event_id": event_id,
        "ts": _utc_now_rfc3339(),
        "flag": flag,
        "plane": plane,
        "trace_id": trace_id,
        "parent_id": parent_id,
        "payload": payload,
    }
    line = _canonical_json(record)
    if len(line.encode("utf-8")) > SETTINGS.event_max_inline_bytes:
        # Spill payload to blob store; replace with reference.
        blob_hash = _spill_to_blobs(payload)
        record["payload"] = {"_blob_ref": blob_hash}
        line = _canonical_json(record)

    line += "\n"
    encoded = line.encode("utf-8")
    path = SETTINGS.paths.events_jsonl

    with _LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("ab") as f:
            f.write(encoded)
            _PENDING_FSYNC += 1
            now = time.monotonic()
            if (
                _PENDING_FSYNC >= SETTINGS.event_fsync_every_n
                or (now - _LAST_FSYNC_AT) >= SETTINGS.event_fsync_every_seconds
            ):
                f.flush()
                os.fsync(f.fileno())
                _PENDING_FSYNC = 0
                _LAST_FSYNC_AT = now

    return event_id


def force_fsync() -> None:
    """Force-flush pending events. Call before clean shutdown."""
    global _PENDING_FSYNC, _LAST_FSYNC_AT
    with _LOCK:
        path = SETTINGS.paths.events_jsonl
        if path.exists():
            with path.open("ab") as f:
                f.flush()
                os.fsync(f.fileno())
        _PENDING_FSYNC = 0
        _LAST_FSYNC_AT = time.monotonic()


def _spill_to_blobs(payload: dict[str, Any]) -> str:
    """Content-addressed blob storage for oversized event payloads."""
    import hashlib

    data = _canonical_json(payload).encode("utf-8")
    h = hashlib.sha256(data).hexdigest()
    blob_path = SETTINGS.paths.blobs_dir / h[:2] / h[2:]
    blob_path.parent.mkdir(parents=True, exist_ok=True)
    if not blob_path.exists():
        # Atomic write
        tmp = blob_path.with_suffix(".tmp")
        tmp.write_bytes(data)
        tmp.replace(blob_path)
    return h


# ─── Tail consumer: JSONL → SQLite events projection ────────────────────────


def init_events_db() -> sqlite3.Connection:
    """Open events.db with the schema from sql/001_events.sql applied."""
    conn = sqlite3.connect(SETTINGS.paths.events_db, isolation_level=None)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    schema = (Path(__file__).parent.parent.parent / "sql" / "001_events.sql").read_text()
    conn.executescript(schema)
    return conn


def tail_to_sqlite(conn: sqlite3.Connection, *, jsonl_path: Path | None = None) -> int:
    """Idempotently ingest events.jsonl into SQLite. Returns count inserted.

    Resume semantics: ingest_cursor.last_byte_offset tells us where we left off.
    INSERT OR IGNORE on event_id PRIMARY KEY makes re-ingest of overlap a no-op.
    """
    jsonl_path = jsonl_path or SETTINGS.paths.events_jsonl
    if not jsonl_path.exists():
        return 0

    cursor = conn.execute(
        "SELECT last_byte_offset FROM ingest_cursor WHERE id = 1"
    ).fetchone()
    offset = cursor[0] if cursor else 0

    inserted = 0
    with jsonl_path.open("rb") as f:
        f.seek(offset)
        for raw in f:
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError:
                # Partial line at tail — stop here, will retry on next pass
                break
            try:
                cur = conn.execute(
                    "INSERT OR IGNORE INTO events "
                    "(event_id, ts, flag, plane, trace_id, parent_id, payload) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        rec["event_id"],
                        rec["ts"],
                        rec["flag"],
                        rec["plane"],
                        rec["trace_id"],
                        rec.get("parent_id"),
                        _canonical_json(rec.get("payload", {})),
                    ),
                )
                # rowcount is the actual number of rows affected by THIS statement
                # (1 if inserted, 0 if the IGNORE clause matched a duplicate).
                inserted += cur.rowcount if cur.rowcount > 0 else 0
            except (KeyError, sqlite3.Error):
                continue
        new_offset = f.tell()

    now = _utc_now_rfc3339()
    conn.execute(
        "INSERT INTO ingest_cursor (id, last_byte_offset, updated_at) VALUES (1, ?, ?) "
        "ON CONFLICT(id) DO UPDATE SET last_byte_offset = excluded.last_byte_offset, "
        "updated_at = excluded.updated_at",
        (new_offset, now),
    )
    return inserted


@contextlib.contextmanager
def trace(trace_id: str | None = None):
    """Context manager that yields a trace_id; emits start-d / end-d bookends."""
    tid = trace_id or str(ULID())
    start_id = emit_event("trace-start-d", plane="control", trace_id=tid)
    try:
        yield tid
    finally:
        emit_event("trace-end-d", plane="control", trace_id=tid, parent_id=start_id)
