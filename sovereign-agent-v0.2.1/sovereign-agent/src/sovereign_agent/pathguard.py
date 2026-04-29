"""Path-scope enforcement. Architecture §6 invariant 6, §7 matrix.

In BUSY mode, every write/edit/copy target must resolve (via realpath) to a
descendant of $AGENT_HOME/sandbox. Symlinks are followed before the check.

This is one of three layers; the others are:
  - tier matrix: tools above tier 1 are not in the available list when mode=BUSY
  - bwrap: $PROJECT_DIR is --ro-bind under BUSY, --bind otherwise
"""
from __future__ import annotations

from pathlib import Path

from .config import SETTINGS
from .modes import Mode


class PathScopeViolation(Exception):
    """Raised when a path-touching tool tries to write outside its allowed scope."""

    def __init__(self, path: str, *, mode: Mode, allowed: str):
        self.path = path
        self.mode = mode
        self.allowed = allowed
        super().__init__(
            f"path-scope violation: {path!r} not under {allowed!r} (mode={mode})"
        )


def _realpath(p: str | Path) -> Path:
    """Resolve symlinks, .., etc. Returns absolute Path."""
    # strict=False: target may not exist yet (write_file creates it)
    return Path(p).expanduser().resolve(strict=False)


def is_under(path: str | Path, root: str | Path) -> bool:
    """True iff realpath(path) is the root or a descendant of root."""
    rp = _realpath(path)
    rr = _realpath(root)
    try:
        rp.relative_to(rr)
        return True
    except ValueError:
        return False


def check_write_path(target: str | Path, mode: Mode) -> Path:
    """Validate a write/edit destination for the given mode.

    Returns the resolved Path on success.
    Raises PathScopeViolation if mode == BUSY and target is outside sandbox.

    Non-BUSY modes have no path guard here — they delegate to the bwrap mount
    layout and per-tool confirmation prompts (see §7 matrix).
    """
    resolved = _realpath(target)
    if mode == Mode.BUSY:
        sandbox = SETTINGS.paths.sandbox_dir
        if not is_under(resolved, sandbox):
            raise PathScopeViolation(
                str(resolved), mode=mode, allowed=str(sandbox)
            )
    return resolved
