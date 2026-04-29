# Open Problems Registry
## Monette Research Repository — Complete Audit of Unresolved Issues

**Version:** 2.0 (includes OP9 discovered during Task 2 analysis)  
**Folder:** `02_MATHEMATICAL_CORRECTIONS/`  
**Status:** Living document — updated as problems are resolved or discovered  
**Purpose:** Intellectual honesty. Every gap, every missing derivation, every potentially wrong number is listed here. A physicist reading the core papers should be able to come here and find an honest accounting of what is not yet settled.

---

## HOW TO READ THIS DOCUMENT

Each entry specifies:
- **Severity:** Critical (blocks submission) / High (should be resolved before submission) / Medium (important but not blocking) / Low (housekeeping)
- **Status:** Open / In progress / Resolved (with resolution location)
- **What is needed:** The precise mathematical or empirical work required to close the problem

---

## OP1 — Emergent G Formula: Dimensionally Incorrect

**Severity:** Critical (resolved — formula removed)  
**Status:** Resolved  
**Original claim (FormulasRefined.pdf, Eq. 5):**

$$G_{\text{eff}} \sim \hbar c \left|\nabla\left(\frac{S_{\text{ent}}}{V}\right)\right|$$

**Why wrong:** Dimensional analysis gives [ℏc · m⁻⁴] = kg·m⁻¹·s⁻², not [G] = m³·kg⁻¹·s⁻². Off by kg²·m⁴.

**Resolution:** Formula removed from repository. Newton's G is treated as empirical input, not a derived quantity. The research program modifies the *source term* in Einstein's equations; it does not derive G.

**Remaining note:** An information-theoretic derivation of G from first principles remains an open problem in quantum gravity generally. It is not claimed or needed in this framework.

---

## OP2 — κ̃ = −1/4 Derivation: Unjustified Regulator

**Severity:** Critical (relabeled — not a blocking error if labeled correctly)  
**Status:** Resolved in framing; open as a derivation  
**Original framing:** "First-principles derivation yields κ̃ = −1/4"

**What is unjustified:** The step:
$$dS_{\text{ent}} = \frac{S_{\text{ent}}}{k_B} \cdot \frac{dV}{4\ell_P}, \quad dV = \ell_P \, dA$$

This uses the Planck length ℓ_P as a holographic regulator for laboratory-scale entanglement — borrowing from horizon physics without derivation.

**Resolution in repository:** Result relabeled as: "estimate under Planck-scale holographic regulator hypothesis." The word "derivation" removed. The result is retained because it is the unique value that falls out of the Clausius relation algebra under this hypothesis, and the hypothesis is physically motivated even if unproven.

**What would close this:** A derivation from holographic renormalization group theory showing that the ℓ_P regulator is valid for systems with volume-law entanglement entropy, not just area-law (horizon) systems. This is an active area of quantum gravity research and would constitute a significant independent contribution.

---

## OP3 — Screening Factor α_screen: Phenomenological Ansatz Without Derivation

**Severity:** High  
**Status:** Open  

**Current formula:**
$$\alpha_{\text{screen}} = \frac{1}{1 + (\Gamma \tau_D)^2} \cdot e^{-(R/\xi)^2}$$

**What is missing:**
1. No derivation from Lindblad master equation for any physical system
2. Parameters Γ, τ_D, ξ not expressed in terms of measurable quantities for ⁸⁷Rb or superconducting qubits
3. Range [10⁻⁴, 10⁻²] is physically plausible but not computed

**What is needed:**
Solve the Lindblad equation:
$$\dot{\rho} = -\frac{i}{\hbar}[H, \rho] + \sum_k \gamma_k \left(L_k \rho L_k^\dagger - \frac{1}{2}\{L_k^\dagger L_k, \rho\}\right)$$
for the specific jump operators L_k appropriate to:
- ⁸⁷Rb atoms at 1 nK in an optical dipole trap (dominant decoherence: off-resonant scattering, trap vibration)
- Superconducting transmon qubits (dominant: 1/f flux noise, quasiparticle poisoning)

The output should be: Γ(B, T, n) and ξ(B, T) as functions of magnetic field B, temperature T, and atom number n, yielding α_screen as a computable prediction.

**Blocking for:** Strong experimental prediction. Can submit with α_screen labeled as phenomenological and the range [10⁻⁴, 10⁻²] as estimate.

---

## OP4 — Δa(R) Formula: Unverified Derivation, 1/R vs. 1/R² Discrepancy

**Severity:** Critical (blocks experimental proposal as stated)  
**Status:** Open — sketch exists, final form unresolved  

