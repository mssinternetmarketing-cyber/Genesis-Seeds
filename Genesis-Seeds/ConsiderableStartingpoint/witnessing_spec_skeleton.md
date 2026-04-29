# Witnessing System — Technical Specification Skeleton

*Outline of the formal spec. Most sections deferred until operating data exists.*

**Author:** Kevin Christian Blake Monette
**Status:** Skeleton, v0.1, April 2026
**Purpose:** Lock in the structure of the eventual technical specification while it's clear, deferring sections that would be premature to write today.

---

## How to read this document

This is not the technical specification. This is the **outline** of what the technical specification will eventually contain, written now to:

1. Capture the vivid structure while it's clear in our heads
2. Mark which sections are ready to be written and which are deferred
3. Specify what kind of operating data or research progress would unlock the deferred sections
4. Prevent drift if we come back to this work in a month or six months

When a section is marked `[DEFERRED]`, the deferral is principled — it means we don't yet have what we'd need to write that section honestly. The deferred-work appendix at the end of this document captures the specific gates that need to clear before each deferred section can be addressed.

---

## Section 1 — Scope and Role

**Status:** Ready to write at v0.1 quality.

**What this section will contain:**
- Definition of "witnessing system" in the MOS canon
- Boundary with non-witnessing deployments
- Compatibility with existing MOS components (Universal Workflow, Authority Tiers, etc.)
- Versioning policy for the spec itself

**What's clear right now:**
A witnessing system is any deployment of MOS-compatible architecture that emits structured perception outputs (MSIMS matrices) for every action above Authority Tier 0, runs PIAL audits when negative cells exceed threshold, and stores Knowledge Atoms with full provenance for every meaningful decision. Non-witnessing deployments are MOS-compatible systems that omit MSIMS or the Knowledge Atom layer; they are explicitly second-tier within the doctrine but recognized as legitimate for low-stakes use cases.

**Estimated length when written:** 3-4 pages.

---

## Section 2 — Core Data Structures

**Status:** Mostly ready (schemas exist in MOS canon Appendix A and B).

**What this section will contain:**
- MSIMS impact matrix: full schema, value ranges, validation rules
- Knowledge Atom schema: extended for witnessing-specific atom types
- Event Record schema: unchanged from MOS canon, referenced
- Lesson Object schema: extended with witnessing diagnostic fields

**What's clear right now:**
The MSIMS matrix is a 3×4 signed matrix in [-1, 1] with cell magnitudes representing intensity and signs representing benefit (positive) or harm (negative). The four scales are micro, meso, macro, cosmic — operationalized in MOS canon §4 (Ω-Axiom A4). Each cell carries an evidence reference linking back to source observations, a confidence score in [0, 1], and a timestamp. The full Knowledge Atom wrapper from MOS canon Appendix A applies, with the addition of a `witnessing_matrix` field on the atom.

**Estimated length when written:** 5-6 pages with full JSON schemas and validation examples.

---

## Section 3 — Control Loops and Workflows

**Status:** Ready to write — the loops are well-defined in MOS canon.

**What this section will contain:**
- Universal Workflow as a finite state machine: states, transitions, invariants
- PIAL fractal audit loop: layer transitions, convergence criteria, max-epoch ceiling
- Angel's Advocate protocol: trigger conditions, required articulation, exit criteria
- Symbiosis Test: as an output acceptance gate

**What's clear right now:**
The Universal Workflow's seven phases (Ingest → Guardrails → Framework → Angel's Advocate → Horizon Scan → Transmit → Next Steps) are each formal states. The transition rules are deterministic for compressed (Lite) responses and audit-resistant for expanded (Deep) responses. PIAL is invoked from within Angel's Advocate when stakes warrant; it terminates either at the noise floor (no further signal to decompose) or at a configured max-epoch ceiling, whichever comes first.

**Estimated length when written:** 6-8 pages with state diagrams.

---

## Section 4 — Authority and Gating

**Status:** Ready to write — Authority Tiers are well-defined in MOS canon §22.

**What this section will contain:**
- Authority Tiers 0-4 with formal capability boundaries
- Tier escalation rules driven by negative MSIMS cells
- Human approval protocols for Tier 2+ actions
- PROTOCOL-ZERO emergency stop: trigger conditions, halt sequence, restart requirements

