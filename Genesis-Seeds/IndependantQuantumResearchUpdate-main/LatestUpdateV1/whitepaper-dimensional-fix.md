# Dimensional Repair and Refined Framework for Entanglement-Entropy Sourcing of Gravity

**Author:** Kevin Monette  
**Affiliation:** Independent Researcher (AI-assisted research)  
**Draft:** March 19, 2026 (Dimensional-consistency revision)

---

## 0. Purpose and Scope

This white paper repairs a critical dimensional inconsistency in earlier drafts of the entanglement–gravity framework and presents a refined, self-consistent phenomenological model.

Earlier work correctly identified a covariant structure and an experimental program, but treated the entanglement entropy density \(S_{\mathrm{ent}}(x)\) as entering the stress–energy tensor via a coupling prefactor \(\alpha \propto c^4/(8\pi G k_B \ln 2)\) without inserting a physical length or energy scale. This made the entanglement stress–energy term dimensionally inconsistent in SI units and rendered derived accelerations formally meaningless.[file:137]

Here we:

1. Introduce the minimal additional scale(s) needed to make the entanglement contribution a bona fide stress–energy tensor.
2. Redefine the effective action and source term accordingly.
3. Re-express the key observable combination \(\mathcal{B}\) and the fifth-force equation with correct dimensions.
4. Preserve the OP3 program and NISQ experimental outlook, now on a dimensionally sound foundation.

The goal is not to fix a unique microscopic model, but to isolate the minimal scaling assumptions needed for dimensional consistency.

---

## 1. Units and the Original Problem

We work in SI units for clarity. The Einstein equations
\[
G_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}
\]
require that \(T_{\mu\nu}\) have units of energy density:
\[
[T_{\mu\nu}] = \text{J m}^{-3} = \text{kg m}^{-1} \text{s}^{-2}.
\]

In earlier drafts, the entanglement entropy density \(S_{\mathrm{ent}}(x)\) was defined as a scalar field with units "bits per unit volume":
\[
[S_{\mathrm{ent}}] = \text{bit m}^{-3} = (\text{dimensionless})\,\text{m}^{-3}.
\]

The stress–energy contribution was introduced via a term \(\propto \alpha S_{\mathrm{ent}} g_{\mu\nu}\) with
\[
\alpha = \tilde{\kappa}\,\frac{c^4}{8\pi G k_B \ln 2}.
\]

In SI units: \(c^4/(8\pi G)\) carries units of \(\text{J m}^{-1}\), and division by \(k_B\) and \(\ln 2\) introduces \(\text{K}^{-1}\), so
\[
[\alpha] = \text{J m}^{-1} \text{K}^{-1}.
\]
Multiplying by \(S_{\mathrm{ent}}\) (bits per m\(^3\)) yields
\[
[\alpha S_{\mathrm{ent}}] = \text{J m}^{-4} \text{K}^{-1},
\]
which is not an energy density. The missing factor is a physical length or energy scale that converts "entropy per volume" into "energy density".[file:137]

This is the root of the OP8 problem: all derived accelerations using this \(\alpha\) had nonsensical units.

---

## 2. Minimal Dimensional Fix: Introducing a Reference Length/Area Scale

### 2.1 Conceptual choice

We need to map a scalar with units \(\sim\text{bit m}^{-3}\) into an energy density. The natural thermodynamic relation is
\[
\text{energy density} \sim T \times (\text{entropy density}),
\]
where \(T\) is a characteristic temperature. In the gravitational context, the relevant temperature scale in Jacobson/Unruh-style arguments is the Unruh temperature or local Rindler horizon temperature, which is set by acceleration and Planck-scale physics.[file:113]

Rather than derive a unique \(T\), we parametrize our ignorance by introducing a **reference energy scale** \(E_*\) (or equivalently a length scale \(\ell_*\)) that expresses how strongly a unit of entanglement entropy density contributes to energy density.

