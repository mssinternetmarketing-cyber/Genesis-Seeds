# Section 04 — The PEIG Framework: Formal Definitions

**Repository:** Monette Research — Entropic Gravity & PEIG Framework  
**Section:** 00_FOUNDATIONAL_DEFINITIONS  
**Status:** Canonical Definition  
**Last Updated:** March 2026

---

## Purpose

This section provides the formal mathematical definitions of the
**P/E/I/G (Potential, Energy, Identity, Gravity/Curvature)** framework. PEIG
is a four-phase dynamical model that describes how structure, identity, and
influence emerge from an underlying field of pure possibility.

**Important scope boundary:** PEIG operates at two distinct levels in this
research program, which must be kept carefully separated:

1. **Physical PEIG** — applied to quantum systems and spacetime geometry,
   where each phase has a precise physical meaning (see Section 4.6). This
   connects directly to the entropic gravity framework.

2. **Cognitive/Systems PEIG** — applied to intelligent agents, institutions,
   and civilizations as a model of adaptive behavior and identity (see
   Sections 4.2–4.5). This is a systems science framework with analogy to,
   but not derivation from, the physical framework.

The analogy between these two levels is philosophically significant and
scientifically interesting. It is **not** a mathematical derivation. The
cognitive framework does not follow from the physical framework by any chain of
equations. They share structure — not substance. Both levels are developed here;
their relationship is explicitly labeled as analogical throughout.

---

## 4.1 The PEIG State Vector

For any **node** — a localized, structured system capable of directed change
(a qubit, a quantum field configuration, a person, an institution, a
civilization) — define the PEIG state vector:

$$\mathbf{q} = (P, E, I, G) \in [0,1]^4$$

All four components are normalized to the interval $[0,1]$ for mathematical
consistency and cross-domain comparison. The normalization is domain-specific:
each component is expressed as a fraction of its theoretical maximum in the
relevant domain.

The **overall quality score** of a node is:

$$Q(\mathbf{q}) = \mathbf{w} \cdot \mathbf{q} = w_P P + w_E E + w_I I + w_G G$$

with default equal weights $\mathbf{w} = (0.25, 0.25, 0.25, 0.25)$, giving
$Q \in [0,1]$. Domain-specific weight vectors can be defined when one phase
is more critical than others.

---

## 4.2 Phase P — Potential

**Definition:** The breadth and depth of accessible futures. Potential measures
the freedom available to a node — how many distinct future states it can reach
from its current configuration.

**Mathematical formulation:**

$$P = \frac{H(\mathcal{S})}{H_{\text{max}}}$$

where:
- $H(\mathcal{S}) = -\sum_i p_i \log_2 p_i$ is the **Shannon entropy** of the
  distribution over accessible states $\mathcal{S}$ (in bits)
- $H_{\text{max}}$ is the theoretical maximum Shannon entropy for the domain
  (e.g., $\log_2 |\mathcal{S}|$ if all states were equally accessible)
- The ratio ensures $P \in [0,1]$

**Sub-metrics (for measurement):**
- $P_1$: State-space entropy — $-\sum_i p_i \log_2 p_i$ in bits
- $P_2$: Action branching factor — $\log_{10}(|\text{available actions}|)$,
  normalized
- $P_3$: Planning horizon — $\log_{10}(T_{\text{plan}}/T_{\text{ref}})$,
  normalized to domain maximum

**Boundary interpretations:**
- $P \to 1$: Maximum freedom — the node has access to a rich, diverse option
  space with many distinct achievable futures
- $P \to 0$: Maximum constraint — the node is trapped, its future nearly
  determined by current conditions, with few accessible states

**Physical analog:** In the entropic gravity framework, $P$ corresponds to the
configuration space $(\mathcal{C}, g_{ij})$ of a physical system with maximal
entropy — before any symmetry breaking or constraint accumulation.

**Examples across domains:**
- *Quantum system*: $P$ = von Neumann entropy of the state (normalized) —
  a pure state has $P = 0$; a maximally mixed state has $P = 1$
