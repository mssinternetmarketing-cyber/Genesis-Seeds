import numpy as np
import matplotlib.pyplot as plt


# ---------- 1. Physical constants ----------
G = 6.67430e-11      # gravitational constant
m_craft = 500.0      # craft mass [kg]


# ---------- 2. Your existing CoherenceSphere ----------
class CoherenceSphere:
    def __init__(self, radius=0.12, mass=1.0, S_total=1e21,
                 alpha=1e-39, repulsive=True, omega=0.0, phase=0.0):
        self.R = radius
        self.M = mass
        self.S_total = S_total
        self.alpha = alpha
        self.repulsive = repulsive
        self.omega = omega      # internal oscillation frequency
        self.phase = phase      # initial phase

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


# ---------- 3. Dynamic 3-sphere drive ----------
class ManeuveringDrive:
    """
    Three spheres arranged in a triangle, orbiting around the craft
    to steer the thrust vector.
    """
    def __init__(self, spheres, base_radius=0.5, vertical_offset=0.5,
                 coupling_strength=3.0):
        self.spheres = spheres
        self.base_radius = base_radius          # radial distance from craft center
        self.vertical_offset = vertical_offset  # distance below craft
        self.coupling_strength = coupling_strength

    def sphere_positions(self, t, yaw_rate=0.5):
        """
        Positions of the three spheres relative to craft center at time t.
        They orbit in a rotating equilateral triangle pattern.
        """
        angles0 = np.array([0, 2*np.pi/3, 4*np.pi/3])
        angles = angles0 + yaw_rate * t
        x = self.base_radius * np.cos(angles)
        y = self.base_radius * np.sin(angles)
        z = -self.vertical_offset * np.ones_like(x)
        return np.column_stack([x, y, z])

    def _resonance_factors(self, t):
        """
        Time‑dependent resonance/throttle law.
        Ramp up, hold, then ramp down; also include phase locking.
        """
        # Simple throttle profile
        if t < 3.0:
            throttle = t / 3.0          # ramp up 0 -> 1
        elif t < 12.0:
            throttle = 1.0             # full power
        elif t < 15.0:
            throttle = 1.0 - (t - 12.0) / 3.0  # ramp down
        else:
            throttle = 0.2             # idle

        # Phase alignment between spheres (near 0 => strong)
        phases = np.array([s.omega * t + s.phase for s in self.spheres])
        phase_spread = np.max(phases) - np.min(phases)
        phase_factor = 1.0 - np.clip(phase_spread / np.pi, 0, 1)

        base = 1.0 + self.coupling_strength * throttle * phase_factor
        # slight asymmetry between spheres
        return base * np.array([0.9, 1.0, 0.95])

    def field_at_point(self, point, craft_pos, t):
        """
        Net acceleration at a spatial point due to all spheres.
        """
        point = np.asarray(point, dtype=float)
        craft_pos = np.asarray(craft_pos, dtype=float)

        positions = craft_pos + self.sphere_positions(t)
        factors = self._resonance_factors(t)

        a_total = np.zeros(3)
        for sphere, pos, f in zip(self.spheres, positions, factors):
            r_vec = point - pos
            r = np.linalg.norm(r_vec)
            if r < 1e-6:
                continue
            a_mag = sphere.accel(r) * f
            a_vec = a_mag * (r_vec / r)
            a_total += a_vec
        return a_total

    def thrust_on_craft(self, craft_pos, m_craft, t):
        """
        Net force on the craft's center of mass.
        """
        a_vec = self.field_at_point(craft_pos, craft_pos, t)
        return m_craft * a_vec


# ---------- 4. Craft dynamics ----------
def run_maneuver_sim():
    # Three identical high‑coupling spheres
    spheres = [
        CoherenceSphere(alpha=5e-39, S_total=5e21, omega=50.0, phase=0.0),
        CoherenceSphere(alpha=5e-39, S_total=5e21, omega=50.0, phase=1.0),
        CoherenceSphere(alpha=5e-39, S_total=5e21, omega=50.0, phase=2.0),
    ]
    drive = ManeuveringDrive(spheres, base_radius=0.5,
                             vertical_offset=0.4, coupling_strength=4.0)

    # Craft initial conditions
    pos = np.array([0.0, 0.0, 0.0])     # start at origin
    vel = np.array([0.0, 0.0, 0.0])

    dt = 0.01
    T = 20.0
    steps = int(T / dt)

    pos_hist = np.zeros((steps, 3))
    vel_hist = np.zeros((steps, 3))
    thrust_hist = np.zeros((steps, 3))

    for i in range(steps):
        t = i * dt

        # Net thrust from spheres
        F = drive.thrust_on_craft(pos, m_craft, t)

        # Craft dynamics (no external gravity for now)
        acc = F / m_craft
        vel += acc * dt
        pos += vel * dt

        pos_hist[i] = pos
        vel_hist[i] = vel
        thrust_hist[i] = F

    speeds = np.linalg.norm(vel_hist, axis=1)
    time = np.arange(steps) * dt

    # ---------- Plot ----------
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 3D‑like XY path
    ax = axes[0, 0]
    ax.plot(pos_hist[:, 0], pos_hist[:, 1], 'b-')
    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_title("Craft Trajectory (Top View)")
    ax.grid(True)

    # Altitude vs time
    ax = axes[0, 1]
    ax.plot(time, pos_hist[:, 2], 'g-')
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Z [m]")
    ax.set_title("Craft Altitude vs Time")
    ax.grid(True)

    # Speed vs time
    ax = axes[1, 0]
    ax.semilogy(time, speeds + 1e-12, 'm-')
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Speed [m/s] (log)")
    ax.set_title("Speed Growth with Steering Drive")
    ax.grid(True)

    # Thrust components
    ax = axes[1, 1]
    ax.plot(time, thrust_hist[:, 0], label="Fx")
    ax.plot(time, thrust_hist[:, 1], label="Fy")
    ax.plot(time, thrust_hist[:, 2], label="Fz")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Thrust [N]")
    ax.set_title("Thrust Vector Components")
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.show()

    print(f"Final speed: {speeds[-1]:.3e} m/s")
    print("Final position:", pos_hist[-1])


if __name__ == "__main__":
    run_maneuver_sim()