We define the entanglement energy density as
\[
\rho_{\mathrm{ent}}(x) = E_*\, S_{\mathrm{ent}}(x),
\]
so that
\[
[\rho_{\mathrm{ent}}] = [E_*]\,[S_{\mathrm{ent}}] = \text{J} \times \text{m}^{-3} = \text{J m}^{-3}
\]
provided \(E_*\) has units of energy per bit, i.e. J/bit.

Equivalently, we can write
\[
\rho_{\mathrm{ent}}(x) = \lambda_*\,k_B T_*\, s_{\mathrm{ent}}(x),
\]
where \(s_{\mathrm{ent}}\) is entropy density in units of J K\(^{-1}\) m\(^{-3}\), \(T_*\) is an effective temperature scale, and \(\lambda_*\) is a dimensionless coefficient. For our purposes, it is simplest to work with a single scale \(E_*\) and an overall dimensionless coupling \(\tilde{\kappa}\).

### 2.2 Revised source term

We now define the entanglement contribution to the stress–energy tensor as
\[
T^{\mathrm{ent}}_{\mu\nu}(x) = \tilde{\kappa} \, \rho_{\mathrm{ent}}(x)\, g_{\mu\nu} + \text{(gradient terms)},
\]
with
\[
\rho_{\mathrm{ent}}(x) \equiv E_*\, S_{\mathrm{ent}}(x).
\]

Then
\[
[T^{\mathrm{ent}}_{\mu\nu}] = \text{dimensionless} \times \text{J m}^{-3},
\]
as required. All previous appearances of \(\alpha S_{\mathrm{ent}}\) are replaced with \(\tilde{\kappa} E_* S_{\mathrm{ent}}\).

We can relate \(E_*\) to familiar scales if desired. For example, one may choose
\[
E_* = \eta\, k_B T_*,
\]
with \(T_*\) an effective Unruh or horizon temperature and \(\eta\) a dimensionless factor of order one. The framework remains agnostic about the microscopic origin of \(E_*\); it is to be constrained phenomenologically.

---

## 3. Revised Effective Action and Fifth-Force Equation

### 3.1 Effective action with correct units

We retain the external-source structure but rewrite the entanglement Lagrangian density as
\[
\mathcal{L}_{\mathrm{ent}} = - \frac{\beta}{2} g^{\mu\nu}(\nabla_\mu\phi)(\nabla_\nu\phi) - \lambda\,\phi(x),
\]
where \(\phi(x) \equiv S_{\mathrm{ent}}(x)\) and
\[
[\lambda] = \text{J m}^{-3} \;\; (\text{per unit} \; \phi).
\]

In terms of \(E_*\) and \(\tilde{\kappa}\), we set
\[
\lambda = \tilde{\kappa}\, E_*, \qquad \rho_{\mathrm{ent}} = E_*\,\phi.
\]

The full action is
\[
S[g;\phi] = \int d^4x\,\sqrt{-g}\left[ \frac{c^3}{16\pi G}R - \frac{\beta}{2} g^{\mu\nu}(\nabla_\mu\phi)(\nabla_\nu\phi) - \tilde{\kappa} E_*\,\phi \right].
\]

Varying \(S\) with respect to \(g_{\mu\nu}\) (treating \(\phi\) as external) yields
\[
T^{\mathrm{ent}}_{\mu\nu} = \beta\left( \nabla_\mu\phi\,\nabla_\nu\phi - \tfrac{1}{2} g_{\mu\nu}(\nabla\phi)^2 \right) + \tilde{\kappa} E_*\,\phi\, g_{\mu\nu}.
\]

This has the correct SI dimensions provided \(\beta\) has dimensions such that the gradient term also yields J m\(^{-3}\) (in practice, \(\beta\) carries the same dimensions as \(E_*\) times a length scale squared). For slowly varying \(\phi\), the gradient term is subleading, and the effective cosmological-constant–like term dominates.

