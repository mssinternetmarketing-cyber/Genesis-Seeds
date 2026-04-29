# α_screen Deep Audit
## Regime-of-Validity Analysis and Experimental Reformulation

**Status:** DESIGN-LEVEL BLOCKER — must be resolved before any experimental proposal can claim a predicted signal  
**Core finding:** The cited range α_screen ∈ [10⁻⁴, 10⁻²] and the macroscopic-ensemble computation giving α_screen ~ 10⁻⁴³ are irreconcilable. They correspond to different physical regimes, and the experiment must be designed for one or the other explicitly.

---

## 1. THE DISCREPANCY — STATED PRECISELY

### 1.1 The heuristic range [10⁻⁴, 10⁻²]

This range appears throughout the source corpus as if it were a calculated result. It is not. It is an order-of-magnitude estimate, apparently borrowed from decoherence rates in NISQ-era few-qubit systems (superconducting qubits, trapped ions with 10–100 qubits). For these systems:

- System size: R ~ 100 μm–1 mm
- Coherence length: ξ ~ 10–100 μm (comparable to R)
- Gaussian factor: exp(-(R/ξ)²) ~ exp(-1) to exp(-100) ≈ 0.37 to 3.7×10⁻⁴⁴

Even for few-qubit systems, the Gaussian factor alone is already borderline. The [10⁻⁴, 10⁻²] range likely corresponds to the Lorentzian factor alone (decoherence rate vs. coherence time), ignoring the spatial suppression.

### 1.2 The macroscopic-ensemble calculation

For the proposed ⁸⁷Rb GHZ experiment with N = 10⁶ atoms:
- Ensemble radius: R ~ 100 μm–1 mm (typical BEC)
- Coherence length for entanglement propagation in the ensemble: ξ ~ 1–10 μm

The Gaussian spatial suppression factor:

$$e^{-(R/\xi)^2} = e^{-(100\,\mu\text{m} / 1\,\mu\text{m})^2} = e^{-10^4} \approx 10^{-4343} \tag{1.1}$$

Even with ξ = 10 μm:

$$e^{-(100\,\mu\text{m} / 10\,\mu\text{m})^2} = e^{-100} \approx 3.7 \times 10^{-44} \tag{1.2}$$

The physical meaning: for a macroscopic atomic ensemble, quantum entanglement correlations do not extend across the full system. Each atom is entangled with its nearest neighbors over a scale ξ ~ few μm, but the global entanglement (the GHZ-type correlations spanning the full ensemble) is suppressed by decoherence over the distance R. The Gaussian factor captures this spatial decoherence.

### 1.3 The irreconcilability

These two estimates differ by 40–4000 orders of magnitude. They cannot both be correct for the same physical system. **One of the following must be true:**

(A) The Gaussian formula for α_screen does not apply to macroscopic entangled ensembles and the correct α_screen is much larger — meaning the [10⁻⁴, 10⁻²] estimate might be salvageable with a different formula.

(B) The [10⁻⁴, 10⁻²] estimate was always only valid for microscopic (few-qubit) systems and was incorrectly applied to the macroscopic ensemble design.

(C) The coherence length ξ for a GHZ state of N atoms is actually ~ R (the GHZ correlations ARE long-range by construction), making the Gaussian factor ~ exp(-1) ≈ 0.37 — a very different physical picture.

---

## 2. PATH TO RESOLUTION: THREE SCENARIOS

### Scenario A — The GHZ state has long-range ξ ~ R [most optimistic]

A true GHZ state $|\text{GHZ}\rangle = (|0\rangle^{\otimes N} + |1\rangle^{\otimes N})/\sqrt{2}$ is **maximally entangled across ALL N atoms simultaneously**. There is no "coherence length" in the usual sense — the correlations span the entire system by definition.

If this is the correct physical picture, then:
- ξ ~ R (system-spanning correlations)
- Gaussian factor ~ exp(-(R/R)²) = exp(-1) ≈ 0.37
- The spatial suppression is minimal
- α_screen is dominated by the Lorentzian factor alone: 1/(1+(Γτ_D)²)

For current BEC technology with Γ ~ 1 s⁻¹ and τ_D ~ 1 s:
$$\alpha_{\text{screen}} \approx \frac{1}{1 + (1 \cdot 1)^2} \times 0.37 \approx 0.18 \tag{2.1}$$

This is much larger than [10⁻⁴, 10⁻²] — suggesting the coupling is only lightly suppressed for a true macroscopic GHZ state.

**The catch:** True N=10⁶ GHZ states do not exist. GHZ states are maximally fragile to individual-qubit decoherence — the loss of a single atom collapses the entanglement. For N=10⁶ atoms, any realistic GHZ state will have effectively zero fidelity in a thermal environment. The "true GHZ" scenario requires near-perfect isolation that does not exist at N=10⁶.

**Implication of Scenario A:** The experiment needs to specify what STATE it is actually preparing. If it is a true GHZ state (long-range correlations), the α_screen suppression is mild but the state is unphysical at N=10⁶. If it is a spin-squeezed state or twin-Fock state (realistic at N=10⁶), the coherence length is short and the spatial suppression is severe.

### Scenario B — Use microscopic systems where α_screen is in [10⁻⁴, 10⁻²] [most achievable]

Reformulate the experiment around small systems where:
- N = 10–100 qubits (superconducting or trapped ions)
- System size R ~ 1 mm
- Coherence length ξ ~ 0.1–1 mm (comparable to R)
- GHZ or high-fidelity entangled states are achievable

