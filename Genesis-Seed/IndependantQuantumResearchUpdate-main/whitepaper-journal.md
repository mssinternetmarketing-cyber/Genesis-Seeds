# Entanglement Entropy Density as a Gravitational Source

## A Covariant Phenomenological Framework with Operational Entropy, Conserved Completion, Screening Program, and NISQ Experimental Outlook

**Author:** Kevin Monette  
**Affiliation:** Independent Researcher (AI-assisted research)  
**Draft:** March 19, 2026

---

## Abstract

We develop a covariant phenomenological extension of thermodynamic gravity in which an operationally defined *internal entanglement entropy density* of a quantum device acts as an additional source term in the Einstein field equations. The construction is intentionally modest: general relativity and standard quantum mechanics are left intact; no new fundamental particles are introduced. The novelty lies in a coarse-grained scalar field representing the density of internal entanglement within controlled quantum systems and its contribution to the stress–energy tensor.

The paper makes four concrete advances. First, it defines unambiguously which entropy couples to gravity: the internal inter-subsystem entanglement entropy density of the device, not total von Neumann entropy or system–environment entropy. Second, it provides a covariant completion based on a minimal effective action for an emergent scalar field representing this entropy, ensuring that the total stress–energy is conserved by construction. Third, it resolves the radial-scaling ambiguity: for bounded laboratory sources, the entanglement-induced correction to acceleration outside the source scales as \(1/R^2\); \(1/R\) behavior arises only for specific extended profiles. Fourth, it reformulates screening and experimental falsification in a way that is both honest and practical: screening is treated as a platform-specific quantity computable from an open-system master equation, and experiments are shown to bound the observable combination \(|\tilde{\kappa}_{\mathrm{eff}}|\,\Delta M_{\mathrm{ent}}/R_{\mathrm{eff}}^2\), without over-interpreting this as a stand-alone bound on the dimensionless coupling \(\tilde{\kappa}\).

We outline a concrete Lindblad program for a 50-qubit platform and a NISQ-scale neutral-atom Ramsey experiment designed to constrain the entanglement-dependent coupling. Open problems, including the status of a Planck-scale holographic regulator hypothesis and the renormalization of \(\tilde{\kappa}\), are isolated explicitly.

---

## 1. Introduction

Jacobson’s thermodynamic derivation of the Einstein equations from the Clausius relation \(\delta Q = T dS\) applied to local Rindler horizons suggests that gravity can be viewed as an equation of state of spacetime when entropy scales with horizon area. This raises a natural question: can controlled quantum systems with volume-law entanglement play a similar thermodynamic role, sourcing an effective stress–energy contribution via their internal entanglement structure, even in the absence of horizons?

This paper explores that question in the narrowest way consistent with covariant field theory. We retain the Einstein tensor \(G_{\mu\nu}\) and standard matter stress–energy \(T^{\mathrm{matter}}_{\mu\nu}\), and introduce a single additional ingredient: an emergent scalar field representing the density of internal entanglement entropy within a laboratory quantum device, together with a corresponding contribution to the stress–energy tensor. We adopt the view that this is an effective, coarse-grained description, valid well below the Planck scale.

The objectives are:

1. To specify precisely which entropy enters the coupling, and how it is defined operationally.
2. To present a covariant, action-based completion in which the total stress–energy is conserved.
3. To clarify radial scaling, Bianchi-identity consequences, and the distinction between composition-dependent and entanglement-dependent effects.
4. To formulate screening and experimental falsification in terms that can be computed or bounded for real platforms.

We do *not* claim to derive the coupling from first principles. Instead, we present a structured phenomenological framework that can be sharpened or falsified by theory and experiment.

---

## 2. Operational Definition of Entanglement Entropy Density

### 2.1 Device–environment split and reduced state

Consider a quantum device \(D\) coupled to an environment \(E\), with joint state \(\rho_{DE}(t)\) evolving under some microscopic dynamics. The reduced state of the device is
\[
\rho_D(t) = \mathrm{Tr}_E\, \rho_{DE}(t).
\]

