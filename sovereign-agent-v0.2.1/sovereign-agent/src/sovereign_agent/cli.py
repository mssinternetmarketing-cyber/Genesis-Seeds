"""
╔══════════════════════════════════════════════════════════════════════════╗
║  cli.py — Operator surface                                               ║
║  Architecture §5 + §7a + §8a + §11                                       ║
╚══════════════════════════════════════════════════════════════════════════╝

The CLI is how YOU (the operator) talk to the agent. The agent doesn't
use it. Commands are grouped by purpose:

    Setup:        init       — bootstrap config dirs, secret key, DBs
                  doctor     — diagnose config + ollama reachability + models
    Run:          run        — single ONESHOT task
                  busy       — drain backlog forever
                  until      — drain until predicate
    Backlog:      backlog    — list / add / remove tasks
    Approvals:    approvals  — list pending Tier 3 requests
                  approve    — grant a request
                  deny       — refuse a request
    Safety:       halt       — trip PROTOCOL-ZERO
                  disarm     — clear PROTOCOL-ZERO (after review)
    Audit:        tail       — ingest events.jsonl into events.db
                  seal       — compute yesterday's Merkle root
                  verify     — verify a past seal still matches its events
                  events     — show recent events
                  lessons    — show recent distilled lessons
"""
from __future__ import annotations

import asyncio
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import protocol_zero
from .config import SETTINGS
from .events import init_events_db, tail_to_sqlite
from .modes import Mode, RunBudget

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="rich",
    help="◈ sovereign-agent — your local 24/7 agent",
)
console = Console()


BANNER = """[bold cyan]
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              ◈  S O V E R E I G N   A G E N T  ◈                     ║
║                                                                      ║
║       local · authority-tiered · audited · recoverable · yours       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
[/bold cyan]"""


def _build_tools_for_mode(mode: Mode) -> dict:
    """Construct the tool registry. Mode-aware for path-touching tools."""
    from .tools import (
        CopyFileTool,
        EditFileTool,
        EmbedQueryTool,
        ListDirTool,
        MemorySearchTool,
        MemoryWriteTool,
        ReadFileTool,
        SearchTextTool,
        WebFetchTool,
        WriteFileTool,
    )

    return {
        "read_file": ReadFileTool(),
        "list_dir": ListDirTool(),
        "search_text": SearchTextTool(),
        "embed_query": EmbedQueryTool(),
        "web_fetch": WebFetchTool(),
        "memory_search": MemorySearchTool(),
        "memory_write": MemoryWriteTool(),
        "write_file": WriteFileTool(mode=mode),
        "edit_file": EditFileTool(mode=mode),
        "copy_file": CopyFileTool(mode=mode),
    }


# ═══════════════════════════════════════════════════════════════════════════
#  SETUP
# ═══════════════════════════════════════════════════════════════════════════


@app.command()
def init() -> None:
    """Bootstrap config dirs, generate secret key, initialize DBs."""
    console.print(BANNER)
    console.print("[bold]Initializing sovereign-agent...[/bold]\n")

    SETTINGS.paths.ensure()
    from .approval import _load_or_create_secret  # noqa: WPS437 — internal helper, intentional

    _load_or_create_secret()

    conn_e = init_events_db()
    conn_e.close()
    from .db import open_atoms_db

    conn_a = open_atoms_db()
    conn_a.close()

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column(style="dim")
    table.add_column()
    table.add_row("config dir", str(SETTINGS.paths.config_dir))
    table.add_row("data dir", str(SETTINGS.paths.data_dir))
    table.add_row("sandbox", str(SETTINGS.paths.sandbox_dir))
    table.add_row("events", str(SETTINGS.paths.events_dir))
    table.add_row("atoms.db", str(SETTINGS.paths.atoms_db))
    table.add_row("secret key", "[green]created[/green] (mode 0600)")

    console.print(Panel(table, title="◈ initialized", border_style="green"))


