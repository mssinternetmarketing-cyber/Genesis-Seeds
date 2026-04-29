import numpy as np
import matplotlib.pyplot as plt


# ---------- 1. Physical constants ----------
G = 6.67430e-11
M_CRAFT = 500.0   # craft mass [kg]


# ---------- 2. Core sphere model (same structure as before) ----------
class CoherenceSphere:
    def __init__(self, radius=0.12, mass=1.0, S_total=1e22,
                 alpha=1e-37, repulsive=True, omega=80.0, phase=0.0):
        self.R = radius
        self.M = mass
        self.S_total = S_total
        self.alpha = alpha
        self.repulsive = repulsive
        self.omega = omega
        self.phase = phase

    def info_density(self):
        V = 4/3 * np.pi * self.R**3
        return self.S_total / V

    def accel(self, r):
        r = np.asarray(r, dtype=float)
        a_mass = np.zeros_like(r)
        r_safe = np.where(r == 0, 1e-12, r)

        inside = r < self.R
        outside = ~inside

        if np.any(inside):
            M_enc = self.M * (r[inside]**3 / self.R**3)
            a_mass[inside] = -G * M_enc / (r_safe[inside]**2)
        if np.any(outside):
            a_mass[outside] = -G * self.M / (r_safe[outside]**2)

        S_rho = self.info_density()
        w = 0.05 * self.R
        shell_profile = np.exp(-((r - self.R)**2) / (2*w**2))

        sign = +1.0 if self.repulsive else -1.0
        a_info = sign * self.alpha * S_rho * shell_profile
        return a_mass + a_info

    def force_on_mass(self, r, m_test):
        return m_test * self.accel(r)


# ---------- 3. 3‑sphere drive with “mode switching” ----------
class UFODrive:
    """
    Drive can switch between modes:
      0 = hover, 1 = forward thrust, 2 = 90° side thrust, 3 = braking.
    """
    def __init__(self, spheres, base_radius=0.5, vertical_offset=0.3,
                 max_coupling=12.0):
        self.spheres = spheres
        self.base_radius = base_radius
        self.vertical_offset = vertical_offset
        self.max_coupling = max_coupling

    def mode_schedule(self, t):
        """
        Returns (mode, throttle) as a function of time.
        Total duration ~ 20 s split into segments:
          0–5 s: hover
          5–10 s: forward thrust (x direction)
          10–15 s: instant 90° turn (y direction)
          15–20 s: braking (opposite velocity)
        """
        if t < 5.0:
            return 0, 0.6    # hover
        elif t < 10.0:
            return 1, 1.0    # accelerate forward
        elif t < 15.0:
            return 2, 1.0    # sideways 90° thrust
        else:
            return 3, 1.0    # braking

    def resonance_factor(self, t, throttle):
        """
        Aggregate resonance amplification from internal phases and throttle.
        """
        phases = np.array([s.omega * t + s.phase for s in self.spheres])
        spread = np.max(phases) - np.min(phases)
        phase_factor = 1.0 - np.clip(spread / np.pi, 0, 1)
        base = 1.0 + self.max_coupling * throttle * phase_factor
        return base * np.array([0.95, 1.05, 1.0])

    def thrust_vector(self, t, vel):
        """
        Ideal thrust direction based on the current maneuver mode.
        We use the velocity vector in braking mode.
        """
        mode, throttle = self.mode_schedule(t)

        if mode == 0:  # hover: cancel gravity/keep mostly vertical support
            direction = np.array([0.0, 0.0, 1.0])
        elif mode == 1:  # accelerate forward along +x
            direction = np.array([1.0, 0.0, 0.1])
        elif mode == 2:  # hard 90° turn: thrust +y, slight support
            direction = np.array([0.0, 1.0, 0.1])
        else:  # braking opposite to current velocity
            if np.linalg.norm(vel) < 1e-9:
                direction = np.array([0.0, 0.0, 0.0])
            else:
                direction = -vel / np.linalg.norm(vel)

        # Normalise and scale by throttle
        if np.linalg.norm(direction) > 0:
            direction = direction / np.linalg.norm(direction)
        return direction, throttle

    def thrust_on_craft(self, t, vel):
        """
        Effective thrust from the spheres, treated as adjustable vector drive.
        """
        direction, throttle = self.thrust_vector(t, vel)
        if np.allclose(direction, 0):
            return np.zeros(3)

        # Use resonance factor magnitude as thrust scale
        factors = self.resonance_factor(t, throttle)
        scale = np.mean(factors) * 1e-7   # 1e-7 N base; tune for stronger effects
        return scale * direction * M_CRAFT  # F = m * a_effective


