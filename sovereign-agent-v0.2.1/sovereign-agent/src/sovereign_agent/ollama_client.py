"""Ollama client wrapper with think_mode-aware dispatch.

Architecture §6 (agent loop) + §V fragile assumption 2a/2b: thinking-mode
behavior on tool-calling is empirically validated separately from no-think.
Default policy is `plan_only`: thinking on for the planner call, off for
tool-dispatch calls.

CAPABILITY DETECTION: Not all tool-calling models support Ollama's `think`
field. Llama 3 Groq Tool Use, for instance, is a tool-calling specialist
without a thinking mode — sending `think=true` returns HTTP 400. We detect
this once per model via ``/api/show`` and silently fall back to no-think
for those models, regardless of the operator's policy. This is the right
behavior: capability mismatches aren't transient errors; they're config
truths the agent should adapt to.
"""
from __future__ import annotations

import asyncio
from enum import StrEnum
from typing import Any

import ollama

from .config import SETTINGS


class CallKind(StrEnum):
    PLAN = "plan"          # decompose a goal into next-action — thinking helps
    DISPATCH = "dispatch"  # produce a tool call against the available list — no-think safer
    REFLECT = "reflect"    # post-task lesson capture — thinking helps


def _policy_wants_think(call_kind: CallKind) -> bool:
    """What the *operator's policy* wants. Capability detection may override."""
    policy = SETTINGS.think_mode
    if policy == "always":
        return True
    if policy == "never":
        return False
    # plan_only (default)
    return call_kind in (CallKind.PLAN, CallKind.REFLECT)


class CapabilityError(Exception):
    """Raised when a model lacks a required capability (e.g., thinking).

    Distinguished from transient model errors so the loop's poison counter
    doesn't punish deterministic config mismatches.
    """


class OllamaClient:
    """Thin wrapper around ollama.AsyncClient with capability detection.

    Capabilities are queried lazily on first chat() per model and cached
    for the lifetime of the client. The cache is per-instance (not global)
    so tests can isolate cleanly.
    """

    def __init__(self, host: str | None = None) -> None:
        self.host = host or SETTINGS.ollama_host
        self._aclient = ollama.AsyncClient(host=self.host)
        # model_name -> set of capability strings (e.g., {"completion", "tools", "thinking"})
        self._capabilities_cache: dict[str, set[str]] = {}
        self._cache_lock = asyncio.Lock()

    async def _get_capabilities(self, model: str) -> set[str]:
        """Return the model's capability set, querying Ollama once and caching."""
        if model in self._capabilities_cache:
            return self._capabilities_cache[model]

        async with self._cache_lock:
            # Re-check after acquiring lock (another caller may have populated)
            if model in self._capabilities_cache:
                return self._capabilities_cache[model]

            try:
                info = await self._aclient.show(model)
                caps_raw = (
                    info.get("capabilities") if isinstance(info, dict)
                    else getattr(info, "capabilities", None)
                )
                caps = set(caps_raw) if caps_raw else set()
            except Exception:  # noqa: BLE001 — show endpoint is best-effort
                # If we can't determine capabilities, assume the broadest set.
                # Better to attempt and surface the real error than to disable.
                caps = {"completion", "tools", "thinking"}

            self._capabilities_cache[model] = caps
            return caps

    async def supports_thinking(self, model: str) -> bool:
        return "thinking" in await self._get_capabilities(model)

    async def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        call_kind: CallKind = CallKind.DISPATCH,
        temperature: float = 0.3,
        num_ctx: int | None = None,
    ) -> dict[str, Any]:
        """Single chat turn. Returns the raw ollama response dict.

        ``think`` is only enabled when (a) the operator's policy wants it
        AND (b) the model advertises the ``thinking`` capability.
        """
        # Decide thinking flag
        want_think = _policy_wants_think(call_kind)
        send_think = want_think and await self.supports_thinking(model)

        opts: dict[str, Any] = {"temperature": temperature}
        if num_ctx is not None:
            opts["num_ctx"] = num_ctx
        elif SETTINGS.num_ctx:
            opts["num_ctx"] = SETTINGS.num_ctx

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "options": opts,
            "think": send_think,
        }
        if tools:
            kwargs["tools"] = tools

        response = await self._aclient.chat(**kwargs)
        return response if isinstance(response, dict) else response.model_dump()

    async def embed(self, *, model: str, prompt: str) -> list[float]:
        result = await self._aclient.embeddings(model=model, prompt=prompt)
        if isinstance(result, dict):
            return list(result["embedding"])
        return list(result.embedding)
