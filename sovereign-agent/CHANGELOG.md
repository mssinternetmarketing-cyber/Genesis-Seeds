# Changelog

## v0.2.29.0 — 2026-05-21

The **Integrator**. Three new surfaces that make the v0.2.27.0 and v0.2.28.0 substrate actually reachable: the `retrieve_memory` Tier-0 tool exposes the Sovereign Retrieval Pipeline to the agent loop; the horizon gate fires for Tier-2+ subtasks (Phase 2 of the v0.3.0 roadmap completed — `horizon.generate_for_subtask` produces a 3m/12m/3y/7g projection through the fast model, persists as an atom, attaches `atom_id` to the subtask); and `sov retrieve` is the operator-facing CLI for the pipeline with intent/stakes overrides, bitemporal `--as-known-at`, and a `--no-embed` fast path.

**1213 tests passing** (+26 new). Zero regressions.

See [RELEASE-NOTES-v0_2_29_0.md](RELEASE-NOTES-v0_2_29_0.md) for full notes.

## v0.2.28.0 — 2026-05-21

The **Sovereign Retrieval Pipeline**. A new package `src/sovereign_agent/retrieval/` (six modules: `__init__`, `query`, `recall`, `filter`, `rerank`, `assembly`) implementing a five-stage retrieval pipeline that uses substrate no other production RAG synthesizes end-to-end: bitemporal storage, provenance graph as a recall source, constitutional source-taxonomy filtering, AriaState focus contextualization, 24-channel typing, and source-verified vs LLM-proposed atoms. Returns a witnessed `RetrievalReport` with hits, confidence ceiling, gap report, and concrete expansion hints — never just a list of documents. Cross-encoder and embedder are injected and degrade honestly to RRF when absent.

**1187 tests passing** (+68 new). Zero regressions. The CLI surface (`sov retrieve <query>`) and the embedder/cross-encoder wiring are the next operator-pacing steps; the function-level API is the contract and is stable.

See [RELEASE-NOTES-v0_2_28_0.md](RELEASE-NOTES-v0_2_28_0.md) for the design synthesis (the six novel pieces) and [docs/CLAUDE-TIER-PLAN.md](docs/CLAUDE-TIER-PLAN.md) for the rest of the roadmap.

## v0.2.27.0 — 2026-05-20

The **long-horizon work envelope**. Introduces `agent_session.py` — the persistent multi-step loop that carries a goal across many subtasks, grows its own queue as it learns, pauses cleanly when called, and resumes from disk exactly where it stopped. Also introduces `rollback.py` (Phase 3 of the v0.3.0 roadmap) — pre-staged undo plans for Tier-3 actions, with four generators shipping (file_write, atom_insert, snapshot_create, draft_archive) and the irreversibility doctrine enforced for everything else.

**1119 tests passing** (+79 new: 48 agent_session, 31 rollback). Zero regressions. The CLI sub-app for `sov session` is the next operator-pacing step; the underlying function-level API is the contract and is stable.

See [RELEASE-NOTES-v0_2_27_0.md](RELEASE-NOTES-v0_2_27_0.md) for the full picture, and [docs/CLAUDE-TIER-PLAN.md](docs/CLAUDE-TIER-PLAN.md) for the design plan covering v0.2.28.0 (retrieval reranker — highest leverage) through v0.2.31.0 (eval harness).

## v0.2.14 — 2026-05-10

The **legendary sprint**. Introduces **Aria-Sovereign-V1** (the AI inside the
system), rebuilds memory as a registry of 13 typed channels (financial,
goals, identity, specialist, lessons, ritual, trust, context, personalities,
intention, humor, emotions, intuition), adds a per-project financial ledger
with payments-grade idempotency, an appendix system for markdown documents
attached to atoms, and a first-class MOS Horizon Scan generator.

540 tests passing (+37 new). No data migration. Drop-in over v0.2.13.

See [CHANGELOG-v0.2.14.md](CHANGELOG-v0.2.14.md) for the full picture, and
[ARIA.md](ARIA.md) + [CHANNELS.md](CHANNELS.md) for the architecture docs.

## v0.2.13 — 2026-05-09

The **personality, FOSS, anti-zombie/anti-ghost, validators, edge-case
registry, and modulated memory** release. Adds five new modules
(personas, foss, edge_cases, validators, health, memory_namespaces),
fcntl on dream YAML, idle-cycle auto-pause, anti-syntax/anti-indent
quarantine, and four new top-level CLI commands (`sov status`, `sov
health`, `sov edge-cases`, `sov personas`) plus `sov dream tail` and
`sov dream gc`.

503 tests passing. No data migration required.

See [CHANGELOG-v0.2.13.md](CHANGELOG-v0.2.13.md) for the full picture.

## v0.2.12 — 2026-05-09

Adds the **infinite trillion-dollar software builder** (`sov dream`),
the **plain-English entry point** (`sov do "<sentence>"`), first-class
**pause/resume** at both continuation and dream level, and a **project
scanner** that detects file changes and emits atoms.

See [CHANGELOG-v0.2.12.md](./CHANGELOG-v0.2.12.md) for the full release
notes, [COMMANDS.md](./COMMANDS.md) for the updated command reference,
and [CORPUS_COMPLETION_PLAN.md](./CORPUS_COMPLETION_PLAN.md) for how to
finish the in-flight 1461-file walk.

### Headline additions

- `sov dream start` / `dream advance` / `dream pause` / `dream resume` /
  `dream stop` / `dream list` / `dream show`
- `scripts/sovereign-dream-loop.sh` — outer driver mirroring the existing
  continuation loop
- `sov do "<directive>"` — deterministic plain-English parser; turns
  missing args into interactive prompts; `-y` accepts defaults
- `sov projects scan` / `update` / `list` / `show` / `delete` — named
  directory tracking with sha256 fingerprinting, deterministic
  diff-to-atoms emission
- `sov pause` / `sov resume` — continuation-level primitives
- `sov continuations alias` — friendly names

### Tests

- v0.2.11: 383 → v0.2.12: **435** (+52, all green, ~15s)

### Compat

- Drop-in upgrade. New directories (`dream-sessions/`, `dreams/`,
  `projects/`) created on first use. `paused` continuation status is
  the only schema change; pre-v0.2.12 continuations untouched.

---

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
