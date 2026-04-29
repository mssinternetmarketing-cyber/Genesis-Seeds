# Key Constants and Unit Conversions
## Physical Reference for the Monette Research Repository

**Folder:** `00_FOUNDATIONAL_DEFINITIONS/`

---

## FUNDAMENTAL CONSTANTS

| Constant | Symbol | Value | Uncertainty | Units |
|---------|--------|-------|------------|-------|
| Speed of light | c | 299,792,458 | exact | m/s |
| Gravitational constant | G | 6.67430 × 10⁻¹¹ | ±0.00015 × 10⁻¹¹ | m³·kg⁻¹·s⁻² |
| Reduced Planck constant | ℏ | 1.054571817 × 10⁻³⁴ | exact (2019 SI) | J·s |
| Boltzmann constant | k_B | 1.380649 × 10⁻²³ | exact (2019 SI) | J·K⁻¹ |
| Elementary charge | e | 1.602176634 × 10⁻¹⁹ | exact (2019 SI) | C |

## DERIVED CONSTANTS USED IN THIS RESEARCH

| Constant | Symbol | Value | Derivation |
|---------|--------|-------|-----------|
| Planck length | ℓ_P | 1.616255 × 10⁻³⁵ m | √(ℏG/c³) |
| Planck mass | m_P | 2.176434 × 10⁻⁸ kg | √(ℏc/G) |
| Planck time | t_P | 5.391247 × 10⁻⁴⁴ s | √(ℏG/c⁵) |
| Planck energy | E_P | 1.956082 × 10⁹ J | m_P c² = √(ℏc⁵/G) |
| Bit-to-entropy conversion | k_B ln 2 | 9.569940 × 10⁻²⁴ J/K | k_B × ln(2) |
| c⁴/(8πG) | — | 4.815 × 10⁴² kg·m⁻¹·s⁻² | Used in κ expression |
| c⁴/(8πG × k_B ln 2) | — | 5.030 × 10⁶⁵ kg·m⁻¹·s⁻²·K·bit⁻¹ | Full coupling prefactor |

## UNIT CONVERSIONS FOR EXPERIMENTAL PREDICTIONS

| Quantity | SI unit | Conversion |
|---------|---------|-----------|
| 1 bit of entanglement entropy | dimensionless | → k_B ln 2 = 9.57 × 10⁻²⁴ J/K of thermodynamic entropy |
| Pressure sensitivity target | Pa | 10⁻⁶ Pa = 10⁻⁶ N/m² = 10⁻⁵ μbar |
| Acceleration sensitivity | m/s² | 10⁻¹² m/s² = 10⁻¹³ g (Earth gravity = 9.81 m/s²) |
| Coherent ensemble (10⁶ ⁸⁷Rb atoms) | atoms | Mass ≈ 1.44 × 10⁻¹⁹ kg; density ≈ 10¹⁴ atoms/cm³ at BEC |

## EXPERIMENTAL PARAMETER ESTIMATES

### ⁸⁷Rb Atomic Ensemble (Proposed Experiment)
- Atomic mass: 86.909 u = 1.443 × 10⁻²⁵ kg
- Ground state: 5S₁/₂, F=1 or F=2
- Typical BEC density: 10¹³–10¹⁴ atoms/cm³
- Coherence time in optical trap: 0.1–10 s
- GHZ state entanglement depth: Up to ~10⁴ atoms with current technology
- Required for experiment: N ≥ 10⁶ atoms with entanglement depth ≥ 10³

### Atom Interferometer (Kasevich-type)
- Baseline acceleration sensitivity: δa ≈ 10⁻¹² m/s²
- Corresponding κ̃ sensitivity: δ|κ̃| ≈ 3.7 × 10⁻¹³ (from Section 6 of master paper)
- Integration time for 1000 runs: ~10³ × (shot duration) ≈ weeks to months

## COUPLING CONSTANT NUMERICAL EXAMPLES

For $S_{\text{ent}} = 10^{18}$ bit/m³ (a very optimistic estimate for current hardware):

| κ̃ value | Physical scenario | Pressure term |
|---------|-----------------|--------------|
| -1/4 (ideal) | Perfect isolation, no decoherence | 1.26 × 10⁴⁰ Pa (purely theoretical) |
| -1/4 × 10⁻² | Light screening (α_screen = 10⁻²) | 1.26 × 10³⁸ Pa |
| -1/4 × 10⁻⁴ | Heavy screening (α_screen = 10⁻⁴) | 1.26 × 10³⁶ Pa |
| < 10⁻¹⁵ (falsification) | Framework irrelevant at lab scale | < 6.3 × 10²⁵ Pa |

Note: These are the coupling *contribution*, not net forces. The actual measurable force requires integration over the source volume and comparison with normal matter gravity — see Δa formula derivation (Section 6 of master paper, marked [OPEN PROBLEM]).
