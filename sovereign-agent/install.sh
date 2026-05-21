#!/usr/bin/env bash
# sovereign-agent install.sh
#
# Idempotent installer with verification. Safe to re-run.
#
# What it does:
#   1. Verifies Python >= 3.10 is available
#   2. Resolves the install directory (defaults to the directory this script lives in)
#   3. Runs `pip install --break-system-packages -e .` from that directory
#   4. Updates the ~/AA-Erebo/sovereign-agent-current symlink (if AA-Erebo exists)
#   5. Runs `sov doctor` for verification
#   6. Runs `sov migrations apply` (auto-backfills then applies new)
#   7. Reports the final state
#
# What it does NOT do:
#   - Install Python (you have it)
#   - Install Ollama (separate, optional)
#   - Touch your data directory
#   - Auto-resolve broken state — that's `sov doctor --fix`'s job

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EREBO_DIR="${HOME}/AA-Erebo"
CURRENT_SYMLINK="${EREBO_DIR}/sovereign-agent-current"

# ─── Colors (only if stdout is a tty) ──────────────────────────────────────
if [[ -t 1 ]]; then
    C_BOLD=$'\033[1m'
    C_GREEN=$'\033[32m'
    C_YELLOW=$'\033[33m'
    C_RED=$'\033[31m'
    C_DIM=$'\033[2m'
    C_RESET=$'\033[0m'
else
    C_BOLD="" C_GREEN="" C_YELLOW="" C_RED="" C_DIM="" C_RESET=""
fi

say()   { printf '%s\n' "$*"; }
ok()    { printf "${C_GREEN}✓${C_RESET} %s\n" "$*"; }
warn()  { printf "${C_YELLOW}⚠${C_RESET} %s\n" "$*"; }
err()   { printf "${C_RED}✗${C_RESET} %s\n" "$*" >&2; }
head1() { printf "\n${C_BOLD}%s${C_RESET}\n" "$*"; }

# ─── Step 1: Python check ──────────────────────────────────────────────────

head1 "▸ Python version check"
if ! command -v python3 >/dev/null 2>&1; then
    err "python3 is not on PATH. Install Python 3.10+ and re-run."
    exit 1
fi
PY_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')"
PY_OK="$(python3 -c 'import sys; print("1" if sys.version_info >= (3, 10) else "0")')"
if [[ "$PY_OK" != "1" ]]; then
    err "Aria requires Python 3.10+. Found: $PY_VERSION"
    exit 1
fi
ok "Python $PY_VERSION"

# ─── Step 2: Confirm install dir contains pyproject.toml ──────────────────

head1 "▸ Install source check"
if [[ ! -f "${SCRIPT_DIR}/pyproject.toml" ]]; then
    err "No pyproject.toml in ${SCRIPT_DIR}"
    err "Are you running install.sh from inside the unpacked sovereign-agent-vX.Y.Z directory?"
    exit 1
fi
INSTALL_VERSION="$(grep -E '^version *= *"' "${SCRIPT_DIR}/pyproject.toml" | head -1 | sed -E 's/.*"([^"]+)".*/\1/')"
ok "Source dir: ${SCRIPT_DIR}"
ok "Version in source: ${INSTALL_VERSION}"

# ─── Step 3: pip install ───────────────────────────────────────────────────

head1 "▸ pip install (editable)"
PIP_OUT="$(mktemp)"
if pip install --break-system-packages -e "${SCRIPT_DIR}" >"${PIP_OUT}" 2>&1; then
    # Extract the installed version from the pip output
    INSTALLED_BY_PIP="$(grep -oE 'sovereign-agent[- ][0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+)?' "${PIP_OUT}" | tail -1 | sed -E 's/sovereign-agent[- ]//')"
    ok "pip install succeeded · installed ${INSTALLED_BY_PIP:-unknown}"
    rm -f "${PIP_OUT}"
else
    err "pip install FAILED. Output:"
    cat "${PIP_OUT}" >&2
    rm -f "${PIP_OUT}"
    exit 1
fi

# ─── Step 4: Verify version on PATH matches what we just installed ────────

head1 "▸ Verify version on PATH"
if ! command -v sovereign >/dev/null 2>&1; then
    err "\`sovereign\` is not on PATH after install."
    err "The package was installed but the entry point script may not be on \$PATH."
    err "Check: $(python3 -c 'import site; print(site.USER_BASE + "/bin")')"
    exit 1
fi
SOVEREIGN_BIN="$(command -v sovereign)"
ON_PATH_VERSION="$(sovereign --version 2>&1 | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1 || echo "unknown")"
if [[ "$ON_PATH_VERSION" != "$INSTALL_VERSION" ]]; then
    warn "PATH binary version (${ON_PATH_VERSION}) does not match source version (${INSTALL_VERSION})"
    warn "This typically means an old install is still being found first."
    warn "  binary: ${SOVEREIGN_BIN}"
    warn "Possible fix: pip uninstall sovereign-agent && re-run this script"
else
    ok "sovereign on PATH: ${SOVEREIGN_BIN} (v${ON_PATH_VERSION})"
fi

# ─── Step 5: Update symlink if AA-Erebo layout is in use ──────────────────

if [[ -d "${EREBO_DIR}" ]]; then
    head1 "▸ AA-Erebo symlink"
    if [[ -L "${CURRENT_SYMLINK}" ]] || [[ ! -e "${CURRENT_SYMLINK}" ]]; then
        ln -sfn "${SCRIPT_DIR}" "${CURRENT_SYMLINK}"
        ok "${CURRENT_SYMLINK} → ${SCRIPT_DIR}"
    else
        warn "${CURRENT_SYMLINK} exists and is NOT a symlink; leaving untouched"
    fi
fi

# ─── Step 6: Run doctor for verification ──────────────────────────────────

head1 "▸ sov doctor"
sovereign doctor || {
    warn "doctor reported issues; review above. Continuing — many issues are auto-resolvable."
}

# ─── Step 7: Apply migrations (auto-backfills first) ──────────────────────

head1 "▸ sov migrations apply"
sovereign migrations apply || {
    err "Migration apply failed. Atoms.db may be in an unusable state."
    err "Try: sovereign doctor"
    exit 1
}

# ─── Step 8: Final summary ────────────────────────────────────────────────

head1 "▸ Install complete"
sovereign info || true

cat <<EOF

${C_BOLD}Next steps:${C_RESET}
  ${C_DIM}#${C_RESET} See what Aria can do
  ${C_DIM}$${C_RESET} sov --help

  ${C_DIM}#${C_RESET} Confirm the seven commitments are codified
  ${C_DIM}$${C_RESET} sov constitution list

  ${C_DIM}#${C_RESET} Aria's first heartbeat on this install
  ${C_DIM}$${C_RESET} sov heartbeat pulse "first pulse on ${INSTALL_VERSION}"

  ${C_DIM}#${C_RESET} Open the cockpit
  ${C_DIM}$${C_RESET} sov-chat

EOF
