import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# 1. Physical constants
# -----------------------------
G = 6.67430e-11       # gravitational constant [m^3 kg^-1 s^-2]
c = 2.99792458e8      # speed of light [m/s]
m_hand = 0.5          # test mass (hand) [kg]

# -----------------------------
# 2. Sphere & coupling model
# -----------------------------
class CoherenceSphere:
    def __init__(self,
                 radius=0.12,          # [m] ~ basketball radius
                 mass=1.0,             # [kg] ordinary mass (tunable)
                 S_total=1e20,         # [bits] total "entanglement entropy"
                 alpha=1e-40,          # [N m^2 / (bit kg)] effective info–gravity coupling
                 repulsive=True):
        self.R = radius
        self.M = mass
        self.S_total = S_total
        self.alpha = alpha
        self.repulsive = repulsive

    def info_density(self):
        """Uniform information density inside sphere [bits/m^3]."""
        V = 4/3 * np.pi * self.R**3
        return self.S_total / V

    def accel(self, r):
        """
        Net radial acceleration at distance r from center [m/s^2].

        Model:
          a(r) = a_mass(r) + a_info(r)
          a_mass(r) = -G M_enc(r) / r^2
          a_info(r) = +/- alpha * S_density * f(r)

        Here we use a simple shell-like info term localized near R.
        """
        r = np.asarray(r)
        a_mass = np.zeros_like(r)

        # Ordinary mass term (attractive)
        # Inside sphere: use enclosed mass proportional to r^3
        inside = r < self.R
        outside = ~inside

        # Avoid divide-by-zero at r=0
        r_safe = np.where(r == 0, 1e-12, r)

        if np.any(inside):
            M_enc = self.M * (r[inside]**3 / self.R**3)
            a_mass[inside] = -G * M_enc / (r_safe[inside]**2)
        if np.any(outside):
            a_mass[outside] = -G * self.M / (r_safe[outside]**2)

        # Information-based term (repulsive shell around R)
        S_rho = self.info_density()   # [bits/m^3]

        # Simple shell profile centered at R with width w
        w = 0.05 * self.R  # 5% of radius
        shell_profile = np.exp(-((r - self.R)**2) / (2 * w**2))

        sign = +1.0 if self.repulsive else -1.0
        a_info = sign * self.alpha * S_rho * shell_profile

        return a_mass + a_info

    def force_on_mass(self, r, m_test=m_hand):
        """Force on a test mass at distance r [N]."""
        return m_test * self.accel(r)

# -----------------------------
# 3. Helper: scenario builder
# -----------------------------
def build_scenarios():
    """
    Return three spheres: weak, moderate, strong coupling.
    Parameters are chosen so you can tune until they match your
    earlier weak/moderate/strong force tables.
    """
    R = 0.12          # m
    M = 1.0           # kg (you can set to 0 if you want pure info term)

    # These S_total and alpha values are arbitrary starting guesses.
    weak = CoherenceSphere(radius=R, mass=M,
                           S_total=1e18, alpha=1e-45, repulsive=True)
    moderate = CoherenceSphere(radius=R, mass=M,
                               S_total=1e20, alpha=1e-40, repulsive=True)
    strong = CoherenceSphere(radius=R, mass=M,
                             S_total=1e22, alpha=1e-35, repulsive=True)
    return weak, moderate, strong

# -----------------------------
# 4. Detector noise model
# -----------------------------
def noisy_force(true_force, rel_noise_level=0.01, abs_noise=1e-4):
    """
    Add simple Gaussian noise.

    rel_noise_level : fractional noise (e.g. 0.01 = 1%)
    abs_noise       : absolute noise floor [N]
    """
    true_force = np.asarray(true_force)
    sigma = np.sqrt((rel_noise_level * np.abs(true_force))**2 + abs_noise**2)
    return true_force + np.random.normal(0.0, sigma, size=true_force.shape)

# -----------------------------
# 5. Main plotting routine
# -----------------------------
def run_simulation():
    # Build scenarios
    weak, moderate, strong = build_scenarios()

    # Radial distances: from sphere surface out to 1 m
    r_surface = weak.R
    r = np.linspace(r_surface + 0.01, 1.0, 200)  # 1 cm above surface to 1 m

    # Compute true forces
    F_weak = weak.force_on_mass(r)
    F_mod  = moderate.force_on_mass(r)
    F_str  = strong.force_on_mass(r)

    # Add noise for one example detector view
    F_mod_noisy = noisy_force(F_mod, rel_noise_level=0.05, abs_noise=1e-3)

    # Plot: force vs distance
    plt.figure(figsize=(8, 5))
    plt.loglog(r, np.abs(F_weak), label="Weak coupling")
    plt.loglog(r, np.abs(F_mod),  label="Moderate coupling (true)")
    plt.loglog(r, np.abs(F_str),  label="Strong coupling")
    plt.loglog(r, np.abs(F_mod_noisy), 'k.', alpha=0.3,
               label="Moderate + detector noise")

    plt.xlabel("Distance from center r [m]")
    plt.ylabel("Force on 0.5 kg hand |F(r)| [N]")
    plt.title("Simulated force vs distance for coherence sphere")
    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.4)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_simulation()
