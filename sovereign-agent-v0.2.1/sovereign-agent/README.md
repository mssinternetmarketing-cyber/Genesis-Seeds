```
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                  ◈  S O V E R E I G N   A G E N T  ◈                     ║
║                                                                          ║
║         A self-owned 24/7 agent. Local models. No cloud. No leash.       ║
║         Authority-tiered. Audited. Recoverable. Yours.                   ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

A reference implementation of [`sovereign_local_agent_architecture_v1.1.md`](sovereign_local_agent_architecture_v1.1.md).
Runs entirely on your hardware against a local Ollama. FOSS-only.

> **Sovereignty here is yours, not the agent's.** The agent runs as your
> deputy on your machine: read what it needs, write to its sandbox, learn
> in durable memory — all without asking. Anything that touches the world
> beyond the sandbox (Tier 2/3) is gated by you. The gates exist to
> protect your sovereignty over the machine, not to hobble the agent.

---

## What this is

A working agent loop with:

| Component                     | Status   | Where                                             |
| :---------------------------- | :------- | :------------------------------------------------ |
| Authority tiering 0–3         | ✓ done   | `authority.py`, enforced inline in `loop.py`      |
| Mode matrix BUSY/ONESHOT/…    | ✓ done   | `modes.py` + `_check_budget` in loop              |
| PROTOCOL-ZERO killswitch      | ✓ done   | `protocol_zero.py`, signal + sentinel file        |
| bwrap sandbox (mode-aware ro) | ✓ done   | `sandbox.py` + `scripts/bwrap-wrap.sh`            |
| HMAC approval tokens (Tier 3) | ✓ done   | `approval.py` + `cli.py:approve/deny`             |
| Path scope guard              | ✓ done   | `pathguard.py`, called from loop & Tier-1 tools   |
| Ollama client w/ think gating | ✓ done   | `ollama_client.py`                                |
| Tier-0 read tools             | ✓ done   | `tools/{read_file, list_dir, search_text, …}`     |
| **Tier-1 write tools**        | ✓ **new**| `tools/{write_file, edit_file, copy_file}`        |
| **Memory write + search**     | ✓ **new**| `tools/{memory_write, memory_search}`             |
| **Atom versioning chain**     | ✓ **new**| `memory/atom.py` (append-only, head-of-chain)     |
| **Hybrid retrieval (RRF)**    | ✓ **new**| `memory/retrieval.py` (vec + FTS5)                |
| **Reflector → Lessons**       | ✓ **new**| `reflector.py`, fires on settle/poison            |
| **Mode Controller**           | ✓ **new**| `mode_controller.py` — drains backlog forever     |
| **Daily Merkle seals**        | ✓ **new**| `seal.py` + `scripts/sovereign-agent-seal.timer`  |
| **AST code gate**             | ✓ **new**| `code_gate.py` (ported from `mos_safety`)         |
| **VRAM accounting**           | ✓ **new**| `vram.py` (ported from `mos_vram`)                |
| **systemd user units**        | ✓ **new**| `scripts/sovereign-agent.service`                 |
| **CLI with rich UX**          | ✓ **new**| `cli.py` — banner, tables, panels                 |
| Document/repo distillers      | ⏸ later  | needs `[distill]` extra; planned v0.3             |
| `transcribe_video`/`ocr_pdf`  | ⏸ later  | scaffolded under `[media]` extra; planned v0.3    |
| Bug bounty harness            | ⏸ paused | per operator instruction — until program approved |

---

## Install

```bash
git clone <your-fork-url> sovereign-agent
cd sovereign-agent

# ── Python venv ───────────────────────────────────────────────────────
python3 -m venv ~/.local/share/sovereign-agent/venv
source ~/.local/share/sovereign-agent/venv/bin/activate
pip install -e ".[dev]"

# ── Ollama models ─────────────────────────────────────────────────────
# Orchestrator (8B) + coder + embedder + reflector
ollama pull qwen3:8b
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text
ollama pull phi-4-mini

# ── Bootstrap ─────────────────────────────────────────────────────────
sovereign init        # generates HMAC secret, creates dirs, opens DBs