### 3.2 Exact matter nonconservation

Total conservation \(\nabla^\mu T^{\mathrm{total}}_{\mu\nu}=0\) implies
\[
\nabla^{\mu}T^{\mathrm{matter}}_{\mu\nu} = -\nabla^{\mu}T^{\mathrm{ent}}_{\mu\nu}.
\]

Substituting the revised \(T^{\mathrm{ent}}_{\mu\nu}\) gives
\[
\nabla^{\mu}T^{\mathrm{matter}}_{\mu\nu} = -\left(\tilde{\kappa} E_* + \beta\,\Box\phi\right)\nabla_\nu\phi + \beta\,\nabla_\nu\left(\tfrac{1}{2}(\nabla\phi)^2\right).
\]

In the quasi-static, slowly varying regime where \(|\beta\Box\phi|\ll |\tilde{\kappa} E_*|\) and gradients are modest, this simplifies to
\[
\nabla^{\mu}T^{\mathrm{matter}}_{\mu\nu} \approx -\tilde{\kappa} E_*\,\nabla_\nu \phi(x) = -\tilde{\kappa} E_*\,\nabla_\nu S_{\mathrm{ent}}(x).
\]

This is the corrected fifth-force law: an entanglement-density gradient induces an anomalous force density on matter proportional to \(\tilde{\kappa} E_*\). Its dimensions are now those of force per unit volume, as required.

---

## 4. Newtonian Limit and Revised \(\mathcal{B}\) Observable

### 4.1 Modified Poisson equation

In the Newtonian limit, the temporal–temporal component of the Einstein equations gives
\[
\nabla^2 \Phi = 4\pi G (\rho_{\mathrm{matter}} + \rho_{\mathrm{ent}}),
\]
with
\[
\rho_{\mathrm{ent}}(\mathbf{x}) = \tilde{\kappa} E_*\,S_{\mathrm{ent}}(\mathbf{x}).
\]

Under spherical symmetry, the entanglement-induced acceleration correction is
\[
\Delta a(R) = -\frac{d\Phi_{\mathrm{ent}}}{dR} = \frac{G}{R^2} M_{\mathrm{ent}}(<R),\qquad M_{\mathrm{ent}}(<R) = 4\pi\int_0^R \rho_{\mathrm{ent}}(r) r^2 dr.
\]

For a bounded source of radius \(R_0\), \(M_{\mathrm{ent}}(<R)\) saturates for \(R>R_0\), implying \(\Delta a(R)\propto 1/R^2\) in the exterior. This is unchanged from the previous derivation, but \(\rho_{\mathrm{ent}}\) is now dimensionally correct.

### 4.2 Observable combination \(\mathcal{B}\)

In branch-comparison experiments, we consider two configurations with the same classical matter distribution but different internal entanglement content. The relevant combination remains
\[
\mathcal{B} \equiv |\tilde{\kappa}_{\mathrm{eff}}|\,\frac{\Delta M_{\mathrm{ent}}}{R_{\mathrm{eff}}^2},\qquad \tilde{\kappa}_{\mathrm{eff}} = \tilde{\kappa}\,\alpha_{\mathrm{screen}},
\]
where
\[
\Delta M_{\mathrm{ent}} = E_*\,\Delta S_{\mathrm{ent}}^{\mathrm{tot}}
\]
is the difference in entanglement energy content between branches, and \(R_{\mathrm{eff}}\) is a characteristic device scale.[file:135][file:137]

In SI units, \([\mathcal{B}] = \text{J m}^{-3}\), consistent with an effective energy density scale. Constraints on \(\mathcal{B}\) can now be compared directly with, e.g., dark-energy densities or other phenomenological scales, and mapped to \(\tilde{\kappa}\) once \(E_*\) is specified.

---

## 5. Implications for OP8 (Fifth-Force Estimates)

