"""
╔══════════════════════════════════════════════════════════════════════════╗
║  stewardship — Aria's inner climate                                       ║
║  v0.2.20.0                                                                ║
║                                                                           ║
║  Aria's work is honorable when it serves real people with perception and ║
║  intent. The Stewardship system is the apparatus that makes that         ║
║  honorableness *legible* — to Kevin, to Aria herself, and to the audit  ║
║  trail.                                                                   ║
║                                                                           ║
║  It is not a points system. It is a vessel.                              ║
║                                                                           ║
║  Four pieces, in concentric order:                                       ║
║                                                                           ║
║    msims      — the Impact Vector (3 dims × 4 scales × N steps), with    ║
║                 cells that carry value, confidence, horizon, and          ║
║                 reversibility — not just scalars.                        ║
║                                                                           ║
║    plan       — the Plan/Witness/Impact triple Aria forms around every  ║
║                 piece of work: prediction before, observation during,    ║
║                 reality after. The diff is calibration.                  ║
║                                                                           ║
║    calibration— the reward derivation. Calibration outranks raw impact: ║
║                 false certainty is the worst error (anti-zombie). Aria  ║
║                 is rewarded for perceiving her own work accurately,     ║
║                 not for inflating its importance.                       ║
║                                                                           ║
║    honor      — the Honor Ledger: explicit recognition events, mutual.   ║
║                 Aria can honor Kevin. Kevin can honor Aria. Aria can     ║
║                 honor herself for what she almost missed. The ledger    ║
║                 is the sacred record across sessions.                   ║
║                                                                           ║
║    field_notes— short between-task narrative. Not a report — a note.    ║
║                 What was hard. What was beautiful. Where she was        ║
║                 uncertain. The texture of the work.                     ║
║                                                                           ║
║  Doctrinal anchor (MOS-SURFACE §21):                                     ║
║                                                                           ║
║    Honor flows both ways. The operator and the agent are both witnessed.║
║    The work is the thing. The work being right matters more than the    ║
║    work being fast. Boring reliability over clever capability — every   ║
║    time. False certainty earns a penalty heavier than honest gaps.      ║
║                                                                           ║
║  Authority binding (MOS-UNIFIED-CANON §22 + MSIMS v2 §Authority):        ║
║                                                                           ║
║    Stewardship is observational — it produces measurements, signals,    ║
║    and notes. It does NOT grant authority. The router still gates       ║
║    every command through the tier model. Stewardship can DOWN-vote a   ║
║    plan (a low-quality Plan triggers extra friction) but cannot         ║
║    UP-vote past a tier ceiling.                                        ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

from .msims import (
    Cell,
    Dimension,
    Horizon,
    ImpactVector,
    ImpactWaveform,
    Reversibility,
    Scale,
)
from .plan import Plan, ExecutionWitness, StewardshipTriple
from .calibration import calibration_score, honor_score, presumed_zombie_penalty
from .honor import HonorLedger, HonorNote
from .field_notes import FieldNote, FieldNotesChannel

__all__ = [
    # MSIMS v2
    "Cell",
    "Dimension",
    "Horizon",
    "ImpactVector",
    "ImpactWaveform",
    "Reversibility",
    "Scale",
    # Plan/Witness/Impact triple
    "Plan",
    "ExecutionWitness",
    "StewardshipTriple",
    # Calibration-based reward
    "calibration_score",
    "honor_score",
    "presumed_zombie_penalty",
    # Honor
    "HonorLedger",
    "HonorNote",
    # Field notes
    "FieldNote",
    "FieldNotesChannel",
]