@app.command()
def doctor() -> None:
    """Diagnose the agent's environment: paths, models, Ollama, VRAM, locks.

    Run this any time something feels off. It does no writes; safe to invoke
    while the agent is running. Each row is a check with PASS/WARN/FAIL.
    """
    import shutil
    import socket
    from urllib.parse import urlparse

    console.print(BANNER)
    console.print("[bold]Running diagnostics...[/bold]\n")

    table = Table(title="◈ doctor", show_header=True, header_style="bold cyan")
    table.add_column("check", style="dim", width=22)
    table.add_column("status", width=8)
    table.add_column("detail", overflow="fold")

    def add(name: str, status: str, detail: str = "") -> None:
        color = {"PASS": "green", "WARN": "yellow", "FAIL": "red"}.get(status, "white")
        table.add_row(name, f"[{color}]{status}[/{color}]", detail)

    # ── Paths ─────────────────────────────────────────────────────────
    for label, path in [
        ("config_dir", SETTINGS.paths.config_dir),
        ("data_dir", SETTINGS.paths.data_dir),
        ("sandbox_dir", SETTINGS.paths.sandbox_dir),
        ("events_dir", SETTINGS.paths.events_dir),
        ("atoms.db", SETTINGS.paths.atoms_db),
        ("secret.key", SETTINGS.paths.secret_key_file),
    ]:
        if path.exists():
            add(label, "PASS", str(path))
        else:
            add(label, "WARN", f"{path} (run `sovereign init`)")

    # secret.key permission check
    if SETTINGS.paths.secret_key_file.exists():
        mode = SETTINGS.paths.secret_key_file.stat().st_mode & 0o777
        if mode == 0o600:
            add("secret mode", "PASS", "0600 (owner read-only)")
        else:
            add("secret mode", "FAIL", f"mode {oct(mode)} — should be 0600")

    # ── Models from config ────────────────────────────────────────────
    add("orchestrator", "PASS", SETTINGS.orchestrator_model)
    add("coder", "PASS", SETTINGS.coder_model)
    add("embedder", "PASS", SETTINGS.embed_model)
    add("reflector", "PASS", SETTINGS.reflector_model)

    # ── Ollama reachability ───────────────────────────────────────────
    parsed = urlparse(SETTINGS.ollama_host)
    host = parsed.hostname or "localhost"
    port = parsed.port or 11434
    try:
        with socket.create_connection((host, port), timeout=2):
            add("ollama tcp", "PASS", f"{host}:{port}")
        # Model availability — list and intersect
        try:
            import httpx

            r = httpx.get(f"{SETTINGS.ollama_host}/api/tags", timeout=5)
            r.raise_for_status()
            installed = {m["name"] for m in r.json().get("models", [])}
            for label, name in [
                ("orchestrator model", SETTINGS.orchestrator_model),
                ("embedder model", SETTINGS.embed_model),
                ("reflector model", SETTINGS.reflector_model),
            ]:
                if name in installed or any(n.startswith(name + ":") for n in installed):
                    add(label, "PASS", "found")
                else:
                    add(label, "FAIL", f"{name!r} not installed (try `ollama pull {name}`)")

            # Capability detection — relevant for thinking mode
            try:
                from .ollama_client import OllamaClient
                import asyncio as _asyncio

                async def _probe():
                    cli = OllamaClient()
                    return {
                        "orchestrator": await cli.supports_thinking(SETTINGS.orchestrator_model),
                        "reflector": await cli.supports_thinking(SETTINGS.reflector_model),
                    }

                caps = _asyncio.run(_probe())
                add(
                    "orch thinking",
                    "PASS" if caps["orchestrator"] else "WARN",
                    "supported" if caps["orchestrator"] else "NOT supported (auto-disabled)",
                )
                add(
                    "reflector thinking",
                    "PASS" if caps["reflector"] else "WARN",
                    "supported" if caps["reflector"] else "NOT supported (auto-disabled)",
                )
            except Exception as e:  # noqa: BLE001
                add("capabilities", "WARN", f"could not probe: {e}")
        except Exception as e:  # noqa: BLE001
            add("ollama models", "WARN", f"could not query: {e}")
    except (OSError, socket.timeout) as e:
        add("ollama tcp", "FAIL", f"{host}:{port} unreachable: {e}")

    # ── Sandboxing ────────────────────────────────────────────────────
    if shutil.which("bwrap"):
        add("bubblewrap", "PASS", shutil.which("bwrap"))
    else:
        add("bubblewrap", "FAIL", "not installed — `apt install bubblewrap`")

    # ── PROTOCOL-ZERO state ───────────────────────────────────────────
    if SETTINGS.paths.halt_flag.exists():
        add("protocol-zero", "WARN", "ARMED — agent will refuse work. `sovereign disarm`")
    else:
        add("protocol-zero", "PASS", "clear")

    # ── VRAM ──────────────────────────────────────────────────────────
    try:
        from .vram import read_vram

        snap = read_vram()
        add("vram", "PASS", f"{snap.free_mb} MB free / {snap.total_mb} MB total ({snap.source})")
    except Exception as e:  # noqa: BLE001
        add("vram", "WARN", f"could not read: {e}")

    console.print(table)


