# Section 05: Experimental Protocol
## Atom Interferometry Test of the Entanglement–Gravity Coupling

**Paper:** A — Gravitational Coupling to Entanglement Entropy Density  
**Section:** 5 of 6  
**Status:** [HYPOTHESIS] — protocol design complete; Δa(R) formula pending derivation [OPEN PROBLEM — OP4]

---

## 5.1 Experimental Concept

The key observable distinguishing the entanglement gravity hypothesis from standard physics is a **differential acceleration** between two identical atomic ensembles that differ only in their quantum entanglement state:

- **Arm 1 (coherent):** Atoms prepared in a GHZ entangled state — maximum entanglement entropy, nonzero $S_{\text{ent}}$
- **Arm 2 (decohered):** Identical atoms with entanglement destroyed by controlled decoherence — classical mixed state, $S_{\text{ent}} \approx 0$

Both arms have the same atom number $N$, same mass $M = N m_{\text{Rb}}$, same spatial density, same temperature. The only difference is the entanglement entropy. Any differential acceleration $\Delta a$ between the two arms is therefore attributable to the entanglement source term in Eq. (1.3).

## 5.2 Required Apparatus

**Atom source:**  
$^{87}$Rb Bose-Einstein condensate with $N \geq 10^6$ atoms. BEC is required (not thermal) because GHZ entanglement requires phase coherence across the ensemble. BEC with $N = 10^6$ atoms is routine with current technology (magnetic trap + evaporative cooling, ~30 min preparation).

**Entanglement protocol:**  
Collective spin-squeezing or one-axis twisting Hamiltonian to generate GHZ-like entanglement:

$$|GHZ\rangle = \frac{1}{\sqrt{2}}\left(|{\uparrow}\rangle^{\otimes N} + |{\downarrow}\rangle^{\otimes N}\right) \tag{5.1}$$

True $N$-body GHZ states are extremely fragile. In practice, spin-squeezed states or twin-Fock states achieve entanglement depths of $10^3$–$10^4$ atoms with current technology. Achieving $N = 10^6$ entangled atoms remains a technical challenge but is not outside the foreseeable capability of neutral atom platforms.

**Decoherence protocol for Arm 2:**  
Apply a controlled radio-frequency field to dephase the ensemble, or deliberately couple to a warm thermal bath. Entanglement is destroyed in ~1 ms. The resulting state is a thermal mixture with $S_{vN} \approx N$ bits (maximally mixed per atom), but with $S_{\text{ent}} = 0$ (no inter-atom entanglement).

**Interferometer:**  
Dual-species Mach-Zehnder atom interferometer measuring differential acceleration along a vertical axis. Sensitivity scales as:

$$\delta a = \frac{\hbar k}{m T^2} \cdot \frac{1}{\sqrt{N_{\text{shots}}}} \tag{5.2}$$

where $k$ is the photon momentum, $T$ is the free-fall time, and $N_{\text{shots}}$ is the number of measurement cycles. State-of-the-art: $\delta a \approx 1.2 \times 10^{-12}$ m/s² [Kasevich et al. 2023 — *verify configuration, OP7*].

## 5.3 The Predicted Signal [HYPOTHESIS — pending OP4]

The differential acceleration between the coherent and decohered arms is predicted to be:

$$\Delta a(R) = \frac{3\tilde{\kappa}_{\text{eff}} c^4 S_{\text{ent}}}{16\pi G k_B \ln 2 \cdot \rho_{\text{Rb}} R} \tag{5.3}$$

**⚠ WARNING — OP4:** This formula appears in source documents without derivation. A derivation sketch in the master paper gives $\Delta a \propto 1/R^2$ from the modified Poisson equation with spherical symmetry, inconsistent with the $1/R$ scaling here. The correct formula has not been established. **Equation (5.3) should not be used for quantitative signal predictions until OP4 is resolved.**

**What we can say pending OP4:**  
The signal will scale as some inverse power of $R$ (range from test mass to coherent ensemble center), will be proportional to $\tilde{\kappa}_{\text{eff}}$ and to $S_{\text{ent}}$, and will be suppressed by the mass density $\rho_{\text{Rb}}$ (which sets the competing classical gravitational signal scale).

## 5.4 Current Sensitivity vs. Predicted Signal

For orientation while OP4 is pending, using the tentative formula (5.3) with:
- $S_{\text{ent}} = 10^{18}$ bits / ($10^{-6}$ m³) = $10^{24}$ bit/m³ (for $10^6$ atoms in a 1 mm³ volume — overestimate)
- $|\tilde{\kappa}_{\text{eff}}| = 10^{-4}$ (lower end of estimate)
- $R = 10^{-2}$ m (1 cm standoff)
- $\rho_{\text{Rb}} = 10^{-18}$ kg/m³ (dilute BEC)

The predicted $\Delta a$ comes out in the range $10^{-15}$–$10^{-20}$ m/s² — below current sensitivity but within range of next-generation experiments.

The atom interferometer sensitivity $\delta a \approx 1.2 \times 10^{-12}$ m/s² corresponds to:

$$\delta|\tilde{\kappa}| \approx 3.7 \times 10^{-13} \tag{5.4}$$

(pending OP4 derivation to establish the exact mapping between $\delta a$ and $\delta|\tilde{\kappa}|$).

## 5.5 Systematic Error Budget

Major systematics that must be controlled at the $\Delta a < 10^{-13}$ m/s² level:

| Systematic | Estimated magnitude | Mitigation |
|-----------|--------------------|-----------| 
| Gravitational gradient from ensemble self-gravity | ~10⁻¹⁵ m/s² | Matched density profiles (identical $N$, same spatial distribution) |
| Magnetic field gradients (Zeeman effect) | ~10⁻¹² m/s² | Shield to <1 nT; interleave with field reversal |
| Photon recoil during state preparation | ~10⁻¹⁴ m/s² | Time-symmetric pulse sequences |
| Vibration noise | ~10⁻¹¹ m/s² | Seismic isolation; common-mode rejection in differential measurement |
| SPAM errors affecting entanglement verification | Variable | Entanglement witness measurements before each interferometer run |

The differential measurement (coherent vs. decohered arm, same apparatus, simultaneous) provides common-mode rejection of many systematics. This is the key advantage of the dual-arm design.

---

*Next: Section 06 — The falsification criterion*