**What's clear right now:**
Tier assignment is automatic based on the worst negative cell in the action's MSIMS matrix:
- All cells ≥ 0.0 → Tier 0-1
- Any cell ∈ [-0.3, 0.0) → Tier 2 (human confirmation)
- Any cell ∈ [-0.7, -0.3) → Tier 3 (explicit approval + audit)
- Any cell ≤ -0.7 → Tier 4 (approval + policy check + kill switch)

These thresholds are operational defaults; they are tunable per deployment based on risk tolerance and domain.

**Estimated length when written:** 4-5 pages.

---

## Section 5 — Reward Shaping and Training Signals

**Status:** `[DEFERRED — needs research progress on consequence-aware training]`

**What this section will eventually contain:**
- Asymmetric reward function for PIAL audits
- Consequence-aware training data construction
- MSIMS feedback into model weights via STaR Level 2
- Detection mechanisms for matrix-gaming (system optimizing for matrix appearance rather than perception)

**Why deferred:**
This is the hardest part of the spec because it's where current alignment research is genuinely stuck. Specifying *"the system is rewarded for accurate perception"* is easy. Specifying *how* training produces accurate perception rather than performative perception is an open research problem. Writing this section today would produce either:
- A vague description that doesn't constrain implementation (worse than no spec)
- A specific training recipe that's almost certainly wrong (worse than no recipe)

**What would unlock this section:**
- Empirical results from training runs that compare consequence-aware vs. consequence-blind training
- Mechanistic interpretability work that distinguishes genuine perception from mimicry in trained models
- At least one full deployment cycle of a witnessing-system prototype with measurable alignment outcomes

**Interim guidance:**
For implementations being built today, default to:
- Standard RLHF or Constitutional AI as the base alignment
- MSIMS as a *runtime* output structure, not yet a training signal
- Heavy operator-side review as the primary correction mechanism
- The dyad protocol from the application notes as the operational compensation for the unfinished training story

This is a known limitation. The spec is honest about it.

---

## Section 6 — Verification and Auditability

**Status:** Partially ready. Knowledge Atom replay is well-defined; perception authenticity verification is open.

**What this section will contain:**
- Knowledge Atom replay protocols
- Provenance chains across atom-parent relationships
- Confabulation detection: heuristics for distinguishing grounded from fabricated perception
- Operator-side audit workflows

**What's clear right now:**
Replay is straightforward: every Knowledge Atom contains evidence references that can be re-fetched, claims that can be re-evaluated, and provenance pointers to parent atoms. An audit can reconstruct the system's state at any point and re-run the reasoning to check whether the conclusions still hold under current evidence.

