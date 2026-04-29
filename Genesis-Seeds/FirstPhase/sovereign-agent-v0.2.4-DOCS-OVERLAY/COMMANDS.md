# Sovereign Agent — Command Reference

**Version:** v0.2.4
**Status:** Comprehensive command reference. Print this. Keep it visible.

---

## Quick orientation

The `sovereign` CLI controls the entire agent. Everything you do with the agent goes through one of the commands below. There is no other way to drive it. The agent does NOT have a "show me my commands" capability built into the model — when you ask the model that question, it doesn't know, because the commands are part of the CLI wrapper, not the model. **This document is the answer to "what can I run."**

All commands have `--help` available. When in doubt: `sovereign <command> --help`.

---

## Setup commands

### `sovereign init`

**Purpose:** First-time setup. Creates config dir, data dir, sandbox, secret.key, atoms.db.

**Run when:**
- First install
- After a clean wipe
- If `sovereign doctor` shows missing infrastructure

**Example:**
```bash
sovereign init
```

**Idempotent:** Yes. Safe to run multiple times. Will not overwrite an existing `secret.key`.

---

### `sovereign doctor`

**Purpose:** Diagnostic check. Verifies all directories, models, ollama connectivity, bubblewrap availability, VRAM headroom.

**Run when:**
- Anytime something feels off
- Before kicking off long agent sessions
- After upgrading the agent or changing config

**Example:**
```bash
sovereign doctor
```

**Output:** A table with PASS/WARN/FAIL for each check. Read it. WARNs are usually fine; FAILs need fixing before proceeding.

---

## Run commands

### `sovereign run --mode oneshot "<goal>"`

**Purpose:** Single-task execution. The agent attempts the goal, runs to completion (success or failure), distills a lesson, exits.

**Use for:**
- Concrete, scoped tasks ("read /etc/hostname and tell me what it says")
- Smoke tests after upgrades
- Anything where you want one round-trip and done

**Example:**
```bash
sovereign run --mode oneshot "Read ~/AA-Erebo/Genesis-Seeds/canon-seed.md and summarize it in 5 sentences."
```

**Limits at v0.2.4:**
- Best for tasks that fit inside ~5-10 tool calls
- Not designed for tasks requiring multi-document planning across hundreds of files
- The model will sometimes ask for clarification rather than acting; if that happens, rerun with a more specific goal

---

### `sovereign run --mode timed --minutes <N> "<goal>"`

**Purpose:** Time-bounded autonomous execution. The agent works on the goal for up to N minutes, then stops cleanly.

**Use for:**
- Bounded exploration ("look at these 20 files and tell me what's there, you have 30 minutes")
- Overnight or break-time work
- Any task where you want a hard upper bound on cost

**Example:**
```bash
sovereign run --mode timed --minutes 30 "Inventory ~/AA-Erebo/Genesis-Seeds/Genesis-Seed/ConsiderableStartingpoint/. List every file with one-sentence purpose. Stop after 30 minutes."
```

---

### `sovereign run --mode until --condition "<predicate>" "<goal>"`

**Purpose:** Goal-bounded execution. The agent works until a stopping predicate is satisfied.

**Use for:**
- Convergence-style tasks ("keep refining until quality > 0.8")
- Tasks with natural completion criteria

**Example:**
```bash
sovereign run --mode until --condition "all 7 files inventoried" "Inventory each .md file in this folder one by one."
```

**Note:** The predicate is checked by the model itself, which means it's interpretive. Don't use this for tasks where convergence is hard to articulate.

---

### `sovereign run --mode live "<goal>"`

**Purpose:** Persistent autonomous mode. The agent stays alive, drains backlog, reflects, and operates indefinitely until you halt it.

**Use for:**
- The mode you want once you trust the agent on a specific class of work
- Genesis-Seeds distillation, once we've staged the work properly (see DISTILLATION_PLAN.md)
- Long-horizon work where you want continuous progress