**Current formula in source documents:**
$$\Delta a(R) = \frac{3\tilde{\kappa} c^4 S_{\text{ent}}}{16\pi G k_B \ln 2 \cdot \rho_{\text{Rb}} R}$$

**The discrepancy:** The derivation sketch in the master paper gives:
$$\Delta a(R) \propto \frac{S_{\text{total}}}{R^2}$$
from the shell theorem applied to the modified Poisson equation. The source formula has 1/R, not 1/R². One of these is wrong; the discrepancy has not been resolved.

**What is needed:**
1. State the specific density profile of S_ent(r) within the atomic ensemble
2. Write the modified Poisson equation: ∇²Φ = 4πGρ_matter + [κ̃c⁴/(2k_B ln 2)]∇²S_ent
3. Solve for the Newtonian potential Φ(R) outside the sphere
4. Compute Δa = -dΦ_ent/dR
5. Verify the numerical prefactors (the factors of 3 and 16π)

This is an undergraduate-level PDE problem once the density profile is specified. It should take approximately one careful afternoon to resolve.

**Blocking for:** Publication. The experimental proposal stands on Eq. (6.1) of the master paper. If that equation is wrong by a factor of R, the predicted signal is off by several orders of magnitude at the experimental scales being considered.

---

## OP5 — PEIG Coupled ODE System: Never Written

**Severity:** Medium (not blocking for physics papers; relevant for PEIG as independent contribution)  
**Status:** Open  

Only the Identity equation exists:
$$\frac{dI}{dt} = \alpha E - \beta I$$

**What is needed:** The full coupled system:
$$\frac{dP}{dt} = f_P(P, E, I, G; \lambda)$$
$$\frac{dE}{dt} = f_E(P, E, I, G; \lambda)$$
$$\frac{dI}{dt} = \alpha E - \beta I$$
$$\frac{dG}{dt} = f_G(P, E, I, G; \lambda)$$

Without this, PEIG cannot be simulated, analyzed for fixed points, compared to data, or falsified as a dynamical claim.

**Suggested approach:** The physical PEIG version (quantum systems) can borrow functional forms from:
- Open quantum systems theory (Lindblad gives f_E)
- Thermodynamic geometry (metric flow gives f_P)
- General relativity (stress-energy coupling gives f_G)

The cognitive PEIG version would need to be grounded in empirical social/cognitive science literature.

---

## OP6 — Verlinde (2025) Citation: Unverified

**Severity:** High (must resolve before arXiv submission)  
**Status:** Open  

**Current citation:** E. Verlinde, SciPost Phys. 2, 016 (2025)

**The problem:** SciPost Physics volume 2 was published in 2017, not 2025. This citation cannot be correct as written. Possible explanations:
1. Verlinde published a 2017 paper in SciPost Phys. 2 and the year is wrong in the source documents
2. There is a 2025 Verlinde paper in a different journal
3. The citation is confabulated

**The 2017 Verlinde paper (likely intended):** E. Verlinde, "Emergent Gravity and the Dark Universe," SciPost Phys. 2, 016 (2017). This is a real and highly cited paper directly relevant to the framework.

**Resolution needed:** Author should verify which Verlinde paper is being cited and what specific result supports the claim being made. If Verlinde 2017 is correct, update the year throughout. If a 2025 paper exists, verify its publication details.

**Blocking for:** arXiv submission. A wrong citation year will be caught immediately by reviewers and signals careless scholarship.

---

## OP7 — Kasevich et al. (2023) Sensitivity Claim: Configuration Unspecified

**Severity:** High  
**Status:** Open  

**Current citation:** J.M. Kasevich et al., Nature Phys. 19, 152 (2023) with claimed sensitivity δa = 1.2 × 10⁻¹² m/s²

**The problem:** The sensitivity 1.2 × 10⁻¹² m/s² applies to a specific experimental configuration. The paper should specify:
- Atom species and number used to achieve this sensitivity
- Integration time
- Whether this is single-shot or averaged
- How this configuration maps onto the proposed entanglement gravity experiment

**Resolution needed:** Author should read the Kasevich (2023) paper directly and confirm that the 1.2 × 10⁻¹² m/s² figure applies to a configuration compatible with the proposed GHZ-state experiment.

---

## OP8 — Bianchi Identity Compatibility: Anomalous Force on Matter

**Severity:** High  
**Status:** Open  

**The issue:** The contracted Bianchi identity requires ∇^μ G_μν = 0, which forces:
$$\nabla^\mu T_{\mu\nu}^{\text{matter}} = -\frac{\tilde{\kappa} c^4}{8\pi G \, k_B \ln 2} \nabla_\nu S_{\text{ent}}$$