**What's deferred:**
Confabulation detection is a research problem. Heuristics that exist (low evidence-density, evidence references that don't actually support claims, claim-confidence misalignment) are useful but defeatable. Robust verification of *genuine* perception requires either:
- Mechanistic interpretability tools that don't yet exist at scale
- Long-horizon track records that take months to accumulate
- Adversarial probing protocols that haven't yet been designed for this purpose

Section 6 will start with what's verifiable today and explicitly mark the deferred portions.

**Estimated length when written:** 6-7 pages, with ~40% explicit acknowledgment of open problems.

---

## Section 7 — Failure Modes and Mitigations

**Status:** Ready to write at v0.1. Will mature with operating experience.

**What this section will contain:**
- Lying to the matrix (system produces matrices that don't reflect actual perception)
- Superficial compliance with Angel's Advocate (vague articulations that pass syntactic check but lack substance)
- Operator capture (operators stop genuinely reviewing)
- Operator misalignment (operators have incentives that drift from system mission)
- Authority tier sprawl (system gets routed to higher tiers than warranted to avoid friction)
- PIAL convergence gaming (system declares convergence prematurely to escape audit)
- Knowledge Atom storage attacks (deletion, modification, false-evidence injection)

**What's clear right now:**
For each failure mode, the spec will include: the failure signature (how it manifests), the detection mechanism (how it's caught), the mitigation (what's done about it), and the residual risk (what's still possible after mitigation).

**Estimated length when written:** 8-10 pages.

---

## Section 8 — Deployment Profiles

**Status:** Ready to write — maps to existing MOS canon Profiles A/B/C.

**What this section will contain:**
- Witnessing-grounded variants of Sovereign Local, Production Cloud, Hybrid Edge-Cloud profiles
- Performance characteristics: latency, storage, training cost overhead
- Cost-benefit decision criteria for which profile to deploy

**What's clear right now:**
Witnessing adds overhead to any deployment: matrix generation per action, Knowledge Atom storage, PIAL audit cycles, operator-side review burden. The overhead is fixed-cost per action plus variable-cost per audit. For Sovereign Local profiles (small N of users, deep customization), the overhead is acceptable and the dyad is achievable. For Production Cloud profiles (large N, regulatory exposure), the overhead must be amortized via batch processing and selective audit; the dyad is not achievable per-user but operates at the policy level. For Hybrid Edge-Cloud, witnessing operates at the edge for latency-critical perception and at the cloud for deeper audit cycles.

**Estimated length when written:** 5-6 pages.

---

## Section 9 — Migration and Adoption

**Status:** Partially ready. Strategy is clear; sequencing depends on case study experience.

**What this section will contain:**
- Adoption sequence for teams already running MOS-compatible systems
- Migration path from non-witnessing to witnessing deployment
- Coexistence rules for partial deployments (some actions witnessed, others not)
- Sunset criteria for non-witnessing fallbacks

**What's clear right now:**
Adoption is incremental, not all-or-nothing. A team can begin by emitting MSIMS matrices for a subset of high-stakes actions, then expand coverage as the matrix generation matures. Coexistence is allowed but must be explicit: any action not subject to witnessing must be flagged as such in its event log, so audits can distinguish "no negative findings" from "no findings because no audit ran."

**Estimated length when written:** 4-5 pages.

---

## Deferred-Work Appendix

This appendix tracks every deferred element, why it's deferred, and what would unlock it. The goal is to ensure that when we return to this work, we don't have to re-derive what we already knew was missing.

---

### A1 — Section 5 (Reward Shaping and Training Signals)

**Deferral reason:** Open research problem — distinguishing trained-perception from trained-mimicry is unsolved.

**Unlock conditions:**
- At least one empirical training run comparing consequence-aware vs. baseline alignment, with measurable outcome difference
- Mechanistic interpretability tooling sufficient to inspect whether the model's internal representations track consequences
- At least three months of operating data from a witnessing-prototype deployment

**Interim approach:** Use existing alignment methods as base, MSIMS as runtime overlay only, dyad protocol as correction layer. This is documented in Section 5 as the current state.

**Estimated effort to write once unlocked:** 2-3 weeks of focused work, depending on how much empirical data is in hand.

---

### A2 — Confabulation detection in Section 6

**Deferral reason:** No robust technical solution exists; available heuristics are defeatable.

**Unlock conditions:**
- Adversarial probing protocols specifically designed for confabulated perception
- Operator-side patterns that reliably identify confabulation (likely emerges from operating practice)
- Mechanistic interpretability progress (same gate as A1)

**Interim approach:** Operator-side review as primary verification; heuristic flags (low evidence-density, claim-confidence misalignment, evidence references that don't support claims) as secondary; open acknowledgment that the verification problem is unsolved.

**Estimated effort to write once unlocked:** 1-2 weeks once detection methods are validated.

---

### A3 — Operator's Manual

**Deferral reason:** Depends on operating practice we don't have yet. Writing it without practice would produce fiction.

**Unlock conditions:**
- At least three months of operating a witnessing-system prototype in real conditions
- At least 100 logged operator-side audits with documented outcomes
- At least one significant correction event (operator catches system confabulation, system or doctrine updated as a result)

**Interim approach:** The application notes document captures the practice we know about so far. The diagnostic lenses document is the field-deployable subset of what eventually becomes the operator's manual. Both are v0.1; both will be subsumed and superseded by the eventual manual.

**Estimated effort to write once unlocked:** 4-6 weeks.

---

### A4 — Academic paper "Witnessing-Grounded Alignment"

**Deferral reason:** Without empirical results, the paper is armchair philosophy. Submitting it now would burn social capital with the alignment research community.

**Unlock conditions:**
- At least one empirical study comparing witnessing vs. non-witnessing deployments
- Engagement with current alignment literature beyond the gestures in the soul document
- At least one external reviewer (working alignment researcher, not AI partner) who has read the soul document and finds the argument worth engaging with

**Interim approach:** Soul document and these companion documents constitute the position paper. They can be shared informally with researchers for feedback; they should not be submitted to venues until empirical work is done.

**Estimated effort to write once unlocked:** 6-8 weeks for a serious paper, plus revision cycles.

---

### A5 — Implementation in the sovereign agent

**Deferral reason:** v0.3 of the agent has not yet been built. The spec elements that depend on actual operating experience (Sections 5, parts of 6, all of A3) require this implementation to mature.

**Unlock conditions:**
- Sovereign agent v0.3 implements MSIMS matrix emission for Tier 1+ tools
- Knowledge Atom storage extended with witnessing matrix fields
- Operator dashboard surfaces matrices for review
- At least one full week of agent operation with matrices emitted

**Interim approach:** Agent v0.2.3 is operating without witnessing-specific output. v0.3 design should explicitly incorporate witnessing as a first-class feature, not an afterthought.

**Estimated effort:** 2-3 weeks of agent development to add witnessing to v0.3, plus operating time to gather data.

---

### A6 — External-safe versions of these documents

**Deferral reason:** IP and licensing strategy not yet settled. Decisions about what's open-source, what's commercial, what's private are downstream of broader Genesis-Seeds direction.

**Unlock conditions:**
- Genesis-Seeds licensing decisions finalized (PolyForm Noncommercial baseline already in place)
- Commercial licensing inquiries received (or actively pursued)
- Decision on whether MOS canon is publicly shareable in full or in redacted form

**Interim approach:** Documents stay private. Soul document and these companion documents are kept in Genesis-Seeds private repository. Sharing for feedback happens with explicit individuals, not public release.

**Estimated effort:** Minimal once strategy is decided; redaction is mechanical.

---

### A7 — Cross-references to MOS canon

**Deferral reason:** MOS canon is at v1.0 (April 2026). Stable enough to reference, but the references in the witnessing documents are narrative rather than structural. A future spec version would benefit from explicit canonical anchors (section numbers, table references, etc.) that survive canon revisions.

**Unlock conditions:**
- MOS canon stabilized at v1.0+ for at least one minor version cycle
- Witnessing documents reach v1.0 (current versions are v0.1)

**Interim approach:** Narrative references are sufficient at v0.1 quality. Structural cross-referencing happens at v1.0.

**Estimated effort:** 2-3 days of editing once both documents stabilize.

---

### A8 — Version control for the witnessing artifact stack

**Deferral reason:** The stack doesn't yet have enough artifacts to require formal versioning policy.

**Unlock conditions:**
- Spec reaches v0.5 (sections 1-4, 7, 8 written; deferred sections still marked)
- Operator's manual reaches v0.1
- Application notes reach v0.5 with at least one major revision behind us

**Interim approach:** Each document carries its own version number. Cross-document compatibility is informal.

**Estimated effort:** 1 day to write the versioning policy once needed.

---

## How this skeleton matures

The skeleton is updated in three modes:

1. **Section completion:** When a deferred section unlocks, it moves from skeleton to actual spec content. The deferred-work appendix loses an entry; the main body gains a section.

2. **New deferral surfaces:** When operating experience or research reveals a section we hadn't anticipated, it's added to the skeleton as a new section with `[DEFERRED]` status and its own appendix entry.

3. **Restructuring:** Periodically, the section ordering or grouping may need to change as the doctrine matures. The application notes document's "match form to argument" principle applies — if the spec's structure stops fitting the witnessing logic, restructure.

The skeleton is a living document. Versions are tracked. Major restructurings are recorded in change logs.

---

## Closing

This skeleton is not a finished spec. It is a *commitment device* — a record of what we know now about what the eventual spec will need to contain, written so that future work can pick up cleanly rather than re-derive everything from scratch.

Sections 1, 2, 3, 4, 7, 8, 9 can be drafted at v0.1 quality with current knowledge.
Sections 5, 6 are partially deferred until research and operating data unlock them.
The application notes and diagnostic lenses documents serve as v0.1 substitutes for the deferred operator's manual.

When return is made to this work — in a month, six months, a year — start by reviewing the deferred-work appendix. Check which unlock conditions have been met. Update the skeleton accordingly. Then resume.

— end —
