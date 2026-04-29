# v0.3.0 — Continuation Architecture

**Released:** April 29, 2026
**Type:** Major architectural extension. Additive — no existing v0.2.3 code changes.

## The shape of the change

v0.2 made the agent loop work. v0.3 makes it possible for the agent to do work
*it could never do before*: long-running corpus-scale tasks where the plan
doesn't fit in a single model context.

The new pattern: **Python iterates externally; the model handles one tiny task
per invocation; a state file remembers where we left off.**

## What's new

### Core modules

**`continuation.py`** — durable state file with atomic writes (tempfile + rename),
file locking via `fcntl`, and a transactional API that holds the lock across
read-modify-write cycles. Schema-versioned. Survives crashes mid-write without
corruption.

**`tool_templates.py`** — compact templates that bind a queue item to a single
agent goal. Three templates ship at v0.3.0:
- `inventory_file` — append one line to an output file per queue item
- `read_summary` — read a text file, write a 2-sentence summary
- `atom_from_file` — read a text file, store a memory atom describing it

Templates render goals like *"You are processing entry 47 of 1557. The path is X.
Call write_file with these exact arguments. Stop."* — concrete enough that
llama3-groq-tool-use:8b can complete reliably.

**`continue_mode.py`** — `ContinueModeRunner` that:
1. Reads the continuation under transaction
2. Advances the queue
3. Renders the template
4. Dispatches to the existing agent loop
5. Settles success or marks retry on failure
6. Exits

The model only ever sees one tiny goal. The continuity is in the file.

**`planner/`** — pure-code goal decomposition. Walks the filesystem
deterministically; produces sorted, filtered queues; no model calls. Three
recipes ship at v0.3.0:
- `plan_inventory` — one line per file
- `plan_atoms` — atom per text file
- `plan_summaries` — summary per markdown/text file

### CLI commands

- `sovereign plan inventory ROOT --output FILE` — produce an inventory plan
- `sovereign plan atoms ROOT` — produce a memory-atom plan
- `sovereign plan summaries ROOT --output FILE` — produce a summary plan
- `sovereign continue` — run one step, exit
- `sovereign queue status` — show progress
- `sovereign queue peek -n N` — show next N items
- `sovereign queue reset` — wipe and start over

### Driver script

**`scripts/sovereign-continue-loop.sh`** — drains the queue with circuit-breaker
on consecutive failures, configurable iteration/wall budgets, full event logging.

## Tests

59 new tests, all passing:
- 19 in `test_continuation.py` (atomicity, locking, transactions, schema versioning)
- 18 in `test_planner.py` (filesystem walks, filtering, plan correctness)
- 11 in `test_continue_mode.py` (runner with mocked agent, retries, crash safety)
- 8 in `test_tool_templates.py` (template rendering, registry)

After integration: **147 tests passing total** (88 existing + 59 new).

## Known limits at v0.3.0

- Templates are text-only. PDF, DOCX, and IPYNB content can't be processed yet.
  These need `distill_document` (deferred to v0.3.1+).
- Retry counts live in process memory, not persisted across loop restarts.
  A stuck item gets fresh retries each loop session — possibly indefinitely.
  Persisting retry state to the continuation file is a v0.3.1 cleanup.
- The `--mode continue` integration with the existing CLI requires a small edit
  to `cli.py`. See `INTEGRATION_NOTES.md`.
- `run_agent_for_continuation` in `loop.py` is a thin adapter that needs to
  be pointed at your existing run-loop entry point. See `INTEGRATION_NOTES.md`.

## Migration

This is purely additive over v0.2.3. Your existing config, atoms.db, secret.key,
and 88 tests are untouched. Follow `INTEGRATION_NOTES.md` for the splice steps.

## Why this is the right architecture

The previous approach asked the model to maintain plans across iterations. It
couldn't, because llama3-groq-tool-use:8b is an 8B-parameter tool-calling model,
not a planning engine. v0.3.0 stops asking the model to plan.

The continuation file is the plan. The Python loop is the executor. The model
is the worker.

This is the same pattern that makes Claude Code work, that makes any long-running
autonomous system work: **state-file checkpointing + bounded sub-tasks + external
loop**. It's not novel; it's the right shape.

What's specific to *your* sovereign agent is the integration with the existing
authority tiers, audit trail, Knowledge Atom storage, and PROTOCOL-ZERO killswitch.
All of those continue to function exactly as before. The continuation pattern
sits on top of the v0.2 architecture, not in place of it.