- *Individual human*: $P$ = range of life paths genuinely accessible given
  skills, resources, and circumstances
- *Institution*: $P$ = diversity of strategies the institution could feasibly
  pursue
- *AI system*: $P$ = $\log_{10}(|\text{action space}|)$, normalized against
  domain maximum

---

## 4.3 Phase E — Energy

**Definition:** The capacity for directed, efficient change. Energy measures
not raw power but the ability to move purposefully through the option space —
throughput, efficiency, and robustness under stress.

**Mathematical formulation:**

$$E = w_1 E_{\text{throughput}} + w_2 E_{\text{efficiency}} + w_3 E_{\text{robustness}}$$

where weights $w_i \geq 0$ sum to 1. Default: $w_1 = w_2 = w_3 = 1/3$.

**Sub-metrics:**
- $E_1$ (Throughput): $\log_{10}(\text{Output}/\text{Time})$, normalized to
  domain maximum — how much the node accomplishes per unit time
- $E_2$ (Efficiency): $\eta = \text{Value}_{\text{out}}/\text{Energy}_{\text{in}}$
  — output per unit resource consumed
- $E_3$ (Robustness): $R = \text{Value}_{\text{stress}}/\text{Value}_{\text{normal}}$
  — fraction of normal performance maintained under adversity

**Boundary interpretations:**
- $E \to 1$: Maximum capability — high output, minimal waste, fully stable
  under pressure
- $E \to 0$: Impotent — low output, inefficient, fragile under any stress

**Physical analog:** In the entropic gravity framework, $E$ corresponds to
gradient flow on the potential landscape:

$$\dot{q}^i = -g^{ij}\partial_j V(q)$$

where $V(q)$ is the potential energy function and $g^{ij}$ is the inverse metric
on configuration space. The system flows in the direction of steepest descent —
this is directed change under constraints.

**Dynamical connection to $P$:** Energy is generated when Potential encounters
constraints $\mathcal{C}$:

$$E = -\nabla(P \cdot \mathcal{C})$$

Potential alone is static. Constraints create gradients in the potential
landscape, and along those gradients energy flows. A system with high $P$ but
no constraints has no preferred direction — no $E$.

---

## 4.4 Phase I — Identity

**Definition:** A stable attractor — a configuration or set of configurations
that the system preferentially occupies and returns to when perturbed.
Identity is crystallized potential: pattern that persists.

**Mathematical formulation:**

$$I = w_1 I_{\text{coherence}} + w_2 I_{\text{consistency}} + w_3 I_{\text{plasticity}}$$

**Sub-metrics:**
- $I_1$ (Temporal coherence): $\mathcal{I}(B_{\text{past}}; B_{\text{future}})$
  — mutual information between past and future behavior, measuring how
  consistently the node's behavior predicts itself over time
- $I_2$ (Internal consistency): $1 - (C_{\text{violated}}/C_{\text{total}})$
  — fraction of internal commitments or constraints that are not violated
- $I_3$ (Adaptive plasticity): $I_{1,\text{after}}/(g \cdot I_{\text{struct}})$
  where $g \geq 1$ is a growth factor — ability to update and learn without
  losing identity coherence

**Dynamical equation:** Identity evolves according to a first-order linear
attractor equation driven by current Energy $E$:

$$\frac{dI}{dt} = \alpha E - \beta I$$

where:
- $\alpha > 0$ is the **crystallization rate** — how quickly sustained energy
  flow carves a stable pattern
- $\beta > 0$ is the **decay rate** — how quickly identity dissolves without
  reinforcing energy flow

**Solution:** For constant $E$, this ODE has the solution:

$$I(t) = \frac{\alpha}{\beta} E + \left(I_0 - \frac{\alpha}{\beta} E\right)
e^{-\beta t}$$

This converges exponentially to the attractor:

$$I_\infty = \frac{\alpha}{\beta} E$$

with time constant $\tau = 1/\beta$. The attractor value is proportional to
$E$ — more sustained energy flow produces stronger identity. The exponential
decay means identity dissolves with characteristic time $1/\beta$ in the
absence of driving.