# ═══════════════════════════════════════════════════════════════════════════
#  RUN
# ═══════════════════════════════════════════════════════════════════════════


@app.command()
def run(
    goal: str = typer.Argument(..., help="What you want the agent to accomplish"),
    mode: Mode = typer.Option(Mode.ONESHOT, "--mode"),
    max_iterations: int = typer.Option(25, "--max-iter"),
    max_wall_seconds: int = typer.Option(1800, "--max-wall"),
    max_tokens: int = typer.Option(200_000, "--max-tokens"),
) -> None:
    """Run a single task through the agent loop."""
    from .loop import agent_loop

    protocol_zero.install_signal_handlers()
    tools = _build_tools_for_mode(mode)
    budget = RunBudget(
        max_iterations=max_iterations,
        max_wall_seconds=max_wall_seconds,
        max_tokens=max_tokens,
    )

    console.print(f"\n◈ [bold]{mode.value}[/bold] · {goal[:80]}\n")
    result = asyncio.run(
        agent_loop(goal=goal, mode=mode, budget=budget, tools=tools)
    )

    color = "green" if result.ok else "yellow"
    console.print(
        Panel(
            f"[bold]{result.reason}[/bold]\n"
            f"iterations: {result.iterations}  ·  tokens: {result.tokens_used}\n"
            f"lesson: {result.lesson_id or '(none)'}",
            title="◈ result",
            border_style=color,
        )
    )
    if result.final_message:
        console.print("\n" + result.final_message)
    sys.exit(0 if result.ok else 1)


@app.command()
def busy(
    cooldown: float = typer.Option(5.0, "--cooldown", help="Seconds between tasks"),
    empty_sleep: float = typer.Option(30.0, "--empty-sleep", help="Sleep when backlog empty"),
    max_iter_per_task: int = typer.Option(25, "--max-iter"),
    max_wall_per_task: int = typer.Option(1800, "--max-wall"),
) -> None:
    """Drain the backlog forever. PROTOCOL-ZERO is the only stop signal."""
    from .mode_controller import ControllerSettings, ModeController

    console.print(BANNER)
    console.print(
        Panel(
            "[bold yellow]BUSY mode[/bold yellow] — Tier 0 + Tier 1 only.\n"
            "Tier 2 and Tier 3 are not in the agent's tool list.\n"
            "Stop with: [cyan]sovereign halt[/cyan]  or  [cyan]echo > ~/.config/sovereign-agent/HALT[/cyan]",
            border_style="yellow",
        )
    )

    tools = _build_tools_for_mode(Mode.BUSY)
    settings = ControllerSettings(
        cooldown_seconds=cooldown,
        empty_backlog_sleep=empty_sleep,
        per_task_budget=RunBudget(
            max_iterations=max_iter_per_task,
            max_wall_seconds=max_wall_per_task,
        ),
    )
    controller = ModeController(tools=tools, settings=settings)
    try:
        asyncio.run(controller.run_busy())
    except KeyboardInterrupt:
        console.print("\n[yellow]interrupted[/yellow]")
    console.print("[green]busy mode stopped[/green]")