**Example:**
```bash
sovereign run --mode live "Distill the corpus per the plan in ~/AA-Erebo/Genesis-Seeds/DISTILLATION_PLAN.md. Process tasks from the backlog one at a time."
```

**Halt with:** `sovereign halt` (graceful) or `sovereign disarm` (immediate).

---

### `sovereign run --mode busy "<goal>"`

**Purpose:** BUSY mode — the agent is currently working and any new approval requests are auto-deferred until the current task settles.

**Use for:**
- Tasks where you don't want to be interrupted with approval prompts
- Sessions where you've pre-staged everything and just want execution

**Example:**
```bash
sovereign run --mode busy "Process the next 10 items in the inventory queue."
```

---

## Backlog and approval commands

### `sovereign backlog`

**Purpose:** Show pending tasks the agent is queued to handle.

**Example:**
```bash
sovereign backlog
```

**Useful for:** Checking what's queued before going live mode, or seeing what's left after a session.

---

### `sovereign approvals`

**Purpose:** List pending approval requests. The agent generates these when it wants to take a Tier 2+ action.

**Example:**
```bash
sovereign approvals
```

---

### `sovereign approve <event_id>`

**Purpose:** Approve a specific pending action.

**Example:**
```bash
sovereign approve 01KQAWXF
```

**Note:** You can use the first 8 characters of the event ID. The system will match unambiguously.

---

### `sovereign deny <event_id>`

**Purpose:** Reject a specific pending action.

**Example:**
```bash
sovereign deny 01KQAWXF
```

---

## Control commands

### `sovereign halt`

**Purpose:** Graceful stop. The agent finishes its current iteration, distills the lesson, then exits.

**Example:**
```bash
sovereign halt
```

**Use this:** Whenever possible. It's the polite way.

---

### `sovereign disarm`

**Purpose:** Immediate stop. The agent is killed mid-iteration. Lessons may not be distilled. Use only when `halt` is too slow.

**Example:**
```bash
sovereign disarm
```

**Triggers PROTOCOL-ZERO** if the agent was doing something dangerous.

---

## Inspection commands

### `sovereign tail`

**Purpose:** Live tail of the events log. Watch what the agent is doing in real time.

**Example:**
```bash
sovereign tail
```

**Use for:** Monitoring during live mode; debugging when something seems wrong.

---

### `sovereign events [-n <count>]`

**Purpose:** Show the last N events. Default is 20.

**Example:**
```bash
sovereign events -n 50
```

**Output columns:**
- `ts` — timestamp
- `flag` — event type (`trace-start-d`, `tool-d`, `reflect-d`, `trace-end-d`, etc.)
- `trace` — trace ID grouping events from one run
- `payload` — JSON details of the event

**Most useful flags to watch:**
- `ingest-d` — agent received a goal
- `plan-d` — agent reasoned about what to do
- `tool-d` — agent invoked a tool
- `reflect-d` — agent distilled a lesson
- `trace-end-d` — run completed

---

### `sovereign lessons [-n <count>]`

**Purpose:** Show recent distilled lessons from the Reflector.

**Example:**
```bash
sovereign lessons -n 10
```

**Use for:** Understanding what the agent has learned. Lessons accumulate in atoms.db and inform future planning.

---

### `sovereign seal`

**Purpose:** Compute and store a Merkle seal of today's events. Cryptographic audit checkpoint.

**Example:**
```bash
sovereign seal
```

**Run:** Daily. There's a systemd timer that does this automatically if you've enabled the unit. Manual seal is for ad-hoc audit checkpoints.

---

### `sovereign verify [--date YYYY-MM-DD]`

**Purpose:** Verify the Merkle seal for a given day's events. Detects tampering.

**Example:**
```bash
sovereign verify --date 2026-04-29
```

**Use for:** Audit work. Should always succeed if the events log hasn't been corrupted.

---

## Configuration

The agent reads config from `~/.config/sovereign-agent/config.toml` and from environment variables that start with `AGENT_`. Environment variables override the config file.