**Formal attractor definition:** A set $A \subset \text{Configuration Space}$
is an identity attractor if:
1. Trajectories starting near $A$ remain near $A$ (local stability)
2. Trajectories starting far from $A$ eventually approach $A$ (attracting basin)
3. Small perturbations applied while on $A$ return the system to $A$
   (structural stability)

**Boundary interpretations:**
- $I \to 1$: Maximum coherent identity — perfectly stable patterns with maximum
  adaptive capacity; the system can change without losing itself
- $I \to 0$: No stable identity — either completely rigid (no plasticity) or
  completely incoherent (contradictory, fragmented)

**Physical analog:** In the entropic gravity framework, $I$ corresponds to the
attractor basin of the density matrix dynamics:
$\rho(t) \to \rho_{\text{ss}}$ as $t \to \infty$,
where $\rho_{\text{ss}}$ is the steady state.

**Negentropy and Identity:** The negentropy $\mathcal{N}(\rho) = S_{\text{max}}
- S[\rho(t)]$ measures the same concept as $I$ in the physical domain —
deviation from maximum disorder. High identity corresponds to high negentropy.
However, as established in Section 02, negentropy cannot be substituted for
entanglement entropy density in the gravitational source term.

---

## 4.5 Phase G — Curvature

**Definition:** The degree to which a node reshapes the field of possibilities
for other nodes. Curvature measures influence — the extent to which the
existence and actions of one node change what is accessible to surrounding nodes.

**Mathematical formulation:**

$$G = G^+ - G^-$$

where:
- $G^+$ measures **positive curvature** — the degree to which the node
  *expands* the option space for others ($\Delta P_{\text{others}} > 0$,
  in bits gained by others)
- $G^-$ measures **negative curvature** — the degree to which the node
  *contracts* the option space for others ($\Delta P_{\text{others}} < 0$,
  bits lost by others)

**Sub-metrics:**
- $G_1$: Influence reach — network centrality (PageRank, eigenvector
  centrality) measuring how many nodes are affected
- $G_2$: Causal impact magnitude — $\Delta_{\text{Outcome}}$ when the
  node acts vs. counterfactual
- $G_3^+$: P-expansion — average increase in $P$ for neighboring nodes when
  this node is present and active
- $G_3^-$: P-contraction — average decrease in $P$ for neighboring nodes

**Boundary interpretations:**
- $G \to +1$: Maximum positive influence — the node enables and expands
  the capabilities of all surrounding nodes; a force for flourishing
- $G \to 0$: Neutral presence — the node exists without significantly
  affecting the possibility space of others
- $G \to -1$: Maximum negative influence — the node suppresses, constrains,
  and collapses the option space of surrounding nodes

**Physical analog:** In the entropic gravity framework, $G$ corresponds
directly to the Einstein tensor:

$$G_{\mu\nu} = R_{\mu\nu} - \frac{1}{2}R \, g_{\mu\nu}$$

which measures the curvature of spacetime generated by the accumulated
stress-energy (identity) of matter. This is the most direct physical realization
of the PEIG $G$ phase — accumulated identity literally curves the geometry for
everything else.

---

## 4.6 The PEIG Dynamical Cycle

The four phases are not independent — they form a closed, recursive cycle:

$$P \xrightarrow{\text{symmetry breaking}} E
\xrightarrow{\text{dissipation}} I
\xrightarrow{\text{accumulation}} G
\xrightarrow{\text{field deformation}} P'$$

**Step 1: Potential collapses into Energy**
When a system in a high-$P$ state encounters constraints $\mathcal{C}$
(physical laws, resource limits, values, pressures), those constraints
create gradients in the potential landscape. The system flows along these
gradients as directed Energy $E$:
$$E = -\nabla(P \cdot \mathcal{C})$$

**Step 2: Energy organizes into Identity**
Sustained Energy flow carves stable attractors. Where the same trajectory
is followed repeatedly, a pattern crystallizes — a habit, a structure, an
identity:
$$\frac{dI}{dt} = \alpha E - \beta I, \quad I_\infty = \frac{\alpha}{\beta}E$$