This predicts that ordinary matter is not independently energy-momentum conserved when S_ent has a spatial gradient. This is a non-trivial prediction that needs to be shown compatible with precision tests.

**Three resolution paths:**
1. **Show it is negligible:** Estimate the right-hand side for typical laboratory S_ent gradients and show it is below current precision test bounds (most likely path)
2. **Acknowledge as prediction:** The anomalous force is itself a testable prediction — S_ent gradients should produce detectable forces on standard matter
3. **Reformulate:** Modify the theory so that ∇^μ(S_ent g_μν) = 0 is separately satisfied

**What is needed:** Numerical estimate of ∇_ν S_ent for the proposed experiment; comparison with solar system and atomic physics precision bounds on violations of energy-momentum conservation.

---

## OP9 — Sensitivity Gap: 75-Order Magnitude Error in Engineering Claims [NEW — discovered Task 2]

**Severity:** Critical for engineering section; does not affect core physics papers  
**Status:** Open (speculative section already labeled, but the specific numerical error should be documented)  

**What was discovered in Task 2:** The source documents claiming "70 Newtons repulsive force" from the basketball-sphere scenario were using the full ideal coupling κ̃ = −1/4 combined with 10¹⁸ qubits, without accounting for:
1. The environmental screening factor α_screen ∈ [10⁻⁴, 10⁻²] — reduces signal by 4–5 orders of magnitude
2. The unresolved OP4 discrepancy (1/R vs. 1/R²) — could reduce by up to ~10 additional orders depending on geometry
3. The unresolved OP3 — α_screen may be far smaller than [10⁻⁴, 10⁻²] for macroscopic systems

**The combined effect:** The actual predicted force from the basketball sphere, using conservative estimates for all uncertainties, is likely 10⁷⁰–10⁸⁰ Pa smaller than the source documents claimed. This is not a rounding error — it is a structural error in the engineering analysis.

**Resolution:** The basketball-sphere scenario in `04_SPECULATIVE_EXTENDED/gravity_engineering_scenarios.md` is already labeled [SPECULATIVE] and explicitly states: "OP4 must be resolved before any force number can be reliably cited." The 70-Newton figure has been removed from the repository. However, this problem should be tracked explicitly because the 70-Newton claim has propagated through multiple source documents and should not appear in any future version of this work without the full derivation.

**What is needed:** Once OP3 and OP4 are resolved, a complete numerical estimate of the force from the basketball-sphere scenario, derived end-to-end from the modified Einstein equation with realistic α_screen, should be computed and presented honestly regardless of how small it is.

---

## RESOLUTION PRIORITY TABLE

| ID | Description | Severity | Blocks submission? | Estimated effort |
|----|-------------|----------|-------------------|-----------------|
| OP1 | G_eff formula | Critical | No (resolved) | Done |
| OP2 | κ̃ regulator | Critical | No (relabeled) | PhD thesis to close properly |
| OP3 | α_screen derivation | High | Partial | 2–4 weeks (quantum optics calc) |
| OP4 | Δa(R) formula | **Critical** | **Yes** | 1–3 days (careful PDE work) |
| OP5 | PEIG coupled ODE | Medium | No | 1–2 months |
| OP6 | Verlinde citation | **High** | **Yes** | 1 hour (verify paper) |
| OP7 | Kasevich configuration | High | Yes | 1–2 hours (read paper) |
| OP8 | Bianchi identity | High | Yes | 1 week (estimate + comparison) |
| OP9 | Sensitivity gap (engineering) | Critical (speculative section) | No (section labeled) | Follows from OP3+OP4 |

---

## WHAT CAN BE SUBMITTED NOW

With OP6 and OP7 verified by the author (simple literature checks), and OP4 resolved (one careful calculation), **Paper A (Entropic Gravity)** is submittable to arXiv in its current form with:
- κ̃ = −1/4 labeled as estimate (OP2 resolved in framing)
- α_screen labeled as phenomenological (OP3 acknowledged)
- Δa(R) formula with derivation pending (OP4 must be resolved first)
- Bianchi identity tension acknowledged as prediction (OP8)

**Paper B (Constraint Manifolds)** has no blocking open problems. It can be submitted now once OP6/OP7 are verified (if cited there).

**Paper C (Landauer ETI)** has no blocking open problems. It can be submitted now.

---

*Last updated: March 2026. This document should be updated whenever a problem is resolved or a new problem is identified.*
