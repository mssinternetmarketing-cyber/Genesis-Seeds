# PEIG Framework — Phase Entanglement Integrity Gate
### A 16-Paper Pre-Registered Quantum Coherence Research Series

**Author:** Kevin Monette | Independent Researcher | Hopkinsville, KY  
**Contact:** mssinternetmarketing@gmail.com  
**Status:** Pre-registration complete | Hardware runs pending  
**Last Updated:** March 2026  

[![DOI](https://zenodo.org/badge/1189467983.svg)](https://doi.org/10.5281/zenodo.19226623)

---

## What Is This?

Quantum computers lose their advantage the moment noise disrupts phase
relationships between qubits. Error correction helps — but it's costly,
hardware-intensive, and not yet practical at scale.

The PEIG Framework asks a different question:

> **Can a protocol RESTORE phase coherence through entanglement itself —
> without error correction?**

This repository contains the complete research series developing and
testing the **Infinite Lineage Protocol (ILP)** — an iterative
entanglement scheme driven by the **BCP gate**, measured by
**Phase Coherence Measure (PCM)**: a metric sensitive to phase structure
that standard fidelity tests miss entirely.

---

## Key Results

| Result | Value | Paper |
|--------|-------|-------|
| Simulation milestone | 12/12 unique phases + 90% high-PCM @ depth-4 | XV |
| BCP hardware validation | R²=0.9999 on ibm_sherbrooke (Eagle r3) | Lambda-Mixing |
| Hardware visibility | A₀ = 0.7858 | Lambda-Mixing |
| Decoherence rate | 0.00363 μs⁻¹ per CNOT | Lambda-Mixing |
| Hardware-optimal α | 0.40 (vs. simulation optimum 0.367) | XVI |
| Predicted restoration ratio (depth-4) | 2.46× | XVI |
| Predicted SNR | ≥39 at all depths | XVI |
| Pre-registered primary criterion | PCM_hw(d=2)/PCM_hw(d=0) > 1.10× | XVI |

---

## Critical Discovery: BCP Gate Non-Unitarity

The BCP gate U = α·CNOT + (1−α)·I₄ is **non-unitary** — no unitary
decomposition exists. Correct hardware implementation is **probabilistic
circuit selection**: apply CNOT with probability α, apply identity with
probability (1−α). Validated on ibm_sherbrooke at R²=0.9999.

This is a transferable result for any researcher designing mixed-unitary
quantum channels on superconducting hardware.

---

## Paper Series

| Paper | Title | Status |
|-------|-------|--------|
| I–IX | PEIG theoretical foundations, topology, PCM definition | Complete |
| X–XIV | Globe topology, co-rotating frame, BCP gate design | Complete |
| XV | Globe+Co-Rotating+ILP: simulation milestone | Complete |
| Lambda-Mixing | BCP hardware validation on ibm_sherbrooke | Complete — arXiv 2026 |
| XVI | Hardware pre-registration: ILP on ibm_sherbrooke | Pre-registered |

---

## Hardware Protocol (Paper XVI)

| Parameter | Value |
|-----------|-------|
| Backend | ibm_sherbrooke (Eagle r3) or ibm_brisbane |
| Shots | 8,192 per circuit instance |
| Depths | 0, 1, 2, 3, 4 |
| Total circuits | 150 instances (with tomography) |
| BCP α (revised) | 0.40 |
| Implementation | Probabilistic circuit selection |
| Error mitigation | None (raw counts) |
| Pre-registration | Filed prior to hardware access |

### Pre-Registered Success Criteria

| Criterion | Threshold | Test |
|-----------|-----------|------|
| PRIMARY | Ratio(d=2)/Ratio(d=0) > 1.10× | Paired t-test, p < 0.05 |
| SECONDARY | Monotonic increase d=0 to d=2 | Spearman ρ > 0 |
| TERTIARY | \|PCM_hw\| > 0.05 at all depths | vs. noise floor |
| NULL CONTROL | Z-basis shows no depth trend | R² < 0.2 |

---

## Open Questions

1. Does PCM restoration survive on trapped-ion hardware (IonQ Aria,
   Quantinuum H-series) where CNOT fidelity exceeds 99.5%?
2. Is hardware visibility A₀ = 0.7858 reproducible across Eagle r3
   processors and calibration cycles?
3. Does the α shift (0.367 → 0.40) follow a predictable function of
   noise rate — making BCP self-calibrating across hardware backends?
4. What is the maximum lineage depth before noise fully suppresses PCM
   restoration — a practical coherence horizon for NISQ devices?

---

## Citation

```bibtex
@software{monette_peig_2026,
  author    = {Kevin Monette},
  title     = {PEIG Framework: Phase Entanglement Integrity Gate — 
               Papers I–XVI},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.19226624},
  url       = {https://doi.org/10.5281/zenodo.19226624}
}


[![DOI](https://zenodo.org/badge/1189467983.svg)](https://doi.org/10.5281/zenodo.19226623)
