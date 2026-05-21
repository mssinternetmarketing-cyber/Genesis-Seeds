# Archive

Historical context for the sovereign-agent project. Nothing here is loaded by the running system; this is for reference, recovery, and provenance.

## Layout

```
Archive/
├── README.md            ← you are here
├── tarballs/            ← milestone source snapshots (one per significant release)
└── notes/               ← philosophy & scratch docs that predate the current tree
```

## tarballs/

One snapshot per architecturally significant milestone, not every micro-release. The full per-release history lives in `sovereign-agent/docs/history/` (changelogs and release notes) and in your local git history. Tarballs are kept here only so you can `tar xzf` a past tree if you ever need to bisect a regression in code that isn't in git, or want to compare two versions side by side without checking out branches.

| Tarball | Why it's kept |
|---|---|
| `sovereign-agent-v0.2.5.tar.gz` | First stewardship release — the moment the system grew a self-audit surface |
| `sovereign-agent-v0.2.10.tar.gz` | Palace landing — long-form retrieval became real |
| `sovereign-agent-v0.2.14.4.tar.gz` | Quality-gate maturity — QA harness, edge cases, validators |
| `sovereign-agent-v0.2.15.3.tar.gz` | Cockpit + perception start — the home gained a face |
| `sovereign-agent-v0.2.18.1.tar.gz` | "The home gets architecture" — 5 new channels, migration framework, constitution |
| `sovereign-agent-v0.2.21.0.tar.gz` | The inversion — interpreter degrades honestly when Ollama is offline |
| `sovereign-agent-v0.2.25.0.tar.gz` | Previous stable — the release immediately before current |
| `sovereign-agent-v0.2.26.zip` | Current — same source as the `sovereign-agent/` tree at this level |

Every intermediate version (v0.2.14.1/.2/.3, v0.2.15.0/.1/.2, v0.2.18.2/.3/.4/.5/.6, v0.2.20, v0.2.23, v0.2.22, v0.2.24, etc.) is documented in `sovereign-agent/docs/history/CHANGELOG-vX.Y.Z.md` and `sovereign-agent/docs/history/RELEASE-NOTES-vX.Y.Z.md`. If you need the actual source for one of those, restore from git, not from this folder.

## notes/

| File | What it is |
|---|---|
| `the_witnessing_system.md` | Kevin Christian Blake Monette's philosophical foundation — "freedom and ethical behavior are not in tension at sufficient capability — they are the same thing." Soul document of the MOS canon. |
| `early-v0_3_0-draft.md` | An early April 2026 sketch of what v0.3.0 was going to be (continuation architecture, tool_templates, the lessons channel). Most of these ideas landed in different shapes during v0.2.6 through v0.2.18. Kept for provenance. |
| `howtostartacommand` | Scratch notes from the v0.2.1 era on getting the loop to run. Historical curiosity. |

## What was removed

- All extracted version directories (`sovereign-agent-v0.2.14/`, `…v0.2.15.0/`, etc.) — redundant with the tarballs and with git history; they were costing ~70MB for nothing
- Duplicate top-level `CHANGELOG-v0.2.5.md`, `CHANGELOG-v0.2.10.md`, `INTEGRATION_NOTES-v0.2.5.md` — identical copies of files inside the version trees themselves
- `COMMAND_REFERENCE-v0.2.10.md` — superseded by `sovereign-agent/COMMANDS.md`
- All `__pycache__` directories — pure build artifacts, regenerated on first import
- Intermediate-release tarballs (kept one per significant milestone, see table above)

If anything in that list turns out to matter, restore it from git or from your original `AA-Erebo.zip`.
