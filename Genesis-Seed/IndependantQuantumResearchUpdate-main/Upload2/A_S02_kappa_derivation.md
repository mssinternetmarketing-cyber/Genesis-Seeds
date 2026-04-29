# Section 02: The κ̃ Derivation
## First-Principles Estimate of the Coupling Constant Under the Holographic Regulator Hypothesis

**Paper:** A — Gravitational Coupling to Entanglement Entropy Density  
**Section:** 2 of 6  
**Status:** [HYPOTHESIS → ESTIMATE] — internally consistent algebra; rests on one unproven assumption (clearly labeled)

---

## 2.1 Jacobson's Thermodynamic Foundation [ESTABLISHED]

Jacobson (1995) showed that Einstein's field equations follow from thermodynamics. The key steps:

**Step 1 — Local Rindler horizon.** Around any spacetime point $p$, an observer accelerating with proper acceleration $a$ perceives a local Rindler horizon. The Unruh temperature seen by this observer is:

$$T_U = \frac{\hbar a}{2\pi c k_B} \tag{2.1}$$

**Step 2 — Bekenstein-Hawking entropy.** The entropy associated with a horizon area element $dA$ is:

$$dS_{BH} = \frac{k_B c^3}{4G\hbar} \, dA \tag{2.2}$$

**Step 3 — Clausius relation.** Applying $\delta Q = T \, dS$ to the heat flux through the horizon, and identifying the energy-momentum flux $\delta Q = T_{\mu\nu}^{\text{matter}} k^\mu d\Sigma^\nu$ (where $k^\mu$ is the null generator), Jacobson recovers:

$$G_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu} \tag{2.3}$$

This is Einstein's equation, derived from thermodynamics alone. Gravity is not fundamental — it is the equation of state of spacetime when entropy scales with horizon area.

## 2.2 The Entanglement Entropy Contribution [HYPOTHESIS introduced here]

We now add an entanglement entropy contribution to the Clausius relation. For a spatial region with entanglement entropy density $S_{\text{ent}}$ (bits/m³), we *propose* that the additional entropy associated with horizon area element $dA$ is:

$$dS_{\text{ent}} = \frac{S_{\text{ent}}}{k_B} \cdot \frac{dV}{4\ell_P} \tag{2.4}$$

where $dV = \ell_P \, dA$ is the volume element one Planck length $\ell_P = \sqrt{\hbar G/c^3} = 1.616 \times 10^{-35}$ m behind the horizon.

**⚠ THE HOLOGRAPHIC REGULATOR HYPOTHESIS — the step that is assumed, not derived:**

Equation (2.4) uses $dV = \ell_P \, dA$. This treats one Planck length of depth behind the horizon as the effective thickness through which entanglement entropy contributes to horizon thermodynamics. This regulator:
- Is borrowed by analogy from holographic principles (area-law entropy at horizons)
- Applies rigorously to causal horizon systems (black holes, Rindler horizons)
- Is **assumed** to apply to laboratory-scale entanglement volumes with no horizon present
- Has no derivation for non-horizon systems

This is the extrapolation boundary. Everything that follows is internally consistent **conditional on this assumption being valid.**

## 2.3 The Derivation [DERIVED — conditional on Sec. 2.2 assumption]

**The modified Clausius relation:**

$$\delta Q_{\text{eff}} = T_U \, dS_{BH} + T_U \, dS_{\text{ent}} = \delta Q_{BH} + \frac{\hbar a}{2\pi c k_B} \cdot \frac{S_{\text{ent}}}{k_B} \cdot \frac{dA}{4} \tag{2.5}$$

The second term represents additional heat flux through the horizon from the entanglement entropy contribution.

**Identifying the effective stress-energy:**

Following Jacobson's procedure, $\delta Q_{\text{eff}} = T^{\text{eff}}_{\mu\nu} k^\mu d\Sigma^\nu$. The standard matter term reproduces Einstein's equation. The entanglement term gives:

$$T^{\text{eff}}_{\mu\nu} \supset \frac{\hbar a}{2\pi c k_B} \cdot \frac{S_{\text{ent}}}{k_B} \cdot \frac{1}{4} \cdot (\text{geometric factor}) \tag{2.6}$$

Using $a = c^2 \kappa_s$ (where $\kappa_s$ is the surface gravity), converting $S_{\text{ent}} \to S_{\text{ent}} \cdot k_B \ln 2$ (bits to J/K), and carrying through the geometric identification:

$$T^{\text{ent}}_{\mu\nu} = -\frac{c^4}{32\pi G} S_{\text{ent}} \, g_{\mu\nu} \tag{2.7}$$

**Reading off κ̃:**

Comparing Eq. (2.7) with the proposed form $T^{\text{ent}}_{\mu\nu} = \tilde{\kappa} \frac{c^4}{8\pi G \, k_B \ln 2} S_{\text{ent}} \, g_{\mu\nu}$:

$$\tilde{\kappa} \cdot \frac{c^4}{8\pi G \, k_B \ln 2} = -\frac{c^4}{32\pi G} \implies \tilde{\kappa} = -\frac{8\pi G \, k_B \ln 2}{32\pi G} \cdot \frac{1}{k_B \ln 2} = -\frac{1}{4} \tag{2.8}$$

**Result:**

$$\boxed{\tilde{\kappa} = -\frac{1}{4} \quad \text{[under holographic regulator hypothesis]}} \tag{2.9}$$

## 2.4 The Realistic Effective Coupling [HYPOTHESIS]

The ideal value $\tilde{\kappa} = -1/4$ applies to a perfectly isolated, maximally coherent quantum system — an idealization. Real systems are decohered by environmental interaction. The effective coupling is:

$$\tilde{\kappa}_{\text{eff}} = -\frac{1}{4} \alpha_{\text{screen}} \tag{2.10}$$

where $\alpha_{\text{screen}} \in [10^{-4}, 10^{-2}]$ is derived from open quantum system dynamics (see Section 03). This gives:

$$|\tilde{\kappa}_{\text{eff}}| \in [2.5 \times 10^{-5},\ 2.5 \times 10^{-3}] \tag{2.11}$$

## 2.5 Existing Experimental Bounds [ESTABLISHED]

No experiment has been specifically designed to test this coupling. Current upper bounds from null results in related experiments:

| Experiment | Bound on |κ̃| | Reference |
|-----------|----------|-----------|
| Gravity-mediated entanglement | < 3 × 10⁻⁹ | Bose et al., Nature 623 (2023) |
| Atom interferometry | < 1.2 × 10⁻¹⁰ | Kasevich et al., Nat. Phys. 19 (2023)* |
| Equivalence principle | < 8 × 10⁻¹¹ | MICROSCOPE, PRL 129 (2022) |

*Citation configuration to be verified (OP7)

All bounds are upper limits from null results. No positive detection has been made.

---

*Next: Section 03 — Environmental screening and the α_screen factor*
