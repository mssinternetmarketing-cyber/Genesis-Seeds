# Genesis-Seeds Distillation Plan

**Author:** Kevin Christian Blake Monette (with Claude as planning partner)
**Status:** Plan, v0.1, April 2026
**Purpose:** Stage the Genesis-Seeds distillation work across agent versions, so each phase ships with confidence rather than aspiration.

---

## The honest picture

`~/AA-Erebo/Genesis-Seeds/` contains **1,557 files across 167 directories**. The corpus spans:

- 6 original research repositories (quantum-ai-observer, Quantum-Consciousness, UIC-Quantum-Coherence-Experiments, entropy-gravity-coupling, IndependantQuantumResearchUpdate, PEIG-Brotherhood)
- A `docs/` folder with 30+ whitepapers, papers, and synthesis documents
- A `ConsiderableStartingpoint/` folder with the witnessing-doctrine and PEIG-as-lens documents we just produced
- Hundreds of experiment results (JSON), Python scripts, LaTeX sources, screenshots, and PDFs

**This is too much for v0.2.4 to autonomously distill in one push.** Trying to do so would produce shallow output and mask the agent's real limitations.

The plan below stages the work so:
- v0.2.4 produces **real value** on the parts it can handle
- v0.3 adds the tools needed for the parts it can't yet
- v0.4+ runs the full sweep

The plan is honest about which phase is which.

---

## Phase 1 — Inventory and lineage map (v0.2.4 capable)

**What:** Walk the entire Genesis-Seeds tree, produce a structured inventory document. For each file/folder: name, size, type, one-line purpose if inferable from filename, parent repo if known, modification date.

**Why this is v0.2.4 capable:**
- Pure text-based work (filesystem walking, no PDF/DOCX content extraction)
- Each file is a small task; agent doesn't need to maintain plan across many iterations
- Output is structured and additive (write to growing inventory file)

**Tools used:**
- `list_dir` (read directory contents)
- `read_file` (read .md, .txt, .json, .py source files for purpose extraction)
- `write_file` (build the inventory document incrementally)

**Output:**
- `~/AA-Erebo/Genesis-Seeds/distilled/inventory.md` — full file/folder index
- `~/AA-Erebo/Genesis-Seeds/distilled/lineage_chronological.md` — files ordered by modification date
- `~/AA-Erebo/Genesis-Seeds/distilled/lineage_by_repo.md` — files grouped by source repository

**Estimated time:** 4-8 hours of agent time (with breaks). Run in `--mode timed --minutes 60` chunks.

**How to start it:**
```bash
sovereign run --mode timed --minutes 60 "Walk the directory tree at ~/AA-Erebo/Genesis-Seeds/. For each file, append a line to ~/AA-Erebo/Genesis-Seeds/distilled/inventory.md with format: <relative_path> | <size_bytes> | <extension> | <purpose_hint>. Use list_dir for each subdirectory. For .md, .txt, .py, .json files, read the first 200 bytes to extract a purpose hint. Skip binary files (PDF, PNG, JPG, DOCX). When done with the current subdirectory, move to the next. Stop after 60 minutes regardless of progress."
```

**What can go wrong:**
- The agent may try to read binary files. The instruction explicitly says skip them; if it tries anyway, the read_file tool will return an error and the agent will move on.
- The agent may not know which subdirectory to do next after 60 minutes. Solution: each `--mode timed` run should start with "the next directory to process is X" based on what was completed last time.
- Total file count means full inventory will take multiple sessions. Expect to run this command 6-10 times across days.

---

## Phase 2 — Source-code synthesis for each repo (v0.2.4 partially capable)

**What:** For each of the 6 source repositories, produce a synthesis document covering: purpose, dependencies, key files, experiments run, results obtained, claims made, falsifiability status.

**Why this is partially v0.2.4 capable:**
- Python source files (.py) and JSON results (.json) are text — the agent can read them
- LaTeX sources (.tex) are text — readable
- Markdown files (.md) — readable

**Why this is partially blocked:**
- PDF whitepapers are NOT readable at v0.2.4. The agent will need to skip them or you'll need to extract their text manually first.
- Jupyter notebooks (.ipynb) are JSON-formatted but contain large embedded outputs; the agent may struggle with parse complexity.