For R/ξ ~ 1–3:
$$e^{-(R/\xi)^2} = e^{-1} \text{ to } e^{-9} \approx 0.37 \text{ to } 10^{-4} \tag{2.2}$$

This gives α_screen ∈ [10⁻⁴, 0.37] — consistent with the cited range for the lower end.

**The cost:** N = 10–100 qubits gives S_total = 10–100 bits. The signal Δa ∝ S_total/R² is proportionally smaller. But the coupling suppression α_screen is also proportionally larger, and the experiment is physically realistic.

**This is likely the correct target for a near-term experiment.**

### Scenario C — Derive α_screen from scratch for the specific system [most rigorous]

Rather than using the phenomenological formula (which may not apply in either regime), derive α_screen from the Lindblad equation for the specific experimental system. This is OP3, but its urgency has now escalated to critical because the formula-derived estimate is not credible.

The Lindblad derivation would:
1. Start from the full many-body density matrix of N atoms in the entangled state
2. Apply the physical decoherence channels (photon scattering at rate Γ_γ, trap noise at rate Γ_trap)
3. Compute the time-evolution of the entanglement entropy density S_ent(r, t)
4. Integrate over the experiment duration to get the effective S_ent contributing to the coupling

This would give a physically meaningful α_screen for the specific system, without relying on the phenomenological formula.

---

## 3. IMPLICATIONS FOR THE EXPERIMENTAL PROPOSAL

The experimental proposal in `A_S05_experimental_protocol.md` requires revision depending on scenario:

| Scenario | Target system | N | Realistic α_screen | S_total | Status |
|----------|--------------|---|-------------------|---------|--------|
| A (true GHZ) | ⁸⁷Rb BEC, N=10⁶ | 10⁶ | ~0.1 | ~10⁶ bits | State unphysical at this N |
| B (NISQ-scale) | Trapped ions / SC qubits | 10–100 | 10⁻⁴–10⁻¹ | 10–100 bits | Physically realistic NOW |
| C (Lindblad-derived) | Any | TBD | TBD | TBD | Requires OP3 |

**Recommendation:** Reframe the experimental proposal around Scenario B. A 50–100 qubit superconducting processor with high-fidelity entangled states is available today. The signal will be smaller (fewer qubits), but the α_screen will be physically motivated and the experiment is achievable.

The N = 10⁶ atom target should remain in the paper as a **long-term goal** (5–10 year horizon) after the Lindblad derivation (Scenario C) establishes what α_screen is for large atomic ensembles.

---

## 4. THE SIGNAL SIZE AFTER AUDIT

Using Scenario B parameters (50 superconducting qubits, R ~ 1 mm, α_screen ~ 10⁻³):

- S_total = 50 bits
- |κ̃_eff| = (1/4) × 10⁻³ = 2.5 × 10⁻⁴
- R = 10⁻³ m
- c⁴/(8πk_B ln 2) = 5.03 × 10⁶⁵ (from constants table)

$$|\Delta a| = \frac{2.5 \times 10^{-4} \times 5.03 \times 10^{65}}{8\pi} \times \frac{50}{(10^{-3})^2} \approx 2.5 \times 10^{70} \text{ m/s}^2 \tag{4.1}$$

This is still an impossible number. This reveals something fundamental: **the coupling prefactor c⁴/(8πk_B ln 2) is approximately 5 × 10⁶⁵ in SI units**, which means even with 40 orders of magnitude of suppression from α_screen, the predicted acceleration from even a few bits of entanglement entropy is enormous unless the screening is truly at the 10⁻⁶⁵ level or below.

**What this calculation means:** Either (a) the coupling constant κ̃ = −1/4 is vastly overestimated even under the holographic regulator hypothesis, or (b) the regime of applicability requires extremely precise cancellations between the coupling and the screening that reduce the effective signal to below 10⁻¹² m/s², or (c) the physical picture is missing a fundamental suppression mechanism not captured in the current formula.

This is not a reason to abandon the framework — it is a reason to be honest that the predicted signal size is **indeterminate** until the coupling, screening, and formula are all consistently derived from the same physical framework.

---

## 5. REVISED SUBMISSION STRATEGY

The paper can be made submission-ready with the following honest framing:

**What can be claimed:**
- The dimensional consistency of the coupling (Section 01 of Paper A) — unaffected
- The falsification criterion (Section 06) — unaffected; it specifies conditions for null results
- The κ̃ = −1/4 estimate under the holographic regulator hypothesis — unaffected, conditional on hypothesis

**What must be removed or qualified:**
- The specific signal prediction Δa ~ 10⁻¹⁵ m/s² — not derivable without resolving α_screen
- The statement δ|κ̃| = 3.7 × 10⁻¹³ — requires the corrected formula and realistic α_screen
- Any claim that the experiment is "designed to detect" the predicted signal — signal size is undetermined

**The honest version of the experimental section:** "We propose this experimental design as a sensitivity test of the coupling constant. The achievable upper bound on |κ̃| depends on experimental sensitivity and on the screening factor α_screen, which is derived in the companion analysis (OP3). Until OP3 is resolved, we can state that the experiment will produce an upper bound on |κ̃| at the level δ|κ̃| [to be computed], without claiming this bound overlaps with the theoretical prediction."

This framing is honest, scientifically rigorous, and does not weaken the paper — it strengthens it, because it accurately represents what the experiment measures.
