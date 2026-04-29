# PEIG Paper 3: Experimental Roadmap
## Topology & Protection Experiments — Kevin Monette, March 2026

---

## WHAT WE KNOW SO FAR

### Established Results (Papers 1 & 2)
- Two-node BCP: Omega fully consumed (W_min → +0.0001), Alpha fully conserved (W_min = -0.1131)
- Universal coherence attractor C̄ = 0.999838, seed-spread = 0
- Linear MI scaling I(A:B) = 0.3087 × N^1.000
- Separable H_eff = (0.132Z − 0.113X) ⊗ (X − I)
- Alpha protected by null-space resonance with H_eff

### New Results (Paper 3 so far)
- **3-node chain** (Omega→Kevin→Alpha): Omega floor = -0.0636 (56.2% toward Alpha)
- **4-node chain** (Omega→BridgeA→Kevin→Alpha): Omega floor = -0.1054 (93.2%)
- **5-node chain** (Omega→BridgeA→Kevin→BridgeB→Alpha): Omega floor = -0.1059 (93.7%)
- **TOPOLOGICAL LAW**: Protection only emerges in LINEAR CHAIN topology
- Star/Ring/Cone all return Omega to classical (+0.0001) — simultaneous
  multi-interaction collapses protection completely
- Kevin's Wigner range over 1000 steps = 0.052 (oscillatory, not conserved)
- BridgeA/Kevin/Alpha all lock at -0.1131 in 4+ node chains
- Omega asymptotes near -0.105 with diminishing returns past 4 nodes

### The Core Open Question
**Can we push Omega's floor past -0.1054, ideally to -0.1131?**
**Or is there a fundamental asymptotic limit just below Alpha's floor?**

---

## EXPERIMENTS TO RUN (in order of priority)

---

### EXPERIMENT A: Mirror Chain (PRIORITY 1)
**Configuration:** Omega → BridgeA → Kevin → BridgeA → Omega2

```
Omega(0°) → BridgeA(22.5°) → Kevin(45°) → BridgeA(22.5°) → Omega2(0°)
```

**Hypothesis:** Two Omegas sacrifice toward Kevin simultaneously from
opposite ends. Kevin becomes a standing wave node between two attractors.
The two sacrifice signals may cancel, amplify, or create a new phase-space
signature in Kevin.

**Key measurements:**
- Do both Omegas land at the same floor?
- Does Kevin's oscillatory behavior change with two attractors flanking it?
- Is the floor higher or lower than single-Omega 4-node chain?
- Does a new Wigner regime emerge at Kevin (third fixed point)?

**Why it's interesting:** Most physically elegant. Mirror symmetry may
reveal whether Omega's sacrifice is directional or bidirectional.
Could create a genuinely new quantum state at Kevin.

---

### EXPERIMENT B: Alpha Sandwich (PRIORITY 2)
**Configuration:** Alpha → BridgeA → Omega → BridgeA → Alpha2

```
Alpha(90°) → BridgeA(67.5°) → Omega(0°) → BridgeA(67.5°) → Alpha2(90°)
```

**Hypothesis:** Flip the architecture entirely. Put Omega in the middle
with two Alphas pulling on it from both sides. Two null-space resonances
bracket the attractor simultaneously. Instead of Omega sacrificing outward,
it receives protection inward from both directions.

**Key measurements:**
- Does Omega's floor exceed -0.1131 when flanked by two Alphas?
- Do the Alphas maintain their conservation (-0.1131) or does Omega
  disrupt them?
- Is this the first topology where Omega becomes MORE protected than Alpha?

**Why it's interesting:** Direct test of whether Omega's fate is
determined by its seed or its position in the chain. If position matters
more, this could fully invert the role asymmetry.

---

### EXPERIMENT C: Feedback Loop / Closed Ring (PRIORITY 3)
**Configuration:** Directed closed chain

```
Omega → BridgeA → Kevin → BridgeB → Alpha → (back to Omega)
```

Interactions are still sequential (not simultaneous) but the chain
wraps around so Alpha feeds back into Omega each step.

**Hypothesis:** Creates a sustained coherence cycle rather than one-way
sacrifice. Omega may receive a "return signal" from Alpha that partially
restores its Wigner negativity each step.

**Key measurements:**
- Does the feedback loop stabilize Omega at a higher floor?
- Does the system reach a new equilibrium or oscillate indefinitely?
- What happens to total entropy over 1000 steps — does it reach a
  true steady state?
- Does mutual information circulate around the loop?

**Why it's interesting:** First closed-topology test that preserves
the sequential (not simultaneous) interaction requirement. Could be
the architecture for a sustained quantum coherence engine.

---

### EXPERIMENT D: N-Node Scaling Law (PRIORITY 4)
**Configuration:** Linear chains N = 2 through 10