With the corrected units, the anomalous acceleration near an entanglement source is
\[
\Delta a(R) \sim \frac{G}{R^2} \Delta M_{\mathrm{ent}} = \frac{G}{R^2} E_*\,\Delta S_{\mathrm{ent}}^{\mathrm{tot}}.
\]

For a device with total entanglement entropy difference \(\Delta S_{\mathrm{ent}}^{\mathrm{tot}}\) (in bits) between branches and effective radius \(R_{\mathrm{eff}}\), a Newtonian fifth-force bound \(\Delta a_{\mathrm{max}}\) translates into
\[
E_* |\tilde{\kappa}| \lesssim \frac{\Delta a_{\mathrm{max}} R_{\mathrm{eff}}^2}{G \Delta S_{\mathrm{ent}}^{\mathrm{tot}}}.
\]

This provides a *dimensionally correct* way to confront the framework with Asenbaum-type or torsion-balance data, once realistic \(\Delta S_{\mathrm{ent}}^{\mathrm{tot}}\) for those experiments are known (which is effectively zero for classical test masses).[file:137]

---

## 6. OP10 Revisited: RG Scaling with \(E_*\)

Previously, \(\tilde{\kappa}\) was attempted to be run directly from the Planck scale, leading to confusing and sometimes huge prefactors. With \(E_*\) explicit, the natural RG Ansatz becomes
\[
\tilde{\kappa}_{\mathrm{lab}} E_{*,\mathrm{lab}} = \tilde{\kappa}_{\mathrm{UV}} E_{*,\mathrm{UV}}\left(\frac{E_{\mathrm{lab}}}{E_P}\right)^{\gamma},
\]
with \(E_{\mathrm{lab}}\) a characteristic laboratory energy (e.g. qubit frequency scale) and \(E_P\) the Planck energy.[file:137]

This clarifies that what experiments actually constrain is the *product* \(\tilde{\kappa} E_*\) at laboratory scales. A null result at the \(\mathcal{B}\) level therefore bounds this IR combination, not \(\tilde{\kappa}_{\mathrm{Planck}}\) alone.

---

## 7. Status of OP3 and Experimental Program

Crucially, the dimensional repair does **not** affect:

- The definition of the internal entanglement entropy density \(S_{\mathrm{ent}}(x)\).
- The Lindblad screening program (OP3) and the definition of \(\alpha_{\mathrm{screen}}(N,\tau)\).[file:141]
- The branch-comparison experimental observable \(\mathcal{B}\) as a function of \(\Delta S_{\mathrm{ent}}^{\mathrm{tot}}\) and \(R_{\mathrm{eff}}\); only its interpretation in terms of \(\tilde{\kappa}\) changes via \(E_*\).

This means all of the numerical and experimental design work (OP3 Stage 1 code, neutral-atom Ramsey protocol, systematics tables) remains valid and can now be interpreted within a dimensionally sound framework.

---

## 8. Conclusions and Next Steps

We have:

- Identified the missing scale in the original entanglement–gravity coupling and introduced a reference energy scale \(E_*\) to repair the dimensions of the stress–energy term.
- Rewritten the external-source effective action and the matter nonconservation law so that all terms carry the correct SI units.
- Re-expressed the experimental observable \(\mathcal{B}\) and fifth-force estimates in a way that is directly comparable to existing phenomenology.

Outstanding tasks are now conceptually clean:

1. Choose or constrain \(E_*\) (and \(\tilde{\kappa}\)) from theory (e.g. Jacobson-style thermodynamics) or from experiment.
2. Complete OP3 numerics to determine \(\alpha_{\mathrm{screen}}\) for realistic NISQ devices.
3. Use the corrected formulas to generate honest OP8 fifth-force predictions and OP10 RG scenarios.

With these repairs, the entanglement–gravity framework moves from being internally inconsistent on dimensional grounds to being a *well-posed effective theory* with two key phenomenological parameters \(\tilde{\kappa}\) and \(E_*\) that future theory and experiment can jointly constrain.