**Tools used:**
- `read_file` for .py, .json, .md, .tex
- `list_dir` for navigation
- `write_file` for outputs
- `memory_write` to store atoms about each file as it's processed

**Output (one per source repo):**
- `~/AA-Erebo/Genesis-Seeds/distilled/repos/<repo_name>_synthesis.md`

**How to start it (do one repo at a time):**
```bash
sovereign run --mode timed --minutes 90 "Read every .py and .md file in ~/AA-Erebo/Genesis-Seeds/Genesis-Seed/quantum-ai-observer-main/. For each file, write an atom (memory_write) capturing its purpose. After processing all files, synthesize a report at ~/AA-Erebo/Genesis-Seeds/distilled/repos/quantum-ai-observer_synthesis.md with sections: Purpose, Architecture, Key Experiments, Results Found, Claims Made, Open Questions. Skip all PDF, PNG, JPG files."
```

**Run this 6 times, once per repo:**
1. quantum-ai-observer-main
2. Quantum-Consciousness-main
3. UIC-Quantum-Coherence-Experiments-main
4. entropy-gravity-coupling-main
5. IndependantQuantumResearchUpdate-main
6. PEIG-Brotherhood-main

---

## Phase 3 — Document distillation (BLOCKED until v0.3)

**What:** Read every PDF, DOCX, IPYNB in the corpus and produce a distillation index: title, abstract, key claims, methodology, evidence, falsification status, derivative relationships.

**Why this is blocked:**
- v0.2.4 has no PDF reader, no DOCX reader, no notebook content extractor
- These tools are explicitly planned for v0.3 (`distill_document` and `distill_repo`)

**What unlocks this:**
- v0.3 release with the distillation tools

**Workaround for now:**
- You can manually convert critical PDFs to .md or .txt and put them somewhere the agent can read
- For the highest-priority documents (Critical, Address, FullDoc — the strongest physics papers), this manual conversion is worth doing now

**Output (deferred until v0.3):**
- `~/AA-Erebo/Genesis-Seeds/distilled/documents/<doc_name>_distillation.md`

---

## Phase 4 — Lineage and derivative mapping (v0.2.4 capable, but produces a draft only)

**What:** Build a graph showing which documents derive from which, where ideas first appear, where they're refined, where they're contradicted.

**Why this is v0.2.4 capable as a draft:**
- The agent can read filenames, modification dates, and the source-code synthesis docs from Phase 2
- Atoms accumulated in Phases 1-2 are searchable via `memory_search`
- The agent can draft a lineage map from this metadata

**Why it's only a draft:**
- The full lineage requires understanding document content, which is blocked until Phase 3
- The Phase 4 draft will need refinement once Phase 3 completes

**Tools used:**
- `memory_search` (find related atoms)
- `read_file` (read Phase 1-2 outputs)
- `write_file` (build lineage doc)

**Output:**
- `~/AA-Erebo/Genesis-Seeds/distilled/lineage_draft.md`

**How to start it:**
```bash
sovereign run --mode timed --minutes 60 "Read all files in ~/AA-Erebo/Genesis-Seeds/distilled/. Use memory_search to find related atoms. Build a lineage graph at ~/AA-Erebo/Genesis-Seeds/distilled/lineage_draft.md showing: which documents reference which others, chronological order of major ideas, derivative relationships. Mark sections as DRAFT-INCOMPLETE since PDF content is not yet processable. Stop after 60 minutes."
```

---

## Phase 5 — Priority and value ranking (v0.2.4 capable)

**What:** Rank all distilled materials by: meaningfulness, modularity, integrability, dynamic potential. The output is your roadmap — what to develop first, what to publish first, what to set aside.

**Why this is v0.2.4 capable:**
- It operates on the structured outputs from Phases 1-4
- Ranking is a synthesis task on already-distilled content
- The Witnessing System diagnostic lenses can guide the ranking criteria

**Tools used:**
- `read_file` (read all phase outputs)
- `write_file` (produce ranking)
- `memory_search` (cross-reference with stored atoms)

**Output:**
- `~/AA-Erebo/Genesis-Seeds/distilled/priority_ranking.md`