**Common environment variables:**

| Variable | Purpose | Default |
|---|---|---|
| `AGENT_ORCHESTRATOR_MODEL` | Model for planning and tool dispatch | `llama3-groq-tool-use:8b` |
| `AGENT_CODER_MODEL` | Model for code-related tasks | `qwen2.5-coder:7b-instruct-q5_K_M` |
| `AGENT_EMBEDDER_MODEL` | Model for memory embeddings | `nomic-embed-text` |
| `AGENT_REFLECTOR_MODEL` | Model for lesson distillation | `nemotron-3-nano:4b` |
| `AGENT_OLLAMA_HOST` | Ollama API endpoint | `http://localhost:11434` |
| `AGENT_THINK_MODE` | Default `auto` (use thinking when supported) | `auto` |

**Set in your `~/.bashrc`** to make persistent. The current EREBO bashrc already exports the four model variables.

---

## Things the agent CANNOT do at v0.2.4

Be honest about this. Save yourself confusion by knowing the limits.

**Cannot:**
- Plan and execute multi-stage projects across hundreds of files autonomously
- Do work that requires maintaining a project plan in memory across many iterations
- Distill or process complex documents (PDF, DOCX, IPYNB) — the file-reading tools are text-only
- Transcribe video or audio
- Browse the web with full agency (only single-URL `web_fetch` calls)
- Connect to your other apps (no MCP servers configured yet)

**To be added in v0.3:**
- `distill_document` tool (handles PDF, DOCX, IPYNB)
- `distill_repo` tool (multi-file project digestion)
- `transcribe_video` tool
- `ocr_pdf` tool

**What this means for Genesis-Seeds work:** see `DISTILLATION_PLAN.md`. The plan explicitly stages what's possible at v0.2.4 vs. what waits for v0.3.

---

## Quick command cheat sheet

```bash
# First-time / health check
sovereign init
sovereign doctor

# Run a single task
sovereign run --mode oneshot "Your goal here. Stop when done."

# Time-bounded session
sovereign run --mode timed --minutes 60 "Your goal here."

# Live continuous mode
sovereign run --mode live "Process tasks from the backlog."

# Watch what's happening
sovereign tail
sovereign events -n 30
sovereign lessons -n 10

# Approvals for risky actions
sovereign approvals
sovereign approve <id>
sovereign deny <id>

# Stop the agent
sovereign halt        # graceful
sovereign disarm      # immediate

# Audit
sovereign seal
sovereign verify --date 2026-04-29
```

---

## When the agent is not behaving

**Symptom:** "I'll start by listing... [no actual work happens]"
**Cause:** The model is loop-bouncing instead of actually invoking tools.
**Fix:** Make the goal more specific. Replace "list the contents" with "use the list_dir tool on path X". Direct tool invocation guidance helps llama3-groq stay on task.

**Symptom:** Tasks hang for minutes with no progress
**Cause:** Often the orchestrator is stuck retrying a failed tool call.
**Fix:** `sovereign tail` to see what's happening; `sovereign halt` to stop; rerun with more specific guidance.

**Symptom:** "I need to know X" when X is obvious from context
**Cause:** llama3-groq is conservative about assuming context.
**Fix:** Restate the goal with the implicit context made explicit. The model is not trying to be obtuse; it's just being literal.

**Symptom:** Model responds without calling any tools
**Cause:** Model decided the task is conversational. This happens with vague goals.
**Fix:** Goals should have action verbs ("read X", "write Y to Z", "search for ABC in folder DEF") rather than questions.

---

## Closing

This is the v0.2.4 command surface. It's complete for what the agent currently is. As v0.3 adds tools, this document will be extended.

When you don't know what to do, the answer is almost always one of:
1. `sovereign doctor` — verify infrastructure
2. `sovereign tail` — see what's happening
3. `sovereign run --mode oneshot "<more specific goal>"` — try again with sharper framing

That's the whole interface. Print it. Stop asking the model. <3