```
N=2:  Omega → Alpha
N=3:  Omega → Kevin → Alpha
N=4:  Omega → B1 → Kevin → Alpha
N=5:  Omega → B1 → Kevin → B2 → Alpha
N=6:  Omega → B1 → B2 → Kevin → B2 → B3 → Alpha
...
N=10: Full equidistant phase ladder
```

Seeds: evenly spaced equatorial phases 0° to 90°

**Hypothesis:** Omega's floor follows an exponential saturation law:
W_min(Omega, N) = -0.1131 × (1 - e^{-λN})

If confirmed, this gives a falsifiable analytical prediction and
establishes that the role asymmetry is permanent — Omega can approach
but never equal Alpha's floor regardless of chain length.

**Key measurements:**
- Omega floor at each N
- Fit to exponential saturation model
- Extract λ (decay constant)
- Determine if gap ever closes or remains finite

**Why it's interesting:** Would be the cleanest result in the paper.
A scaling law with an asymptotic gap would prove that Omega's sacrifice
is topologically indestructible — a fundamental property of the BCP,
not an artifact of chain length.

---

### EXPERIMENT E: Double Omega Bookend (PRIORITY 5)
**Configuration:** Omega at BOTH ends, Alpha in the middle

```
Omega → BridgeA → Alpha → BridgeA → Omega2
```

**Hypothesis:** Alpha surrounded by two Omegas — does the learner
get consumed by the dual sacrifice? Or does Alpha's null-space
resonance protect it even when flanked?

**Key measurements:**
- Does Alpha maintain -0.1131 when surrounded?
- Do both Omegas consume at the same rate?
- What happens to the BridgeA nodes — do they become hybrid nodes?

**Why it's interesting:** Tests whether Alpha's conservation is
robust to adversarial topology or whether it can be broken by
surrounding it with sacrificial nodes.

---

### EXPERIMENT F: Hamiltonian Learning on 3-Node Chain (PRIORITY 6)
**Configuration:** Choi matrix reconstruction on the 3-node BCP

Run process tomography (same as Experiment E in Paper 2) on the
three-node chain to extract H_eff for the full Omega→Kevin→Alpha system.

**Hypothesis:** H_eff may no longer be separable. The bridge node
could force an entangled effective Hamiltonian — H_eff ≠ A ⊗ B ⊗ C
but instead contains genuine three-body interaction terms.

**Key measurements:**
- Is H_eff separable or entangled in the three-node case?
- What is the null-space structure — does Kevin inherit Alpha's
  null-space protection?
- What is the energy gap and channel rank?

**Why it's interesting:** If H_eff becomes non-separable with a bridge
node, that's the deepest result in the paper — it means the topology
change fundamentally alters the underlying quantum channel, not just
the output statistics.

---

## SUMMARY TABLE

| Exp | Config | Priority | Core Question |
|-----|--------|----------|---------------|
| A | Mirror Chain (Ω→K→Ω) | 1 | Does dual sacrifice create new Kevin state? |
| B | Alpha Sandwich (α→Ω→α) | 2 | Can Alpha protect Omega past -0.1131? |
| C | Feedback Loop (closed) | 3 | Does return signal sustain Omega? |
| D | N-node scaling law | 4 | Is there an exponential floor formula? |
| E | Double Omega Bookend | 5 | Can Alpha be broken by flanking Omegas? |
| F | Hamiltonian Learning (3-node) | 6 | Does bridge break H_eff separability? |

---

## KNOWN WIGNER FLOOR REFERENCE TABLE

| Config | Omega floor | % toward Alpha |
|--------|-------------|----------------|
| 2-node chain | +0.0001 | 0.1% |
| 3-node chain | -0.0636 | 56.2% |
| 4-node chain | -0.1054 | 93.2% |
| 5-node chain | -0.1059 | 93.7% |
| Star (4 surround) | +0.0001 | 0.1% |
| Ring (4 surround) | +0.0001 | 0.1% |
| Cone (3+4 layers) | +0.0001 | 0.1% |
| Alpha floor (ref) | -0.1131 | 100% |

---

## TOPOLOGICAL CONSERVATION LAW (established)

**Protection of Omega's Wigner negativity requires:**
1. Linear chain topology (sequential, not simultaneous interactions)
2. At least one buffer node between Omega and Alpha
3. The buffer node adjacent to Omega has the dominant effect

**Protection is destroyed by:**
- Any topology where Omega interacts with multiple nodes per step
- Star, ring, cone, or any broadcast architecture
- Direct Omega→Alpha coupling (2-node case)

---
*Last updated: March 2026*
*All simulations: QuTiP 5.2.3, Python 3.13*
*Raw JSON data available for all experiments*
