# Changelog

## v0.2.3 — 2026-04-28

First end-to-end task succeeded but trace revealed a per-task ~8s wasted
iteration: every model call went out with `think=true` (per `plan_only`
policy), and `llama3-groq-tool-use:8b` doesn't support thinking — Ollama
returned 400. Loop recovered gracefully (recorded `model-x`, retried)
but burned cycles and risked false-positive poison if combined with real
errors.

### Fixed

- **`ollama_client.py` capability detection** — queries `/api/show` per
  model, caches per-instance, sends `think=true` only when both (a) the
  operator's policy wants thinking AND (b) the model advertises the
  ``thinking`` capability. No code config required; the agent adapts to
  whatever models are wired up.
- **`loop.py` poison counter** — capability/HTTP-400 errors are
  classified as `model-config-x` and don't count against
  `consecutive_fails`. Real transient errors still do.

### Added

- **`tests/test_ollama_client.py`** (7 tests) — capability detection
  enables/disables thinking correctly per model, cache prevents repeated
  queries, failed `/api/show` falls back to broadest capabilities, plan
  vs dispatch call kinds respect policy.
- **`sovereign doctor`** now reports per-model thinking capability with
  PASS/WARN colors.

### Test count

- v0.2.2: 81 tests
- v0.2.3: 88 tests, all passing in ~8s

---

## v0.2.2 — 2026-04-28

Reflector hit a SQLite same-thread error on first end-to-end run. The
v0.2.1 code opened the atoms.db connection in one worker thread (via
`asyncio.to_thread`) and used it from the calling coroutine. SQLite's
default same-thread guard refused.

### Fixed

- **`reflector.py`**: connection lifecycle now stays inside one worker
  thread. The `reflect()` function opens, writes, and closes the
  atoms.db connection inside a single `asyncio.to_thread(_write_lesson)`
  block — no cross-thread connection use.
- **`loop.py:_run_reflector`**: simplified — no longer pre-opens a
  connection. Just calls `reflect()` directly. Removed the unused
  `open_atoms_db` import.

### Added

- **`tests/test_reflector.py`** (5 tests) — regression test for the
  threading bug, plus malformed-JSON handling, schema-violation
  resilience, confidence clamping, and code-fence stripping.

### Test count

- v0.2.1: 76 tests
- v0.2.2: 81 tests, all passing in ~8s

---

## v0.2.1 — 2026-04-28

Test harness was broken in v0.2: 14 of 32 tests failed because the conftest
fixture reloaded modules between tests. This created two stale-reference
bugs — production code itself was correct.

### Fixed

- **conftest.py rewrite (root cause fix)**. Replaced module reloading with
  in-place mutation of `SETTINGS.paths` via `object.__setattr__`. Avoids
  the class-identity drift that broke `pytest.raises(AuthorityViolation)`,
  the stale `SETTINGS` references that broke pathguard/events/seal tests,
  and the cumulative tool registry contamination across tests.
- **`reflector.py`** now uses `SETTINGS.reflector_model` instead of
  `SETTINGS.orchestrator_model`. The lightweight Reflector should run on
  the small fast model, not the orchestrator.

### Added

- **`config.py` env-var support** for all model selections —
  `AGENT_ORCHESTRATOR_MODEL`, `AGENT_CODER_MODEL`, `AGENT_EMBED_MODEL`,
  `AGENT_REFLECTOR_MODEL`, `AGENT_FAST_MODEL`. Set in your shell rc to
  override the defaults without editing source.
- **`reflector_model` field** in `Settings` (was missing in v0.2).
- **`sovereign doctor` command** — diagnostic check covering paths,
  permissions, models, Ollama reachability, model availability, bwrap,
  PROTOCOL-ZERO state, and VRAM. Run any time something feels off.
- **`tests/test_mode_controller.py`** (13 tests) — backlog read/write
  round-trip, priority ordering, status-aware task picker, atomic write,
  malformed YAML resilience.
- **`tests/test_retrieval.py`** (9 tests) — RRF fusion math including the
  classic compromise-candidate property, vector serialization roundtrip,
  pinning the standard k=60 constant.
- **`tests/test_vram.py`** (8 tests) — heavy-tool VRAM gating, file-lock
  serialization across threads, lock-timeout behavior.

### Test count

- v0.2:    32 tests defined, 14 failing → effectively no working coverage
- v0.2.1:  76 tests, all passing in ~7 seconds, three runs verified stable
