# Open Problems Registry — Updated
## Version 3.0: Post-White-Paper Revision

**Supersedes:** `open_problems.md` (v2.0)  
**Changes in this version:**
- OP4 CLOSED (radial scaling resolved — 1/R² confirmed)
- OP3 ESCALATED to Critical (α_screen audit reveals design-level blocker)
- OP10 ADDED: Signal size is indeterminate — coupling prefactor produces unphysical numbers
- OP11 ADDED: MICROSCOPE → κ̃ bound mapping needs explicit derivation
- OP6, OP7 updated with verification results

---

## STATUS SUMMARY TABLE

| ID | Description | Severity | Status |
|----|-------------|----------|--------|
| OP1 | G_eff formula dimensional error | Critical | ✅ RESOLVED (formula removed) |
| OP2 | κ̃ regulator justification | Critical | ✅ RESOLVED in framing (labeled hypothesis) |
| OP3 | α_screen Lindblad derivation | **Critical** | 🔴 ESCALATED — see below |
| OP4 | Δa(R) radial scaling | Critical | ✅ CLOSED — 1/R² confirmed |
| OP5 | PEIG coupled ODE system | Medium | 🔵 Open (not blocking) |
| OP6 | Verlinde citation year | High | ✅ RESOLVED — confirmed 2017 |
| OP7 | Kasevich configuration | High | ✅ PARTIALLY RESOLVED — 2020 PRL verified |
| OP8 | Bianchi identity compatibility | High | 🔵 Open |
| OP9 | Signal size sensitivity gap | Critical | 🔴 DEEPENED — see OP10 |
| OP10 | Coupling prefactor produces unphysical signal | **Critical** | 🆕 NEW |
| OP11 | MICROSCOPE → κ̃ bound derivation | High | 🆕 NEW |

---

## CLOSED PROBLEMS

### OP4 — CLOSED ✅
**Δa(R) derivation: 1/R² confirmed**

The correct formula is:
$$\Delta a(R) = -\frac{\tilde{\kappa} c^4}{8\pi k_B \ln 2} \cdot \frac{M_{\text{ent}}(<R)}{R^2}$$

where M_ent(<R) = 4π∫₀ᴿ ρ_ent(r) r² dr is the enclosed entanglement entropy. For R outside a compact source, this scales as 1/R². The 1/R formula in source documents was incorrect, implicitly requiring ρ_ent ∝ 1/r² — physically unmotivated.

Full derivation: `OP4_resolution_DeltaA_derivation.md`

### OP6 — CLOSED ✅
Verlinde citation corrected to 2017 throughout. Citation: SciPost Phys. 2, 016 (2017).

### OP7 — PARTIALLY CLOSED ✅
The 2020 Kasevich PRL paper is verified: Eötvös parameter η measured at the 10⁻¹² level, per-shot sensitivity ~1.4×10⁻¹⁰ m/s². The 2023 citation remains unverified and has been suspended. The δ|κ̃| = 3.7×10⁻¹³ claim based on the unverified 2023 sensitivity has been removed from the manuscript.

---

## ESCALATED PROBLEMS

### OP3 — ESCALATED TO CRITICAL 🔴

**Previous status:** High — phenomenological formula needs Lindblad derivation  
**New status:** Critical — the phenomenological formula gives α_screen ~ 10⁻⁴³ for the proposed macroscopic experiment

**What the audit found** (see `alpha_screen_audit.md`):

The Gaussian spatial suppression factor e^{-(R/ξ)²} in the phenomenological formula gives:
- For R = 100 μm, ξ = 1 μm: α_screen ~ exp(-10⁴) ~ 10⁻⁴³⁴³
- For R = 100 μm, ξ = 10 μm: α_screen ~ exp(-100) ~ 10⁻⁴³

The cited range [10⁻⁴, 10⁻²] corresponds to systems where R/ξ ~ 1–3, i.e., systems where the coherence length is comparable to the system size. This applies to few-qubit systems (10–100 qubits, R ~ ξ ~ 0.1–1 mm), not to macroscopic atomic ensembles.

**The consequence:** The experimental proposal as written (N = 10⁶ atoms, R ~ 0.1–1 mm) is targeting a regime where α_screen may be ~10⁻⁴³, making the signal undetectable by any conceivable technology.

**Paths to resolution:** See `alpha_screen_audit.md` — three scenarios, Scenario B (reformulate around 50–100 qubit NISQ systems) is the most immediately achievable.

---

## NEW PROBLEMS