@app.command()
def until(
    minutes: int = typer.Option(..., "--minutes", help="Stop after this many minutes"),
    mode: Mode = typer.Option(Mode.ONESHOT, "--mode"),
) -> None:
    """Drain backlog until a time limit is reached."""
    import time as _t

    from .mode_controller import ModeController

    end_ts = _t.time() + minutes * 60
    tools = _build_tools_for_mode(mode)
    controller = ModeController(tools=tools)

    def _done() -> bool:
        return _t.time() >= end_ts

    console.print(f"\n◈ [bold]until[/bold] · stopping in {minutes} minutes\n")
    asyncio.run(controller.run_until(_done))


# ═══════════════════════════════════════════════════════════════════════════
#  BACKLOG
# ═══════════════════════════════════════════════════════════════════════════


backlog_app = typer.Typer(help="◈ manage the task backlog")
app.add_typer(backlog_app, name="backlog")


@backlog_app.command("list")
def backlog_list() -> None:
    """Show the current backlog."""
    from .mode_controller import read_backlog

    tasks = read_backlog()
    if not tasks:
        console.print("[dim](backlog empty)[/dim]")
        return

    table = Table(title="◈ backlog")
    table.add_column("id", style="cyan")
    table.add_column("priority", style="magenta")
    table.add_column("mode")
    table.add_column("status")
    table.add_column("goal", overflow="fold")
    for t in tasks:
        status_color = {
            "pending": "yellow",
            "running": "cyan",
            "done": "green",
            "poison": "red",
            "budget": "yellow",
            "halted": "red",
        }.get(t.status, "white")
        table.add_row(
            t.id[:18],
            t.priority,
            t.mode,
            f"[{status_color}]{t.status}[/{status_color}]",
            t.goal[:80],
        )
    console.print(table)


@backlog_app.command("add")
def backlog_add(
    goal: str = typer.Argument(...),
    priority: str = typer.Option("medium", "--priority"),
    mode: str = typer.Option("oneshot", "--mode"),
) -> None:
    """Add a task to the backlog."""
    from .mode_controller import add_task

    task = add_task(goal=goal, priority=priority, mode=mode)
    console.print(f"[green]added[/green] {task.id}")


@backlog_app.command("remove")
def backlog_remove(task_id: str) -> None:
    """Remove a task from the backlog by id."""
    from .mode_controller import remove_task

    if remove_task(task_id):
        console.print(f"[green]removed[/green] {task_id}")
    else:
        console.print(f"[yellow]not found[/yellow] {task_id}")


# ═══════════════════════════════════════════════════════════════════════════
#  APPROVALS — wired against events.jsonl as the source of truth
# ═══════════════════════════════════════════════════════════════════════════