# ---------- 4. Craft dynamics in gravity ----------
def run_ufo_maneuver_sim():
    # Three identical spheres
    spheres = [
        CoherenceSphere(phase=0.0),
        CoherenceSphere(phase=1.0),
        CoherenceSphere(phase=2.0),
    ]
    drive = UFODrive(spheres)

    # Initial state: hovering 100 m above origin
    pos = np.array([0.0, 0.0, 100.0])
    vel = np.array([0.0, 0.0, 0.0])

    dt = 0.01
    T = 20.0
    steps = int(T / dt)

    pos_hist = np.zeros((steps, 3))
    vel_hist = np.zeros((steps, 3))
    thrust_hist = np.zeros((steps, 3))
    mode_hist = np.zeros(steps)

    g_vec = np.array([0.0, 0.0, -9.81])  # Earth gravity

    for i in range(steps):
        t = i * dt

        F_drive = drive.thrust_on_craft(t, vel)        # from spheres
        F_grav = M_CRAFT * g_vec                       # gravity
        F_net = F_drive + F_grav

        acc = F_net / M_CRAFT
        vel += acc * dt
        pos += vel * dt

        pos_hist[i] = pos
        vel_hist[i] = vel
        thrust_hist[i] = F_drive
        mode_hist[i] = drive.mode_schedule(t)[0]

    speeds = np.linalg.norm(vel_hist, axis=1)
    time = np.arange(steps) * dt

    # ---------- Plot ----------
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # XY trajectory
    ax = axes[0, 0]
    ax.plot(pos_hist[:, 0], pos_hist[:, 1], 'b-')
    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_title("Craft XY Trajectory (Top View) – Hover, Boost, 90° Turn, Brake")
    ax.grid(True)

    # Altitude vs time
    ax = axes[0, 1]
    ax.plot(time, pos_hist[:, 2], 'g-')
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Altitude Z [m]")
    ax.set_title("Altitude vs Time")
    ax.grid(True)

    # Speed vs time (log)
    ax = axes[1, 0]
    ax.semilogy(time, speeds + 1e-9, 'm-')
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Speed [m/s] (log)")
    ax.set_title("Speed Profile Across Maneuvers")
    ax.grid(True)

    # Thrust components + mode shading
    ax = axes[1, 1]
    ax.plot(time, thrust_hist[:, 0], label="Fx")
    ax.plot(time, thrust_hist[:, 1], label="Fy")
    ax.plot(time, thrust_hist[:, 2], label="Fz")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Drive Thrust [N]")
    ax.set_title("Thrust Vector Components & Modes")
    ax.grid(True)
    ax.legend()

    # Color bands for modes
    for mode_val, color, label in [
        (0, "#e0e0e0", "Hover"),
        (1, "#c8e6ff", "Forward"),
        (2, "#ffe0c8", "Sideways 90°"),
        (3, "#ffc8dc", "Braking"),
    ]:
        mask = mode_hist == mode_val
        if np.any(mask):
            t_start = time[np.where(mask)[0][0]]
            t_end = time[np.where(mask)[0][-1]]
            ax.axvspan(t_start, t_end, color=color, alpha=0.2)

    plt.tight_layout()
    plt.show()

    print(f"Final speed: {speeds[-1]:.3e} m/s")
    print("Final position:", pos_hist[-1])


if __name__ == "__main__":
    run_ufo_maneuver_sim()
