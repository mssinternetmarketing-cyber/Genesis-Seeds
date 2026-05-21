"""
╔══════════════════════════════════════════════════════════════════════════╗
║  conversation.py — High-level entry point for natural conversation       ║
║  v0.2.19.0                                                                ║
║                                                                           ║
║  This is what `sov chat "<text>"` calls. It wires the interpreter and    ║
║  router together with the operator's environment (project store, channel║
║  writers, event sink, ollama client).                                    ║
║                                                                           ║
║  The cockpit's `_run_directive_worker` also calls this — instead of     ║
║  spawning `sovereign do` as a subprocess. v0.2.19.0 collapses that       ║
║  subprocess hop for the common case: when the operator's message is     ║
║  conversation or tier-0/1 work, no subprocess is needed and the          ║
║  cockpit's UI stays responsive without the §19.2 plumbing dance.        ║
║                                                                           ║
║  Why retain `sovereign do` as a subprocess at all:                      ║
║    For tier-2 long-running commands (`sov dream start`, `sov continue`) ║
║    a subprocess is still right — they run for hours and produce events. ║
║    The router's executor parameter is the seam: in the cockpit, tier-2  ║
║    commands route through the subprocess-spawning executor; tier-0/1    ║
║    commands run inline.                                                  ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .config import SETTINGS
from .intents import ConversationContext, Intent
from .interpreter import interpret
from .router import Router, RouteResult

logger = logging.getLogger(__name__)


@dataclass
class Turn:
    """The complete record of one conversational turn.

    Surfaces (cockpit, CLI) consume this; they don't need to know about
    Intent / RouteResult internals unless they want to.
    """
    text: str
    intent: Intent
    result: RouteResult

    @property
    def messages(self) -> list[str]:
        return self.result.messages

    @property
    def kind(self) -> str:
        return self.result.kind

    @property
    def has_pending(self) -> bool:
        return self.result.pending is not None


async def converse(
    text: str,
    *,
    ollama_client: Any = None,
    project_store: Any = None,
    channel_writer: Callable[[str, str], None] | None = None,
    event_sink: Callable[[dict], None] | None = None,
    executor: Callable[[list[str]], int] | None = None,
    surface: str = "cli",
    recent_turns: tuple[str, ...] = (),
    allow_llm: bool = True,
) -> Turn:
    """Process one operator message end-to-end. Returns a Turn record.

    Steps:
      1. Build a ConversationContext from the environment.
      2. Call interpret() to classify intent.
      3. Call router.route() to enact the intent.
      4. Wrap as a Turn and return.

    Never raises. If anything goes wrong, the operator sees Aria's voice
    explain what failed; the work is not silently dropped.
    """
    text = (text or "").strip()
    if not text:
        from .intents import Conversation
        empty = Conversation(text="", save_to=["context"], reply_voice="quiet")
        return Turn(text="", intent=empty, result=RouteResult(kind="empty"))

    # Build context
    known: tuple[str, ...] = ()
    if project_store is not None:
        try:
            known = tuple(project_store.list_names())
        except Exception as exc:  # noqa: BLE001
            logger.debug("project_store.list_names failed: %r", exc)

    context = ConversationContext(
        known_project_names=known,
        recent_turns=recent_turns,
        surface=surface,  # type: ignore[arg-type]
        busy=False,
    )

    # Interpret
    intent = await interpret(
        text,
        context=context,
        ollama_client=ollama_client,
        allow_llm=allow_llm,
    )

    # Route
    router = Router(
        project_store=project_store,
        channel_writer=channel_writer,
        event_sink=event_sink,
        executor=executor,
    )
    result = await router.route(intent)

    return Turn(text=text, intent=intent, result=result)


# ─── Default integrations ───────────────────────────────────────────────────


def make_default_channel_writer(
    channel_root: Path | None = None,
) -> Callable[[str, str], None]:
    """A default channel writer that appends to the per-channel YAML
    files under SETTINGS.paths.data_dir/channels/.

    This is intentionally minimal — the real channel writers in
    mem_channels/*.py have richer per-channel schemas. This default is
    a safety net for the offline/no-LLM path so that conversation
    content is never silently dropped.
    """
    from datetime import datetime, timezone

    root = channel_root or (SETTINGS.paths.data_dir / "channels")

    def write(channel: str, text: str) -> None:
        root.mkdir(parents=True, exist_ok=True)
        # Accept lowercase + digits + hyphens + underscores.
        # v0.2.21.0: hyphens are now valid since Aria names channels
        # like "back-pain" and "qcai-ring". Anything outside this set
        # (whitespace, slashes, quotes, control chars) is filtered.
        import re as _re
        if not _re.match(r"^[a-z0-9][a-z0-9_-]{0,63}$", channel):
            logger.debug("rejecting unsafe channel name: %r", channel)
            return
        path = root / f"{channel}.log"
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            with path.open("a", encoding="utf-8") as f:
                f.write(f"[{ts}] {text}\n")
        except OSError as exc:
            logger.warning("channel write failed [%s]: %r", channel, exc)

    return write


def make_default_event_sink() -> Callable[[dict], None]:
    """A default event sink that appends to a NDJSON file under
    SETTINGS.paths.data_dir/conversation-events.ndjson.

    The richer event system in events.py handles audit-grade events;
    this default exists so the conversation layer always has an
    append-only trail even when the full event pipeline isn't running.
    """
    import json
    from datetime import datetime, timezone

    root = SETTINGS.paths.data_dir
    root.mkdir(parents=True, exist_ok=True)
    path = root / "conversation-events.ndjson"

    def write(evt: dict) -> None:
        evt = dict(evt)
        evt.setdefault(
            "ts",
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        try:
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(evt, ensure_ascii=False) + "\n")
        except OSError as exc:
            logger.warning("event sink write failed: %r", exc)

    return write


__all__ = [
    "Turn",
    "converse",
    "make_default_channel_writer",
    "make_default_event_sink",
]