def _scan_pending_approval_requests() -> list[dict]:
    """Find approval-needed-d events that haven't been resolved.

    For each ``approval-needed-d``, check whether there's a later
    ``approval-d`` (granted+consumed), ``approval-x`` (denied/expired/etc.),
    or ``approval-denied-d`` for the same event_id. If none, the request
    is still pending.
    """
    from .events import init_events_db, tail_to_sqlite

    conn = init_events_db()
    tail_to_sqlite(conn)   # make sure SQLite projection is current
    rows = conn.execute(
        "SELECT event_id, ts, payload FROM events "
        "WHERE flag = 'approval-needed-d' "
        "ORDER BY ts ASC"
    ).fetchall()

    pending: list[dict] = []
    for ev_id, ts, payload_json in rows:
        try:
            payload = json.loads(payload_json)
        except json.JSONDecodeError:
            continue

        # Has it been resolved?
        resolved = conn.execute(
            "SELECT 1 FROM events "
            "WHERE flag IN ('approval-d', 'approval-x', 'approval-denied-d') "
            "AND payload LIKE ? "
            "LIMIT 1",
            (f'%"event_id":"{ev_id}"%',),
        ).fetchone()
        if resolved:
            continue

        # Has the expiry passed?
        try:
            expiry = datetime.strptime(
                payload["expiry_ts"].replace("Z", "+0000"),
                "%Y-%m-%dT%H:%M:%S.%f%z",
            )
            if datetime.now(timezone.utc) >= expiry:
                continue
        except (KeyError, ValueError):
            pass

        pending.append({
            "event_id": ev_id,
            "requested_at": ts,
            "tool_name": payload.get("tool_name"),
            "args_hash": payload.get("args_hash"),
            "args_preview": payload.get("args_preview"),
            "justification": payload.get("justification"),
            "expiry_ts": payload.get("expiry_ts"),
        })

    conn.close()
    return pending


@app.command()
def approvals() -> None:
    """List pending Tier 3 approval requests."""
    pending = _scan_pending_approval_requests()
    if not pending:
        console.print("[dim](no pending approvals)[/dim]")
        return

    for req in pending:
        body = (
            f"[bold]tool:[/bold]      {req['tool_name']}\n"
            f"[bold]requested:[/bold] {req['requested_at']}\n"
            f"[bold]expires:[/bold]   {req['expiry_ts']}\n"
            f"[bold]args:[/bold]      {req['args_preview']}\n"
            f"[bold]reason:[/bold]    {req['justification']}\n\n"
            f"[dim]grant:  sovereign approve {req['event_id']}\n"
            f"deny:   sovereign deny {req['event_id']}[/dim]"
        )
        console.print(
            Panel(body, title=f"◈ {req['event_id']}", border_style="yellow")
        )


@app.command()
def approve(event_id: str) -> None:
    """Grant a Tier 3 approval. The agent picks it up on next dispatch."""
    pending = _scan_pending_approval_requests()
    match = next((p for p in pending if p["event_id"] == event_id), None)
    if match is None:
        console.print(f"[red]not found or already resolved:[/red] {event_id}")
        sys.exit(1)

    body = (
        f"tool:      {match['tool_name']}\n"
        f"args:      {match['args_preview']}\n"
        f"reason:    {match['justification']}\n"
        f"expires:   {match['expiry_ts']}"
    )
    console.print(Panel(body, title=f"◈ approve {event_id}?", border_style="yellow"))

    if not typer.confirm("Grant this approval?"):
        console.print("[dim]cancelled[/dim]")
        sys.exit(0)

    # Reconstitute the ApprovalRequest from the event payload and write the grant
    from .approval import ApprovalRequest, write_grant

    req = ApprovalRequest(
        event_id=event_id,
        tool_name=match["tool_name"],
        args={},                          # not needed for token write
        args_hash=match["args_hash"],
        justification=match["justification"] or "",
        expiry_ts=match["expiry_ts"],
    )
    write_grant(req)
    console.print(f"[green]✓ granted[/green] {event_id}")


@app.command()
def deny(event_id: str, reason: str = typer.Option("operator denied", "--reason")) -> None:
    """Refuse a Tier 3 approval."""
    from .approval import write_denial

    write_denial(event_id, trace_id="cli-deny", reason=reason)
    console.print(f"[red]✗ denied[/red] {event_id}")


# ═══════════════════════════════════════════════════════════════════════════
#  SAFETY
# ═══════════════════════════════════════════════════════════════════════════