### OP10 — NEW CRITICAL 🆕

**Signal size indeterminate: coupling prefactor produces unphysical numbers**

Even with α_screen = 10⁻⁴ (the optimistic estimate) and S_total = 50 bits (NISQ-scale), the Δa formula gives:

$$|\Delta a| = \frac{2.5 \times 10^{-4} \times 5 \times 10^{65}}{8\pi} \times \frac{50}{R^2} \sim 10^{62} / R^2 \text{ m/s}^2$$

For any laboratory-scale R, this is unphysically large. The coupling prefactor c⁴/(8πk_B ln 2) ≈ 5×10⁶⁵ generates signals that exceed any physical bound unless the effective coupling is suppressed to ~10⁻⁶⁵ or below.

**What this means:** The framework as currently formulated predicts signals that are either impossibly large (if α_screen is not ~10⁻⁶⁵) or immeasurably small (if α_screen is ~10⁻⁴³ from the spatial calculation). There is no regime where the predicted signal lands in the experimentally accessible range [10⁻¹⁵, 10⁻¹²] m/s² without a very specific combination of parameters that hasn't been identified.

**Three possible resolutions:**

1. **The formula is wrong at the Newtonian limit.** The modified Poisson equation may not be the correct Newtonian limit of the modified Einstein equation for an entanglement source term. The derivation of the Newtonian limit itself may need to be re-examined.

2. **The coupling constant κ̃ = −1/4 is a Planck-scale quantity.** The fact that c⁴/(8πGk_B ln 2) is ~10⁶⁵ is not a coincidence — it is because c⁴/G is the Planck energy density scale and k_B ln 2 is far below Planck energy. The "1/4" may be a ratio at the Planck scale that gets renormalized to a far smaller value at laboratory scales, similar to how gravity itself is ~10³⁸ times weaker than electromagnetism.

3. **The correct framework is non-perturbative.** The Newtonian limit may not be applicable — the entanglement correction to spacetime geometry may only be meaningful in a non-perturbative, fully quantum-gravitational context.

**Implication for submission:** Paper A can still be submitted as a theoretical framework paper — it does not need to predict a specific detectable signal to be a scientific contribution. The falsification criterion (null result with specific conditions) remains valid regardless of whether the signal is computable from current theory. The paper should simply be honest that the predicted signal magnitude is currently indeterminate.

### OP11 — NEW HIGH 🆕

**MICROSCOPE → κ̃ bound: mapping not derived**

The statement |κ̃| < 8×10⁻¹¹ from MICROSCOPE requires showing that a nonzero κ̃ would produce a composition-dependent gravitational anomaly. Both MICROSCOPE test masses are classical solids (Pt-Rh alloy and Ti-Al-V alloy). For classical solids at room temperature, S_ent ≈ 0 (no quantum entanglement between atoms). Therefore, the entanglement source term contributes equally (essentially zero) to both test mass trajectories — producing η ≈ 0 trivially, independent of κ̃.

**The κ̃ bound from MICROSCOPE may not be valid.** If both test masses have S_ent = 0, MICROSCOPE does not constrain κ̃ at all. The bound should be removed from Table 7.1 of Paper A unless the mapping argument is supplied explicitly.

---

## SUBMISSION DECISION TREE

```
Paper A submission readiness:

OP4 closed? YES ✅
  → Δa formula is correct (1/R²)
  
OP6, OP7 resolved? YES (partially) ✅
  → Use Verlinde 2017 and Kasevich 2020
  
OP10 resolved? NO 🔴
  → Cannot state a predicted signal magnitude
  → CAN state: "signal magnitude is indeterminate pending resolution of Planck-scale renormalization"
  → CAN submit if Section 05 is honest about this

OP3 (α_screen) resolved? NO 🔴  
  → Cannot design experiment targeting N=10⁶
  → CAN reformulate experiment targeting N=50-100 qubits
  → CAN submit if experimental section is reformulated

OP11 (MICROSCOPE mapping) resolved? NO 🔴
  → Remove MICROSCOPE bound from Table 7.1 OR supply the argument

Bottom line: Paper A is submittable with:
1. Section 05 reformulated around 50-100 qubit experiment
2. Signal magnitude stated as "indeterminate, bounded by falsification criterion"  
3. MICROSCOPE row removed or justified in Table 7.1
4. δ|κ̃| = 3.7×10⁻¹³ claim removed (was based on unverified inputs)

Papers B and C: NO blocking issues → ready to submit
```