# ── Verify ────────────────────────────────────────────────────────────
pytest tests/ -q
```

If you want long-running media tools later:

```bash
pip install -e ".[media]"   # faster-whisper, easyocr, PyMuPDF
```

---

## Usage

### 1. Single task

```bash
sovereign run "Summarize ~/notes/project-foo.md and write an atom"
sovereign run --mode busy "Catalog all .py files in ~/code/myproject"
```

### 2. Backlog-driven 24/7 work

```bash
sovereign backlog add "Read ~/papers/*.pdf and write atoms" --priority high
sovereign backlog add "Update README in sandbox/myproject"  --priority medium
sovereign backlog list

sovereign busy        # drain forever; only PROTOCOL-ZERO stops it
```

In a separate shell — observe:

```bash
sovereign events -n 30
sovereign lessons -n 10
sovereign tail        # ingest events.jsonl into the SQLite projection
```

### 3. Tier-3 approval flow

When the agent needs to do something Tier 3 (push to a remote, write
outside sandbox), it emits an `approval-needed-d` event and refuses the
call. You review:

```bash
sovereign approvals
```

```
╭─ ◈ 01J9... ─────────────────────────────────────────────────────────────╮
│ tool:      git_push                                                     │
│ requested: 2026-04-27T14:20:11.402Z                                     │
│ expires:   2026-04-27T14:25:11.402Z                                     │
│ args:      {"remote": "origin", "branch": "main"}                       │
│ reason:    deliver the agent's daily summary to the operator's repo     │
│                                                                         │
│ grant:  sovereign approve 01J9...                                       │
│ deny:   sovereign deny 01J9...                                          │
╰─────────────────────────────────────────────────────────────────────────╯
```

```bash
sovereign approve 01J9...     # writes one-shot HMAC grant token
# or
sovereign deny 01J9... --reason "wrong remote"
```

The grant is bound to the exact `(tool_name, args_hash, expiry_ts)` —
you cannot accidentally approve a different request.

### 4. Audit & seals

```bash
sovereign seal                  # compute yesterday's Merkle root
sovereign verify 2026-04-26     # verify a past seal still matches
```

A daily systemd timer can do this for you (see *Run as a service*).

### 5. Halt

```bash
sovereign halt --reason "thermals climbing"
# … investigate …
sovereign disarm
```

`PROTOCOL-ZERO` can also be tripped from anywhere by writing the sentinel
file: `echo "$reason" > ~/.config/sovereign-agent/HALT`.

### 6. Diagnose

```bash
sovereign doctor
```

Walks through paths, permissions, models, Ollama reachability, bubblewrap,
PROTOCOL-ZERO state, and VRAM. Color-coded output. Run this any time
something feels off — does no writes; safe even with the agent running.

---

## Run as a service (systemd user unit)

```bash
mkdir -p ~/.config/systemd/user
cp scripts/sovereign-agent.service       ~/.config/systemd/user/
cp scripts/sovereign-agent-seal.service  ~/.config/systemd/user/
cp scripts/sovereign-agent-seal.timer    ~/.config/systemd/user/

systemctl --user daemon-reload
systemctl --user enable --now sovereign-agent.service
systemctl --user enable --now sovereign-agent-seal.timer

journalctl --user -u sovereign-agent -f         # tail
systemctl --user list-timers                    # confirm seal timer
```

The unit runs `sovereign busy --cooldown 5` with `MemoryMax=4G`,
`CPUQuota=80%`, `Restart=on-failure`, and a 5-failures-in-60s rate limit.
Adjust `scripts/sovereign-agent.service` to your preferences.

---

## How the Mode Controller behaves in BUSY

```
read backlog.yaml
     │
     ├─ pending task? ──► run agent_loop(mode=task.mode, budget=...)
     │                       │
     │                       ├─ settle  ─► mark "done"   ─► reflect ─► sleep cooldown
     │                       ├─ poison  ─► mark "poison" ─► reflect ─► sleep cooldown
     │                       ├─ budget  ─► mark "budget" ─►            sleep cooldown
     │                       └─ halted  ─► PROTOCOL-ZERO ─► EXIT
     │
     └─ no pending? ────► sleep empty_backlog_sleep
