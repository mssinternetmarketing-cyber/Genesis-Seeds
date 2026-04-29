# 00_FOUNDATIONAL_DEFINITIONS

**Repository:** Monette Research — Entropic Gravity & PEIG Framework  
**Role:** Conceptual and mathematical bedrock for the entire repository  
**Status:** Canonical — all other folders depend on definitions established here  
**Last Updated:** March 2026

---

## Purpose

This folder contains the foundational definitions, axioms, and conventions that
underpin every paper, derivation, and claim in this repository. Before reading
any document in `01_PHYSICS_CORE/`, `03_PEIG_FRAMEWORK/`, or elsewhere, a
reader should be familiar with the content here.

Think of this folder as the **dictionary and grammar** of the research program.
Every technical term used in this repository is defined here first, with
precisely the meaning it carries throughout.

---

## Contents — The `sections/` Folder

| File | Topic | Key Contribution |
|---|---|---|
| `01_universe_and_history.md` | The Universe as $\mathcal{U} = (\mathcal{S} \mid r)$ | Establishes why reality is a conditioned description; defines time, structure, and gravity as constraint accumulation |
| `02_entropy_and_information.md` | All entropy definitions + bit-to-entropy conversion | Canonical conversion table; resolves the most common dimensional error in information-theoretic gravity |
| `03_constraint_manifold.md` | $\mathcal{S}$, $\mathcal{O}(r)$, shot scaling, entropy bias | Explains the 40–50% NISQ plateau as a measurement artifact; provides the bias correction formula |
| `04_peig_definitions.md` | P, E, I, G — formal definitions and dynamics | Full PEIG state vector, sub-metrics, the Identity ODE, and the physical vs. cognitive framework distinction |
| `05_landauer_etl_axioms.md` | ETI axioms A1–A5, lemmas L1–L5, predictions P1–P3 | Complete formal treatment of Landauer's principle as an operational constraint, not a fundamental law |
| `06_notation_and_conventions.md` | Every symbol, unit, and sign convention | The master symbol table; resolves all notation inconsistencies identified across the corpus |

---

## How This Folder Relates to the Rest of the Repository

```
00_FOUNDATIONAL_DEFINITIONS/          ← Start here
        ↓
01_PHYSICS_CORE/
    ├── A_ENTROPIC_GRAVITY/           ← Uses §02 (entropy), §06 (notation)
    ├── B_CONSTRAINT_MANIFOLDS/       ← Uses §03 (constraint manifold)
    └── C_LANDAUER_ETI/               ← Uses §05 (Landauer axioms)
        ↓
03_PEIG_FRAMEWORK/                    ← Uses §04 (PEIG definitions)
        ↓
04_SPECULATIVE_EXTENDED/              ← Uses all of the above
```

No document in this repository introduces a new symbol or concept without
first grounding it in one of the six sections here.

---

## Key Decisions Recorded Here

The following decisions were made during the Phase 2 audit and are encoded
in these definitions:

1. **$S_{\text{ent}}$ is always entanglement entropy density** (bit/m³),
   never total entropy. Total entropy uses $S_{\text{vN}}(\rho)$ or
   $\mathcal{S}$.

2. **Negentropy $\mathcal{N}$ cannot be substituted for $S_{\text{ent}}$**
   in the Einstein equation — they make opposite physical predictions.

3. **$\tilde{\kappa}$ (with tilde) is always dimensionless.** The
   dimensionful version $\kappa$ (without tilde) is rarely used and always
   labeled explicitly.

4. **The Cramér-Rao bound is written** $\text{Var}[\hat{S}] \geq [F_Q(\rho)]^{-1}/\nu$,
   not with Fisher information as a function of the scalar entropy.

5. **$\tilde{\kappa} = -1/4$ is a first-principles estimate** under the
   holographic Planck-scale regulator hypothesis, not a fully derived result.
   This is explicitly stated in Section 02 of the entropic gravity paper.

6. **The screening factor range is $\alpha_{\text{screen}} \in [10^{-4}, 10^{-2}]$**
   throughout. The value $[10^{-5}, 10^{-3}]$ appearing in one source file
   was an error and has been corrected.

---

## For New Readers

If you are new to this research program, read the sections in order:

1. Start with **Section 01** to understand the conceptual framework
2. Read **Section 02** to understand how entropy and information are handled
3. Read **Section 06** to familiarize yourself with the notation
4. Then proceed to whichever physics paper interests you most

If you are a physicist reviewing the entropic gravity work specifically:
- Section 02 (bit-to-entropy conversion) and Section 06 (sign conventions)
  are the most immediately relevant to the modified Einstein equation
- Section 03 explains the NISQ entropy plateau result
- The extrapolation boundary (horizon physics → laboratory physics) is
  explicitly addressed in `01_PHYSICS_CORE/A_ENTROPIC_GRAVITY/sections/03_extrapolation_boundary.tex`