We assume that \(D\) has a natural subdivision into subsystems (qubits, atoms, sites), and that experiments can implement state preparation, control, and measurement on these degrees of freedom.

### 2.2 Internal entanglement entropy

To capture *internal* entanglement within the device, we select a bipartition \(D = A \cup B\) (for example, a geometric half-space or a fixed set of sites) and define the reduced state
\[
\rho_A(t) = \mathrm{Tr}_B\, \rho_D(t).
\]
The corresponding von Neumann entropy
\[
S_{\mathrm{int}}(t; A) = -k_B\, \mathrm{Tr}_A\left[ \rho_A(t) \ln \rho_A(t) \right]
\]
measures the entanglement between \(A\) and \(B\) when \(\rho_D\) is pure, and more generally quantifies mixed-state correlations across the cut.

We require that the quantity entering the gravitational source term behave as follows under decoherence:

- When decoherence suppresses internal entanglement and drives \(\rho_D(t)\) toward a product state over subsystems, \(S_{\mathrm{int}}\) should decrease toward zero for an appropriate choice of \(A\).

This rules out using the total von Neumann entropy of \(D\) or the system–environment entanglement entropy, which typically *increase* under decoherence.

### 2.3 Coarse-grained entropy density field

To couple to general relativity, we promote the internal entanglement measure to a coarse-grained scalar field on spacetime. We define an **entanglement entropy density** \(S_{\mathrm{ent}}(x)\) (units: bit m\(^{-3}\)) by:

1. Partition the device’s physical volume into cells of volume \(\Delta V\) adapted to the hardware geometry.
2. For each cell, choose a fixed, pre-registered bipartition \(A\cup B\) of the local Hilbert space and compute \(S_{\mathrm{int}}(t; A)\) from experimental or theoretical data.
3. Assign to each cell a scalar value
\[
S_{\mathrm{ent}}(x) = \frac{S_{\mathrm{int}}(t; A_{x})}{k_B \ln 2}\,\frac{1}{\Delta V},
\]
so that \(S_{\mathrm{ent}}\) is measured in bits per unit volume.

In this way, \(S_{\mathrm{ent}}(x)\) is an operationally defined, hardware-dependent scalar field that tracks internal entanglement density.

---

## 3. Covariant Framework and Minimal Effective Action

### 3.1 Modified Einstein equations

We write the total stress–energy as
\[
T^{\mathrm{total}}_{\mu\nu} = T^{\mathrm{matter}}_{\mu\nu} + T^{\mathrm{ent}}_{\mu\nu},
\]
and postulate that the geometry satisfies the usual Einstein equations
\[
G_{\mu\nu} = \frac{8\pi G}{c^4}\,T^{\mathrm{total}}_{\mu\nu}.
\]

The entanglement sector contributes a term of cosmological-constant type,
\[
T^{\mathrm{ent}}_{\mu\nu}(x) = \Lambda_{\mathrm{ent}}(x)\, g_{\mu\nu},
\]
where
\[
\Lambda_{\mathrm{ent}}(x) = \tilde{\kappa}\,\frac{c^4}{8\pi G k_B \ln 2}\, S_{\mathrm{ent}}(x).
\]
Here \(\tilde{\kappa}\) is a dimensionless coupling. By construction, \(T^{\mathrm{ent}}_{\mu\nu}\) has the same dimensions as \(T^{\mathrm{matter}}_{\mu\nu}\) for any value of \(\tilde{\kappa}\); the modification is dimensionally consistent even if \(\tilde{\kappa}\) is left as a free parameter.

### 3.2 Holographic regulator hypothesis and \(\tilde{\kappa} = -1/4\)

The specific estimate \(\tilde{\kappa} = -1/4\) arises only if one imports the Planck-length regulator and Clausius identification from Jacobson’s horizon setting into the bulk. Concretely, one assumes that volume-law entanglement entropy density contributes an additional term in the horizon entropy balance of the form
\[
\mathrm{d}S_{\mathrm{ent}} \propto S_{\mathrm{ent}}\,\frac{\mathrm{d}V}{4\ell_P}, \quad \mathrm{d}V = \ell_P \mathrm{d}A,
\]
with \(\ell_P\) the Planck length, and that this term participates in the same \(\delta Q = T dS\) relation as the Bekenstein–Hawking entropy. Under these hypotheses, Jacobson-style algebra yields an effective entanglement stress–energy proportional to \(-S_{\mathrm{ent}} g_{\mu\nu}\), corresponding to \(\tilde{\kappa} = -1/4\).

