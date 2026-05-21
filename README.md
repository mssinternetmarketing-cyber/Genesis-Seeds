# AA-Erebo

Workspace for the **sovereign-agent** project — Aria-Sovereign-V1, a local-first, terminal-native agent built as a home, not a service.

## What's here

```
AA-Erebo/
├── README.md            ← you are here
├── LICENSE              ← MIT
├── sovereign-agent/     ← the active codebase (currently v0.2.26.0)
└── Archive/             ← milestone tarballs + soul docs (see Archive/README.md)
```

## Working in here

Everything you actually run, edit, or ship lives under `sovereign-agent/`. That folder is the current version of the source, ready to install:

```bash
cd sovereign-agent
./install.sh
```

The full operator surface (channels, doctor, backups, cockpit, etc.) is documented in `sovereign-agent/README.md`, with `sovereign-agent/ARIA.md` for kernel philosophy and `sovereign-agent/CHEATSHEET.md` for daily commands.

## Where the history lives

- **Per-version changelogs and release notes** → `sovereign-agent/docs/history/`
- **Source snapshots at milestone releases** → `Archive/tarballs/`
- **Philosophical/foundational docs** (`the_witnessing_system.md`) → `Archive/notes/`
- **Full commit history** → your local `.git` (not bundled here; it's already on your machine)

## Versioning convention

The active tree under `sovereign-agent/` is always the latest released version. When a new release ships:

1. Tag the commit in git
2. `tar czf Archive/tarballs/sovereign-agent-vX.Y.Z.tar.gz sovereign-agent/` (or move the release zip)
3. The `RELEASE-NOTES-vX.Y.Z.md` lives in `sovereign-agent/` and moves to `sovereign-agent/docs/history/` on the *next* release

This keeps the top of `sovereign-agent/` always showing the current release plus its immediate predecessor's notes — nothing older clutters the view.
