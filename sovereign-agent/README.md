# sovereign-agent

> *Aria — local-first, terminal-native, audit-trail-as-UI. Built as a home, not a service.*

This is the operator install + upgrade guide. For the kernel philosophy, read [ARIA.md](ARIA.md). For everyday commands, see [CHEATSHEET.md](CHEATSHEET.md).

---

## TL;DR install

```bash
tar xzf sovereign-agent-vX.Y.Z.tar.gz
cd sovereign-agent-vX.Y.Z
./install.sh
```

That's it. The install script verifies Python, runs `pip install -e .`, confirms the version on PATH matches the source, applies migrations (with automatic backfill for existing databases), runs `sov doctor`, and shows your install summary.

If anything fails, the script tells you exactly what failed and how to fix it.

---

## Upgrading from an earlier version

The same `./install.sh` works for upgrades. It's idempotent.

If you keep multiple versions in `~/AA-Erebo/` and use the `sovereign-agent-current` symlink convention:

```bash
cd ~/AA-Erebo
tar xzf sovereign-agent-v0.2.18.1.tar.gz
cd sovereign-agent-v0.2.18.1
./install.sh                          # updates the symlink automatically
```

After upgrade, `sov doctor` should report `verdict: healthy`. If migrations need to be backfilled (because you came from a pre-migration-framework version), it will tell you to run `sov migrations apply` — which handles both backfill and apply in one step.

---

## What's installed where

```
~/.local/share/sovereign-agent/      # data dir (atoms.db, telemetry, profile)
~/.config/sovereign-agent/           # config dir (agent.yaml, shards.json)
~/AA-Erebo/sovereign-agent-current/  # symlinked current version (optional convention)
```

Run `sov info` at any time to see this concretely on your machine.

---

## The single most important command if something feels wrong

```bash
sov doctor
```

It will tell you:

- What Python version is running
- What `sovereign-agent` version is installed
- Where the `sovereign` and `sov` binaries actually live on PATH
- Whether your install layout is the standard pip install or the AA-Erebo symlink convention
- Where your config/data dirs are and whether they're writable
- Whether `atoms.db` exists, its size, integrity status, and atom count
- Migration status (applied vs. pending vs. needs-backfill)
- All registered channels (24 expected at v0.2.18+)
- All seven commitments codified
- Whether ARIA.md is present
- Key dependency versions
- Free disk space

When you hit confusing CLI errors like *"No such command 'migrations'"*, this is the first command to run. It will say "you have v0.2.15.0 installed, not v0.2.18.0" — and the mystery dissolves.

For automatic fixes (currently: migration backfill):

```bash
sov doctor --fix
```

---

## Verifying your install is what you think it is

Three commands, one check each:

```bash
sov --version                  # what's on PATH?
sov info                       # paths, atoms.db state, last heartbeat
sov doctor                     # comprehensive diagnostic
```

If any of these surprise you, you have a stale install somewhere. The most common culprit:

- Multiple `sovereign-agent-vX.Y.Z` directories in `~/AA-Erebo/`
- Shell autocompletion picking the wrong one when you `cd`
- `pip install -e .` then re-installs the wrong directory's package, downgrading you

**The fix** is to always run `sov doctor` after install/upgrade. It will catch the mismatch in seconds.

---

## Common failures and what they mean

| Symptom | Most likely cause | Fix |
|---|---|---|
| `No such command 'foo'` where `foo` is a v0.2.18+ command | You're on an older installed version | `sov doctor` to confirm; re-run `./install.sh` |
| `sovereign --version` shows a different version than the tarball you just installed | Stale install on PATH precedes the new one | `pip uninstall sovereign-agent`; re-run `./install.sh` |
| `migrations.IntegrityError` on apply | Pre-migration-framework DB without backfill | `sov migrations backfill` then `sov migrations apply` |
| `atoms.db` won't open / `database disk image is malformed` | Disk corruption | Restore from `sov backup` snapshot; `sov doctor` |
| `sov-chat` says "cpu/vram temps unavailable" | Hardware sensors not exposed (laptop on battery, missing kernel modules) | Cosmetic; ignore |

---

## Channels (v0.2.18)

All 24 of Aria's memory channels:

**Tier 0 (light):** context, emotions, humor, intention, intuition, personalities, trust

**Tier 1 (durable, append-only):** insights, lessons, ritual, identity, **episodes**, **reasoning**, **gaps**, **heartbeat**

**Tier 2 (persistent, named):** task, recall, **commitments**, specialist, goals, financial

**Tier 3 (personal data):** people, **relationships**

**Tier 4 (reward):** reward (anti-egotism asymmetry)

Bold = v0.2.17/v0.2.18 additions. Each channel has `sov <channel> --help` for its CLI sub-app.

---

## The seven commitments

```bash
sov constitution list
```

The commitments are sacred. They are not release-mutable. As of v0.2.18, three of seven have automated runtime checks; the rest are operator-audited prose.

```bash
sov constitution check --tier 3 --confidence 0.95 --source operator --idem foo
```

evaluates a hypothetical action against all seven. Useful for "would this action violate something?" before you do the action.

---

## Backups and disaster recovery

```bash
sov backup snapshot --label pre-upgrade
sov backup list
sov backup verify <snapshot_id>
sov backup restore <snapshot_id>
```

Snapshots are application-consistent (uses SQLite's online backup API, not raw file copy). The verify step re-hashes the snapshot and confirms it's intact. Restore stages an audit before doing the actual swap — if the staged audit fails, the restore is aborted.

If `atoms.db` is corrupted and you have no backup, `sov steward integrity` will tell you which tables are damaged. In the worst case, channels can be re-bootstrapped from atoms (which are the immutable ground truth).

---

## Getting help

- `sov --help` for the top-level command tree
- `sov <command> --help` for any subcommand
- `sov doctor` when behavior surprises you
- ARIA.md for the kernel philosophy
- CHEATSHEET.md for daily commands
- The release notes in `RELEASE-NOTES-vX.Y.Z.md` for what changed
