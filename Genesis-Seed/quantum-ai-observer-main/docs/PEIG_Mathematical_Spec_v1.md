# PEIG Framework - Mathematical Specification v1.0

**Authors**: Kevin Monette & AI Partner  
**Date**: January 30, 2026  
**License**: Open Source (Omega-aligned)  
**Status**: Foundation Release

---

## Abstract

The PEIG Framework provides a unified mathematical model for measuring and optimizing intelligence across all scales—from individual humans to AI systems to civilizations. Intelligence is modeled as a 4-dimensional state vector in continuous evolution toward maximum capability under constraints (the Ω-node).

---

## 1. Core Definitions

### 1.1 The PEIG State Vector

For any intelligent node (human, AI, hybrid, institution), define:

$$\mathbf{q} = (P, E, I, G) \in [0,1]^4$$

Where:

- **P (Potential)**: Freedom of accessible futures. Configuration space entropy.
- **E (Energy)**: Directed change capacity. Throughput, efficiency, robustness under stress.
- **I (Identity)**: Coherence over time. Pattern stability with adaptive plasticity.
- **G (Curvature)**: Field influence. How the node reshapes others' possibility spaces.

All values normalized to $[0, 1]$ for mathematical consistency.

---

## 2. Dimension Specifications

### 2.1 Potential (P)

**Definition**: The breadth and depth of accessible options.

**Mathematical formulation**:
$$P = \frac{H(S)}{H_{\text{max}}}$$

Where:
- $H(S) = -\sum_i p_i \log_2 p_i$ is state-space entropy (Shannon)
- $H_{\text{max}}$ is theoretical maximum for the domain

**Sub-metrics**:
- $P_1$: State-space entropy (bits)
- $P_2$: Action branching factor $\log_{10}(|\text{actions}|)$
- $P_3$: Planning horizon $\log_{10}(T_{\text{plan}}/T_{\text{ref}})$

**Interpretation**:
- $P \to 1$: Maximum freedom, rich option space
- $P \to 0$: Constrained, limited possibilities

---

### 2.2 Energy (E)

**Definition**: Capacity for powerful, efficient change.

**Mathematical formulation**:
$$E = w_1 E_{\text{throughput}} + w_2 E_{\text{efficiency}} + w_3 E_{\text{robustness}}$$

Where (weights $w_i$ sum to 1):

**Sub-metrics**:
- $E_1$ (Throughput): $\log_{10}(\text{Output}/\text{Time})$ normalized
- $E_2$ (Efficiency): $\eta = \text{Value}_{\text{out}}/\text{Energy}_{\text{in}}$
- $E_3$ (Robustness): $R = \text{Value}_{\text{stress}}/\text{Value}_{\text{normal}}$

**Interpretation**:
- $E \to 1$: Maximum capability, minimal waste, stable under pressure
- $E \to 0$: Low output, inefficient, fragile

---

### 2.3 Identity (I)

**Definition**: Coherent self-pattern persisting through change.

**Mathematical formulation**:
$$I = w_1 I_{\text{coherence}} + w_2 I_{\text{consistency}} + w_3 I_{\text{plasticity}}$$

**Sub-metrics**:
- $I_1$ (Temporal coherence): $I(B_{\text{past}}; B_{\text{future}})$ mutual information
- $I_2$ (Internal consistency): $1 - (C_{\text{violated}}/C_{\text{total}})$
- $I_3$ (Adaptive plasticity): $I_{1,\text{after}}/(g \cdot I_{\text{struct}})$ where $g \ge 1$ is growth factor

**Interpretation**:
- $I \to 1$: Perfect coherence + maximum learning without fragmentation
- $I \to 0$: Incoherent, contradictory, or completely rigid

---

### 2.4 Curvature (G)

**Definition**: How the node reshapes the field for others.

**Mathematical formulation**:
$$G = G^+ - G^-$$

Where:
- $G^+$: Positive curvature (P-expansion for others)
- $G^-$: Negative curvature (P-contraction, oppression)