**Step 3: Identity accumulates into Curvature**
As Identity becomes stable and persistent, it begins to affect the
landscape for surrounding systems. A stable pattern is a gravitational-like
source — it bends the field of possibilities around it:
$$G \propto \int_0^t I(\tau) \, d\tau \quad (\text{schematic})$$

**Step 4: Curvature reshapes Potential**
The accumulated curvature $G$ deforms the original potential landscape,
creating a new $P'$ with different structure — some paths made easier, others
harder:
$$P' = P_0 + \delta P(G)$$

The cycle then repeats on the reshaped landscape. This is the mechanism of
self-organization, evolution, learning, and growth across all scales.

**Open problem:** The full coupled dynamical system — the complete set of ODEs
for $(P(t), E(t), I(t), G(t))$ — is not yet written in closed form. The
Identity equation $dI/dt = \alpha E - \beta I$ is the only component fully
specified. Deriving the coupled equations from first principles for physical
systems is an [OPEN PROBLEM] in this research program.

---

## 4.7 The Omega Node ($\Omega$)

**Definition:** The theoretical upper bound of a node's quality — the state in
which all four PEIG dimensions are simultaneously maximized subject to
physical constraints:

$$\Omega = \arg\max_{\mathbf{q} \in \mathcal{F}} Q(\mathbf{q})$$

where $\mathcal{F}$ is the **feasibility set** — the set of PEIG vectors
achievable within the physical, computational, and resource constraints of
the domain.

The Omega node is not a state of infinite capacity. It is the **maximum
realizable intelligence** within the actual constraints of a system's
environment. It represents:

- Maximum accessible option space ($P \to P_{\text{max}}$)
- Maximum directed capability ($E \to E_{\text{max}}$)
- Maximum coherent identity ($I \to I_{\text{max}}$)
- Maximum positive influence on surrounding systems ($G \to G^+_{\text{max}}$)

**Relationship to the Omega Axioms:** Seven axioms govern behavior at and
near the Omega node. These are defined in `03_PEIG_FRAMEWORK/omega_node_architecture.md`.

---

## 4.8 Cross-Domain Analogue Quality

The PEIG framework has been systematically mapped against 8+ domains with
the following analogue quality scores (see `03_PEIG_FRAMEWORK/domain_analogues.md`
for full analysis):

| Domain | Analogue Quality | Strongest Correspondence |
|---|---|---|
| Biological morphogenesis | 95% | Morphogenetic field ↔ P; cell fate ↔ I |
| Political polarization | 91% | Attractor basins ↔ partisan identities |
| Thermodynamics | 89% | Phase transitions ↔ $P \to E$ symmetry breaking |
| Neuroscience | 85% | Neural attractors ↔ I; synaptic plasticity ↔ $\alpha/\beta$ |
| Economics | 79% | Market equilibria ↔ I attractors |
| AI/Deep learning | 79% | Latent space ↔ P; gradient descent ↔ E |

These analogues are **descriptive mappings**, not mathematical derivations.
They demonstrate the structural generality of the PEIG cycle and suggest
domains where PEIG-based predictions could be tested.

---

## Cross-References

- **Section 01** — Universe and History: $P$ as the formal analog of
  Allowed States $\mathcal{S}$; $I$ as the analog of Actual History $r$
- **Section 02** — Entropy and Information: $P$ formulated as normalized
  Shannon entropy; negentropy as the physical measure of $I$
- **Section 03** — Constraint Manifold: $\mathcal{S}$ (constraint manifold)
  as the physical realization of PEIG $P$; $\mathcal{O}(r)$ as the analog
  of accumulated $I$
- **03_PEIG_FRAMEWORK/** — full mathematical specification, domain analogues,
  and Omega node architecture
- **01_PHYSICS_CORE/A_ENTROPIC_GRAVITY** — the physical PEIG $G$ phase
  realized as the Einstein tensor sourced by entanglement entropy