Because there is no rigorous derivation of this regulator relation for non-horizon, volume-law systems, we treat \(\tilde{\kappa} = -1/4\) as a **motivated ansatz under explicit additional assumptions**, not as a prediction. In this paper, \(\tilde{\kappa}\) is left free unless otherwise stated.

### 3.3 Effective scalar-field representation and conservation

The contracted Bianchi identity imposes
\[
\nabla^{\mu} G_{\mu\nu} = 0 \quad\Rightarrow\quad \nabla^{\mu} T^{\mathrm{total}}_{\mu\nu} = 0.
\]
With the purely algebraic ansatz \(T^{\mathrm{ent}}_{\mu\nu} = \Lambda_{\mathrm{ent}} g_{\mu\nu}\), this implies
\[
\nabla^{\mu} T^{\mathrm{matter}}_{\mu\nu} = -\nabla_\nu \Lambda_{\mathrm{ent}}(x) = -\tilde{\kappa}\,\frac{c^4}{8\pi G k_B \ln 2}\, \nabla_\nu S_{\mathrm{ent}}(x).
\]
Thus, matter alone is not conserved wherever \(S_{\mathrm{ent}}\) has gradients; energy–momentum is exchanged between matter and the entanglement sector. To make this exchange law a consequence of an action principle rather than an imposed interpretation, we introduce an effective scalar field \(\phi(x)\) representing the coarse-grained entanglement entropy density,
\[
\phi(x) \equiv S_{\mathrm{ent}}(x).
\]

We consider the effective action
\[
S[g,\phi] = \int d^4x\,\sqrt{-g}\left[ \frac{c^3}{16\pi G} R
- \frac{\beta}{2}\, g^{\mu\nu} (\nabla_\mu \phi)(\nabla_\nu \phi)
- \alpha\, \phi \right],
\]
with constants
\[
\alpha = \tilde{\kappa}\,\frac{c^4}{8\pi G k_B \ln 2}, \qquad \beta > 0.
\]

Varying with respect to \(g_{\mu\nu}\) yields
\[
T^{\mathrm{ent}}_{\mu\nu} = \beta\left( \nabla_\mu \phi\, \nabla_\nu \phi - \tfrac{1}{2} g_{\mu\nu} (\nabla\phi)^2 \right) + \alpha\, \phi\, g_{\mu\nu},
\]
which reduces to the simple \(\Lambda_{\mathrm{ent}} g_{\mu\nu}\) form in the limit where gradients are negligible. Varying with respect to \(\phi\) yields the equation of motion
\[
\beta\, \Box \phi - \alpha = 0,
\]
so that on-shell the total stress–energy is covariantly conserved. In this way, the entanglement sector is represented by an effective scalar field whose stress–energy conservation is guaranteed by the action, clarifying the conservation story.

We emphasize that \(\phi\) is not assumed to be a new fundamental field; it is an effective description of coarse-grained internal entanglement dynamics.

---

## 4. Radial Scaling for Bounded Sources

In the weak-field, nonrelativistic limit, the entanglement contribution can be recast in terms of an effective potential \(\Psi\) satisfying
\[
\nabla^2 \Psi = \kappa_{\mathrm{eff}}\, \rho_{\mathrm{ent}}(\mathbf{x}),
\]
where \(\rho_{\mathrm{ent}}\) encodes an entropic source density and \(\kappa_{\mathrm{eff}}\) is a constant proportional to \(\tilde{\kappa}\). Under spherical symmetry, this integrates to
\[
\Delta a(R) \equiv -\frac{d\Psi}{dR} = \frac{\kappa_{\mathrm{eff}}}{R^2} M_{\mathrm{ent}}(<R),
\]
with enclosed entropic source
\[
M_{\mathrm{ent}}(<R) = 4\pi \int_0^R \rho_{\mathrm{ent}}(r) r^2\,dr.
\]