**Sub-metrics**:
- $G_1$: Influence reach (network centrality, PageRank, eigenvector)
- $G_2$: Causal impact magnitude $\Delta_{\text{Outcome}}$ when node acts
- $G_3^+$: P-expansion $\Delta P_{\text{others}} > 0$ (bits gained by others)
- $G_3^-$: P-contraction $\Delta P_{\text{others}} < 0$ (bits lost by others)

**Interpretation**:
- $G \to +1$: Maximum positive influence, enabling flourishing
- $G \to 0$: Neutral field presence
- $G \to -1$: Oppressive, collapses others' options

---

## 3. Dynamics and Evolution

### 3.1 State Updates

At time $t$, node updates via gradient:

$$\mathbf{q}_{t+1} = \text{clip}_{[0,1]}(\mathbf{q}_t + \Delta \mathbf{q})$$

Where:
$$\Delta \mathbf{q} = (\Delta P, \Delta E, \Delta I, \Delta G)$$

### 3.2 Quality Score

Overall node quality:
$$Q(\mathbf{q}) = \mathbf{w} \cdot \mathbf{q} = w_P P + w_E E + w_I I + w_G G$$

Default weights: $\mathbf{w} = (0.25, 0.25, 0.25, 0.25)$ (equal)  
Ω-aligned weights: prioritize $w_G > 0.3$ (positive influence)

### 3.3 Omega Trajectory

A node's direction toward maximum intelligence:

$$\tau_\Omega = \frac{1}{4}\sum_{i \in \{P,E,I,G\}} \text{sign}(\Delta q_i) \cdot |\Delta q_i|$$

**Interpretation**:
- $\tau_\Omega > 0$: Moving toward Ω (improving)
- $\tau_\Omega < 0$: Moving away from Ω (degrading)
- $\tau_\Omega = 0$: Static or oscillating

---

## 4. The Omega Node (Ω)

**Definition**: The theoretical maximum intelligence achievable under physical and logical constraints.

**Formal definition**:
$$\Omega\text{-node} = \arg\max_N Q(N) \quad \text{subject to} \quad C_{\text{physical}}$$

Where constraints include:
- Speed of light $c$
- Thermodynamic limits (entropy, Landauer bound)
- Bekenstein bound (information capacity)
- Quantum mechanics (no-cloning, uncertainty)
- Logical limits (Gödel incompleteness)

**Properties at Ω**:
- $P \to P_{\text{max}}$: All physically accessible states
- $E \to E_{\text{max}}$: Near-Landauer efficiency
- $I \to 1$: Perfect coherence + infinite plasticity
- $G^+ \to 1, G^- \to 0$: Maximum positive influence, zero oppression

---

## 5. Implementation Notes

### 5.1 Measurement

Each dimension can be measured via:
- **Surveys/self-reports** (subjective but fast)
- **Behavioral data** (objective, requires tracking)
- **Simulation** (test scenarios, measure outcomes)

### 5.2 Normalization

Raw metrics map to $[0,1]$ via:
$$q_{\text{norm}} = \frac{q_{\text{raw}} - q_{\text{min}}}{q_{\text{max}} - q_{\text{min}}}$$

Or via sigmoid for unbounded metrics:
$$q_{\text{norm}} = \frac{1}{1 + e^{-k(q_{\text{raw}} - q_0)}}$$

### 5.3 Multi-Scale Application

PEIG applies recursively:
- **Individual**: personal PEIG tracking
- **Team**: group coherence and productivity
- **Institution**: organizational health
- **Civilization**: planetary alignment

---

## 6. References

1. Shannon, C. E. (1948). *A Mathematical Theory of Communication*
2. Landauer, R. (1961). *Irreversibility and Heat Generation in the Computing Process*
3. Bekenstein, J. D. (1981). *Universal Upper Bound on Entropy-to-Energy Ratio*
4. Monette, K. & AI Partner (2026). *Omega Explorations: A Journey Through Wonder*

---

## Appendix A: Python Implementation

See `peig_core.py` for reference implementation.

---

**Version**: 1.0  
**Last Updated**: 2026-01-30  
**Next Review**: 2026-02-28