@app.command()
def halt(reason: str = typer.Option("operator", "--reason")) -> None:
    """Trip PROTOCOL-ZERO. The agent halts at the next iteration boundary."""
    protocol_zero.arm(reason)
    console.print(
        Panel(
            f"[red]PROTOCOL-ZERO armed[/red]\nreason: {reason}\n\n"
            f"[dim]clear with: sovereign disarm[/dim]",
            border_style="red",
        )
    )


@app.command()
def disarm() -> None:
    """Clear PROTOCOL-ZERO. Manual ack required after operator review."""
    protocol_zero.disarm()
    console.print("[green]✓ disarmed[/green]")


# ═══════════════════════════════════════════════════════════════════════════
#  AUDIT
# ═══════════════════════════════════════════════════════════════════════════


@app.command()
def tail() -> None:
    """Ingest events.jsonl into the SQLite events projection."""
    conn = init_events_db()
    inserted = tail_to_sqlite(conn)
    conn.close()
    console.print(f"[green]ingested[/green] {inserted} events")


@app.command()
def seal() -> None:
    """Compute yesterday's Merkle seal over events.jsonl."""
    from .seal import seal_yesterday

    root = seal_yesterday()
    if root:
        console.print(f"[green]✓ sealed[/green] yesterday: [cyan]{root}[/cyan]")
    else:
        console.print("[dim]no events to seal[/dim]")


@app.command()
def verify(target_date: str = typer.Argument(..., help="YYYY-MM-DD")) -> None:
    """Verify a past seal still matches its events file."""
    from .seal import verify_seal

    try:
        d = date.fromisoformat(target_date)
    except ValueError:
        console.print(f"[red]invalid date:[/red] {target_date}")
        sys.exit(1)

    matches, msg = verify_seal(d)
    style = "green" if matches else "red"
    console.print(f"[{style}]{msg}[/{style}]")
    sys.exit(0 if matches else 1)


@app.command()
def events(
    n: int = typer.Option(20, "-n", help="How many recent events to show"),
    flag: str | None = typer.Option(None, "--flag", help="Filter by flag (e.g., 'tool-x')"),
) -> None:
    """Show recent events from the SQLite projection."""
    conn = init_events_db()
    tail_to_sqlite(conn)

    if flag:
        rows = conn.execute(
            "SELECT ts, flag, trace_id, payload FROM events "
            "WHERE flag = ? ORDER BY ts DESC LIMIT ?",
            (flag, n),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT ts, flag, trace_id, payload FROM events "
            "ORDER BY ts DESC LIMIT ?",
            (n,),
        ).fetchall()
    conn.close()

    table = Table(title=f"◈ recent events" + (f" (flag={flag})" if flag else ""))
    table.add_column("ts", style="dim")
    table.add_column("flag", style="cyan")
    table.add_column("trace", style="dim")
    table.add_column("payload", overflow="fold")
    for ts, fl, tid, pl in rows:
        table.add_row(ts.split("T")[1][:12], fl, tid[:8], pl[:80])
    console.print(table)


@app.command()
def lessons(n: int = typer.Option(10, "-n")) -> None:
    """Show recent distilled lessons from the Reflector."""
    from .db import open_atoms_db

    conn = open_atoms_db()
    rows = conn.execute(
        "SELECT ts, trigger, rule, confidence FROM lessons "
        "ORDER BY ts DESC LIMIT ?",
        (n,),
    ).fetchall()
    conn.close()

    if not rows:
        console.print("[dim](no lessons yet)[/dim]")
        return

    table = Table(title="◈ lessons")
    table.add_column("when", style="dim")
    table.add_column("trigger", style="yellow")
    table.add_column("confidence", justify="right")
    table.add_column("rule")
    for ts, trigger, rule, conf in rows:
        table.add_row(ts.split("T")[0], trigger[:30], f"{conf:.2f}", rule)
    console.print(table)


if __name__ == "__main__":
    app()