```

Reflection is best-effort — a malformed Reflector response logs `reflect-x`
and continues, never blocking the loop. Lessons accumulate in `atoms.db`
and are queryable via `sovereign lessons`.

---

## Doctrine reference

This is the short version — the long form is in
[`sovereign_local_agent_architecture_v1.1.md`](sovereign_local_agent_architecture_v1.1.md).

- **§7 tier matrix** — every tool has a tier; modes have ceilings; the
  loop refuses tools above the ceiling at the gate, not at the sandbox.
- **§7a approval tokens** — Tier 3 grants are HMAC-SHA256 over
  `event_id|args_hash|expiry_ts`, one-shot (consumed by unlink), 5-minute
  default expiry.
- **§8a events** — `events.jsonl` is the source of truth; the SQLite
  `events` table is a rebuildable projection. Daily Merkle seals over the
  JSONL give tamper-evidence.
- **§12 sandbox** — bwrap with mode-conditional binding: `--ro-bind` in
  BUSY (sandbox dir as the only writable surface), `--bind` in ONESHOT.

---

## What v0.2 deliberately doesn't have

- **Self-modifying core** — explicitly out of scope. The architecture
  doesn't permit the agent to edit its own source. Future capabilities
  are added by you, in code, with PRs.
- **Auto-evolution gates** — no `mos_evolution`-style "AI grades AI's
  rubric" loops. If a behavior change is needed, it's a code change.
- **Bug bounty harness** — paused per operator instruction until the
  program is approved.
- **Distillation pipelines** (`distill_document`, `distill_repo`) and
  **media tools** (`transcribe_video`, `ocr_pdf`) — the dependencies are
  in `pyproject.toml` extras and the architecture has the contract
  worked out, but the tool implementations land in v0.3.

---

## Layout

```
sovereign-agent/
├─ pyproject.toml                          version 0.2.0; +rich, +media extra
├─ sovereign_local_agent_architecture_v1.1.md
├─ sql/
│  ├─ 001_events.sql                        events.db schema + ingest cursor
│  └─ 002_atoms.sql                         atoms + lessons + seals + vec/fts
├─ scripts/
│  ├─ bwrap-wrap.sh                         the bubblewrap shim
│  ├─ sovereign-agent.service               long-running BUSY mode unit
│  ├─ sovereign-agent-seal.service          daily seal oneshot
│  └─ sovereign-agent-seal.timer            00:05 UTC daily
├─ src/sovereign_agent/
│  ├─ __init__.py                           banner + version
│  ├─ config.py        modes.py             paths/settings; mode/budget types
│  ├─ authority.py     approval.py          tier matrix; HMAC approval tokens
│  ├─ protocol_zero.py pathguard.py         killswitch; path scope
│  ├─ sandbox.py       ollama_client.py     bwrap; chat/embed/think gating
│  ├─ db.py            events.py            SQLite + sqlite-vec; events I/O
│  ├─ code_gate.py     vram.py              AST gate; VRAM accounting
│  ├─ reflector.py     seal.py              lesson distillation; Merkle seals
│  ├─ mode_controller.py                    long-running orchestration
│  ├─ loop.py                               THE agent loop — read top-to-bottom
│  ├─ cli.py                                operator surface (typer + rich)
│  ├─ memory/                               atoms, hybrid retrieval
│  └─ tools/                                read/write/memory/web tools
└─ tests/
   ├─ test_pathguard.py                     scope violations + symlink escapes
   ├─ test_authority.py                     tier ceiling refusals
   ├─ test_approval.py                      HMAC binding, one-shot consume
   ├─ test_events.py                        JSONL/SQLite projection idempotence
   ├─ test_atom_versioning.py               extend preserves parent + chain walk
   ├─ test_code_gate.py                     forbidden patterns blocked
   └─ test_seal.py                          Merkle tamper detection
```

---

## License

MIT. Yours to fork, run, and modify.
