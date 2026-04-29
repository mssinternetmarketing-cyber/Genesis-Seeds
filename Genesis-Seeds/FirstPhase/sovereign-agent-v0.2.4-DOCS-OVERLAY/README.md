# Sovereign Agent v0.2.4

**A local, authority-tiered, audited, recoverable autonomous agent — yours.**

---

## What's new in v0.2.4

This version doesn't change agent code. It adds the operational and doctrinal scaffolding the agent needs to be actually usable for the Genesis-Seeds work:

- **`COMMANDS.md`** — comprehensive command reference (the missing manual)
- **`RUNBOOK.md`** — practical operations guide
- **`DISTILLATION_PLAN.md`** — staged plan for Genesis-Seeds distillation work
- **`docs/doctrine/`** — the witnessing-system doctrine the agent operates under
- **`CHANGELOG.md`** — version history through v0.2.4

The agent itself is unchanged from v0.2.3 (88 tests passing, capability-detected thinking, SQLite threading fixed, conftest pure). v0.2.4 is documentation + doctrine.

---

## Why no new features

Be honest about it: at v0.2.3 the agent has 88 passing tests but only Tier 0/1 tools and is loop-prone on multi-step planning. Adding new tools (PDF reader, document distiller) without first making the existing agent **drivable** would just add complexity to something that's hard to use.

v0.2.4 makes the existing agent drivable. v0.3 adds the new tools.

---

## Quick start

```bash
# 1. Extract
tar -xzf sovereign-agent-v0.2.4.tar.gz
cd sovereign-agent-v0.2.4

# 2. Install (if not already done)
pip install -e .

# 3. First-time setup
sovereign init
sovereign doctor

# 4. Read the manual
cat COMMANDS.md       # what commands exist
cat RUNBOOK.md         # how to use them
cat DISTILLATION_PLAN.md   # the Genesis-Seeds work plan
```

---

## Driving the agent — the absolute minimum

If you only remember three commands:

```bash
sovereign doctor                                    # health check
sovereign run --mode oneshot "<concrete goal>"      # do one task
sovereign tail                                      # watch it work
```

Everything else is in `COMMANDS.md`.

---

## What the agent can do at v0.2.4

**Capable:**
- Read filesystem (Tier 0)
- Write files in sandbox (Tier 1)
- Search and embed text
- Distill lessons after each task
- Audit trail with Merkle seals
- Multi-mode operation (oneshot, timed, until, live, busy)

**Not capable yet:**
- Read PDF, DOCX, IPYNB content (text-only at v0.2.4)
- Multi-stage project planning across hundreds of files
- Web browsing with full agency
- Connecting to external apps (no MCP servers)

See `DISTILLATION_PLAN.md` for how this affects the Genesis-Seeds work.

---

## Doctrine

This agent operates under the witnessing-system doctrine. The full doctrine is in `docs/doctrine/`:

- `the_witnessing_system.md` — the soul document
- `witnessing_application_notes.md` — the practice that produced it
- `witnessing_diagnostic_lenses.md` — seven lenses for interrogating perception health
- `witnessing_spec_skeleton.md` — outline for the eventual technical specification
- `peig_as_lens.md` — PEIG framework as computational design language
- `omega_axioms.md` — alignment essay (companion to the witnessing system)
- `omega_explorations_personal.md` — personal vision document

These are not just decoration. They specify what the agent is *for* and what it should *not* do. When extending the agent, refer back to the doctrine — especially `witnessing_diagnostic_lenses.md` for the seven interrogation questions.

---

## Migration from v0.2.3

This is purely additive. No code changes.

```bash
# Backup v0.2.3 (just in case)
cp -r ~/AA-Erebo/sovereign-agent-v0.2.1/sovereign-agent ~/AA-Erebo/sovereign-agent-v0.2.1.bak

# Extract v0.2.4 alongside
cd ~/AA-Erebo
tar -xzf sovereign-agent-v0.2.4.tar.gz
cd sovereign-agent-v0.2.4

# Reinstall (atoms.db, secret.key, configs are preserved)
pip install -e .

# Verify
sovereign doctor
pytest tests/ -q       # should still be 88 passed
```

Your existing `secret.key`, `atoms.db`, events log, and lesson history are unchanged.

---

## Roadmap (honest version)

**v0.3 (next):**
- `distill_document` tool (PDF, DOCX, IPYNB content extraction)
- `distill_repo` tool (multi-file project digestion with structured output)
- `transcribe_video` and `ocr_pdf` tools

**v0.4:**
- Multi-stage project planning (the agent can maintain a plan across many iterations)
- MSIMS matrix emission for Tier 1+ tools (witnessing doctrine implementation begins)

**v0.5+:**
- MCP connector support
- More sophisticated reflector
- Self-evolution protocols (STaR Levels)

---

## Files in this package

```
sovereign-agent-v0.2.4/
├── README.md                     # this file
├── CHANGELOG.md                  # version history
├── COMMANDS.md                   # complete command reference
├── RUNBOOK.md                    # operations guide
├── DISTILLATION_PLAN.md          # Genesis-Seeds staged plan
├── pyproject.toml                # package definition
├── docs/
│   └── doctrine/
│       ├── the_witnessing_system.md
│       ├── witnessing_application_notes.md
│       ├── witnessing_diagnostic_lenses.md
│       ├── witnessing_spec_skeleton.md
│       ├── peig_as_lens.md
│       ├── omega_axioms.md
│       └── omega_explorations_personal.md
├── scripts/
│   ├── bwrap-wrap.sh
│   ├── sovereign-agent-seal.service
│   ├── sovereign-agent-seal.timer
│   └── sovereign-agent.service
├── sql/
│   ├── 001_events.sql
│   └── 002_atoms.sql
├── src/sovereign_agent/          # unchanged from v0.2.3
└── tests/                        # unchanged from v0.2.3, 88 passing
```

---

## License

PolyForm Noncommercial 1.0.0. Same as Genesis-Seeds. See `LICENSE` if bundled, or refer to the parent Genesis-Seeds repo.

---

## Contact

mssinternetmarketing@gmail.com

— Kevin Christian Blake Monette