For a compact source confined within radius \(R_0\), \(M_{\mathrm{ent}}(<R)\) saturates to a constant for \(R > R_0\), yielding an exterior correction \(\Delta a(R) \propto 1/R^2\). A \(1/R\) falloff arises only if the entropic source itself has a scale-free extended profile (e.g. \(\rho_{\mathrm{ent}} \propto 1/r^2\)), in which case \(M_{\mathrm{ent}}(<R) \propto R\).

This result closes the earlier ambiguity between \(1/R\) and \(1/R^2\): for bounded laboratory sources, the entanglement-induced correction outside the source scales as \(1/R^2\).

---

## 5. Screening and Open-System Dynamics

### 5.1 Definition of the screening factor

In realistic devices, decoherence and control errors suppress internal entanglement. To quantify this, we define an *effective screening factor* \(\alpha_{\mathrm{screen}}\) as the ratio of time-integrated internal entanglement in the presence of noise to that in an ideal, noiseless evolution:
\[
\alpha_{\mathrm{screen}} \equiv \frac{\int_0^{\tau} dt\, M^{\mathrm{actual}}_{\mathrm{ent}}(t)}{\int_0^{\tau} dt\, M^{\mathrm{ideal}}_{\mathrm{ent}}(t)},
\]
where \(M_{\mathrm{ent}}(t)\) is an appropriate measure of total internal entanglement content during the protocol of duration \(\tau\).

This definition turns \(\alpha_{\mathrm{screen}}\) into a computable quantity once a master equation is specified.

### 5.2 Example Lindblad model for a transmon chain

As a concrete example, consider a chain of \(N\) fixed-frequency transmon qubits with system Hamiltonian (in an appropriate rotating frame)
\[
H_{\mathrm{sys}} = \sum_{k=1}^N \frac{\omega_k}{2} \sigma^z_k + \sum_{\langle j,k\rangle} J_{jk} (\sigma^+_j \sigma^-_k + \mathrm{h.c.}).
\]

Dominant decoherence channels are energy relaxation and pure dephasing, represented in Lindblad form by
\[
L_{1,k} = \sigma^-_k, \quad L_{\phi,k} = \sigma^z_k,
\]
with rates set by \(T_1\) and \(T_2\). The reduced device state obeys
\[
\dot{\rho} = -\frac{i}{\hbar}[H_{\mathrm{sys}}, \rho] + \sum_k \left( \mathcal{D}[L_{1,k}]\rho + \mathcal{D}[L_{\phi,k}]\rho \right),
\]
where \(\mathcal{D}[L]\rho = L \rho L^{\dagger} - \tfrac{1}{2}\{L^{\dagger}L,\rho\}\).

Given an initial entangled state (e.g. a cluster state), one can compute the evolution of \(S_{\mathrm{int}}(t; A)\) for chosen cuts and thereby \(M_{\mathrm{ent}}(t)\), then evaluate \(\alpha_{\mathrm{screen}}\) for the protocol. This program can be extended to include gate errors by replacing ideal gates with experimentally determined Kraus maps.

### 5.3 Regimes and state choice

Global GHZ states are maximally fragile: their coherence, and thus internal entanglement content, can decay at a rate that scales with \(N\). In contrast, graph or cluster states with local entanglement structure can retain substantial internal entanglement for longer under local noise. For purposes of maximizing \(\int M_{\mathrm{ent}}(t) dt\) in a realistic experiment, locally entangled states are preferable to full-register GHZ states.

Screening is strongly regime-dependent: in macroscopic ensembles with coherence length much smaller than the system size, \(\alpha_{\mathrm{screen}}\) may be effectively negligible; in mesoscopic NISQ devices with \(N \sim 50\) and carefully optimized circuits, \(\alpha_{\mathrm{screen}}\) can plausibly remain at a significant fraction of unity.

---

## 6. Experimental Outlook and Falsification Logic

### 6.1 Observable combinations

Because the absolute value of \(\tilde{\kappa}\) is tied to microscopic assumptions (e.g. holographic regulati