**How to start it:**
```bash
sovereign run --mode oneshot "Read all files in ~/AA-Erebo/Genesis-Seeds/distilled/. Produce ~/AA-Erebo/Genesis-Seeds/distilled/priority_ranking.md ranking each major work by: meaningfulness (1-10), modularity (how reusable as a piece, 1-10), integrability (how well it connects to other work, 1-10), dynamic potential (how alive/extensible it is, 1-10). For each, give a one-paragraph justification."
```

---

## Phase 6 — Godot simulation prep (BLOCKED until Phases 1-5 complete and v0.3+ available)

**What:** Extract the dynamics, equations, and structural relationships from the corpus into a form that can be implemented as a running simulation in Godot.

**Why this is blocked:**
- Requires the deep distillation that Phase 3 will produce
- Requires v0.3 tools to extract math from PDFs
- Requires Phase 5's ranking to know which dynamics matter most
- Implementation in Godot is a separate project from the distillation work

**What this looks like when ready:**
- `~/AA-Erebo/Genesis-Seeds/godot/dynamics_spec.md` — formal dynamics specification
- `~/AA-Erebo/Genesis-Seeds/godot/data_structures.md` — what state needs representation
- `~/AA-Erebo/Genesis-Seeds/godot/initial_conditions.md` — what to seed the simulation with
- Eventually: actual GDScript / C# implementation

---

## Order of operations — recommended

**This week (v0.2.4):**
1. Run Phase 1 (inventory). Multiple sessions. Get the inventory docs to ~80% complete.
2. Begin Phase 2, one repo at a time. Aim for 2-3 repos this week.

**Next week:**
3. Finish Phase 2 (remaining 3-4 repos)
4. Run Phase 4 (lineage draft) and Phase 5 (priority ranking) using Phase 1-2 outputs

**When v0.3 ships:**
5. Run Phase 3 (document distillation)
6. Refine Phase 4 with full content understanding
7. Refresh Phase 5 ranking with new info

**When Phases 1-5 are complete:**
8. Begin Phase 6 (Godot simulation prep)

---

## Output directory structure

The agent should create and maintain this structure under Genesis-Seeds:

```
~/AA-Erebo/Genesis-Seeds/distilled/
├── inventory.md
├── lineage_chronological.md
├── lineage_by_repo.md
├── lineage_draft.md
├── priority_ranking.md
├── repos/
│   ├── quantum-ai-observer_synthesis.md
│   ├── Quantum-Consciousness_synthesis.md
│   ├── UIC-Quantum-Coherence_synthesis.md
│   ├── entropy-gravity-coupling_synthesis.md
│   ├── IndependantQuantumResearchUpdate_synthesis.md
│   └── PEIG-Brotherhood_synthesis.md
├── documents/                  # populated in Phase 3
└── godot/                       # populated in Phase 6
```

---

## How to monitor progress

**During each run:**
```bash
sovereign tail
```

**After each session:**
```bash
sovereign events -n 50
sovereign lessons -n 10
```

**When you want a status check:**
```bash
ls -la ~/AA-Erebo/Genesis-Seeds/distilled/
wc -l ~/AA-Erebo/Genesis-Seeds/distilled/inventory.md
```

The growing line count of `inventory.md` is your most reliable progress signal.

---

## When to stop and reassess

After Phase 1 produces an initial inventory, **stop and look at it**. Verify:
- File counts match what `find ~/AA-Erebo/Genesis-Seeds -type f | wc -l` shows
- Purpose hints look reasonable (not empty, not hallucinated)
- The format is consistent

If Phase 1 output is bad, fixing the prompts is cheaper than fixing 1500 entries later.

After Phase 2 produces the first repo synthesis, **stop and read it**. Verify:
- The synthesis matches what you actually have in that repo
- Claims attributed to your work are accurate
- No invented results, no hallucinated experiments

If Phase 2 output is bad, refine the prompts before doing the other 5 repos.

The witnessing principle applies here too: **trust the agent only to the degree it has earned trust.** Trust is built one verified output at a time.

---

## Closing

This plan exists so that when you say "go distill Genesis-Seeds," there's a real concrete sequence of agent runs that does meaningful work, rather than one giant prompt that produces vague output.

The v0.2.4 agent can really do Phases 1, 2, 4, and 5. It cannot do Phase 3 yet. It cannot do Phase 6 until much later.

Don't ask it to do what it can't. Ask it to do what it can, well, and ship that.

— end —
