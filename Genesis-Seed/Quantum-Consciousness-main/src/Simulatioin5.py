import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 1. Ship and environment parameters
# ============================================================

G = 6.67430e-11
M_SHIP = 1e9          # 1 billion kg (~large carrier or city-ship)
GRAVITY = np.array([0.0, 0.0, -9.81])  # Earth gravity [m/s^2]


# ============================================================
# 2. Drive module: coherence + gravito-magnetic term
# ============================================================

class DriveModule:
    """
    Represents a cluster of coherence spheres embedded in a
    superconducting EM toroid. It contributes a combined
    info-gravity + gravito-magnetic acceleration field.
    """

    def __init__(self, position, alpha, S_total, axis, omega, phase):
        """
        position : 3D vector [m] relative to ship COM
        alpha    : effective info-gravity coupling
        S_total  : effective entropy / information content
        axis     : unit vector of toroid rotation axis
        omega    : internal oscillation frequency [rad/s]
        phase    : initial phase [rad]
        """
        self.pos = np.asarray(position, dtype=float)
        self.alpha = alpha
        self.S_total = S_total
        axis = np.asarray(axis, dtype=float)
        self.axis = axis / (np.linalg.norm(axis) + 1e-12)
        self.omega = omega
        self.phase = phase

    def resonance_gain(self, t, global_phase):
        """
        Simple phase-lock gain: maximal when module is aligned
        with global lattice phase.
        """
        phi = self.omega * t + self.phase - global_phase
        # Map cos(phi) from [-1,1] to [0,1]
        return 0.5 * (1.0 + np.cos(phi))

    def accel_at(self, point, t, global_phase):
        """
        Acceleration at a 3D point due to this module.
        point        : 3D vector [m] (usually ship COM)
        global_phase : scalar phase of entire lattice
        """
        r_vec = np.asarray(point, float) - self.pos
        r = np.linalg.norm(r_vec) + 1e-9
        r_hat = r_vec / r

        # 1) Info-gravity term: shell around 0.5 m radius
        shell_radius = 0.5
        shell_width = 0.1
        shell_profile = np.exp(-((r - shell_radius) ** 2) /
                               (2.0 * shell_width ** 2))
        a_info_mag = self.alpha * self.S_total * shell_profile
        a_info = a_info_mag * r_hat

        # 2) Gravito-magnetic term: frame-dragging-like swirl
        #    Proportional to axis x r; tuned with small factor.
        a_gm = np.cross(self.axis, r_vec) * 1e-6  # [m/s^2]

        gain = self.resonance_gain(t, global_phase)
        return gain * (a_info + a_gm)


# ============================================================
# 3. Drive lattice over the ship hull
# ============================================================

class ShipDriveLattice:
    """
    Collection of drive modules distributed around the hull.
    Provides net drive acceleration at the ship COM and the
    effective inertial-mass reduction factor mu(t).
    """

    def __init__(self, modules):
        self.modules = modules

    def global_phase(self, t):
        """
        Define a common global phase reference for the lattice.
        For now: base oscillator at 200 rad/s.
        """
        return 200.0 * t

    def drive_accel(self, ship_pos, t):
        """
        Net drive acceleration at the ship COM due to all modules.
        """
        global_phi = self.global_phase(t)
        a = np.zeros(3)
        for m in self.modules:
            a += m.accel_at(ship_pos, t, global_phi)
        return a

    def mu(self, t):
        """
        Inertial mass reduction factor mu(t) between 1.0 and 0.01.
        Depends on phase coherence across modules and on time-
        scheduled 'drive on' window.
        """
        phases = [m.omega * t + m.phase for m in self.modules]
        spread = max(phases) - min(phases)
        # Coherence in [0,1], 1 when phases equal
        coherence = 1.0 - np.clip(spread / np.pi, 0.0, 1.0)

        # Time-based profile: ramp down mu from 1->0.01 over first 10 s,
        # hold, then ramp back up near end.
        if t < 10.0:
            time_factor = 1.0 - 0.99 * (t / 10.0)
        elif t < 25.0:
            time_factor = 0.01
        else:
            time_factor = 0.01 + 0.99 * ((t - 25.0) / 5.0)
            time_factor = min(time_factor, 1.0)

        # Combine: better coherence pushes mu down toward 0.01.
        mu_val = 1.0 - (1.0 - time_factor) * coherence
        # Clamp to [0.01, 1.0]
        return float(np.clip(mu_val, 0.01, 1.0))


# ============================================================
# 4. Maneuver program for the ship
# ============================================================

def maneuver_accel_command(t, vel):
    """
    High-level commanded drive acceleration direction [unit vector]
    and magnitude scale [m/s^2] before mu-effects.
    Segments:
      0–10 s: inertial reduction only (no commanded drive)
      10–15 s: strong upward jump
      15–22 s: high-speed lateral 90° turn
      22–30 s: braking to stop
    """
    # Default: no command
    direction = np.array([0.0, 0.0, 0.0])
    mag = 0.0

    if 10.0 <= t < 15.0:
        # Anti-gravity leap: strong +Z
        direction = np.array([0.0, 0.0, 1.0])
        mag = 50.0  # 50 m/s^2
    elif 15.0 <= t < 22.0:
        # Lateral 90° turn: thrust along +Y while still moving
        direction = np.array([0.0, 1.0, 0.2])
        direction /= np.linalg.norm(direction)
        mag = 40.0
    elif 22.0 <= t <= 30.0:
        # Braking opposite velocity
        speed = np.linalg.norm(vel)
        if speed > 1e-6:
            direction = -vel / speed
            mag = 60.0  # strong braking
        else:
            direction = np.array([0.0, 0.0, 0.0])
            mag = 0.0

    if np.linalg.norm(direction) > 0:
        direction = direction / np.linalg.norm(direction)
    return direction, mag


# ============================================================
# 5. Build a representative ship drive lattice
# ============================================================

def build_ship_lattice():
    modules = []
    # Ring of 12 modules around hull radius ~40 m, z=0
    radius = 40.0
    for k in range(12):
        theta = 2 * np.pi * k / 12
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        z = 0.0
        pos = [x, y, z]

        # Axes: radial + vertical mix
        axis = np.array([np.cos(theta), np.sin(theta), 0.3])

        # Effective parameters (tuned)
        alpha = 1e-40
        S_total = 1e24
        omega = 500.0 + 10.0 * np.sin(theta)  # slightly detuned
        phase = theta

        modules.append(DriveModule(pos, alpha, S_total, axis, omega, phase))

    # Add central spine modules (top/bottom)
    spine_positions = [
        [0.0, 0.0, 30.0],
        [0.0, 0.0, -30.0],
    ]
    for i, z in enumerate([30.0, -30.0]):
        pos = [0.0, 0.0, z]
        axis = [0.0, 0.0, 1.0 if z > 0 else -1.0]
        alpha = 5e-41
        S_total = 5e23
        omega = 480.0 + 15.0 * i
        phase = 0.5 * i
        modules.append(DriveModule(pos, alpha, S_total, axis, omega, phase))

    return ShipDriveLattice(modules)


# ============================================================
# 6. Main ship-scale simulation
# ============================================================

def run_ship_scale_sim():
    lattice = build_ship_lattice()

    # Initial state: hovering 2 km above origin, moving slowly forward
    pos = np.array([0.0, -500.0, 2000.0])  # x,y,z [m]
    vel = np.array([50.0, 0.0, 0.0])       # 50 m/s along +x

    dt = 0.02
    T = 30.0
    steps = int(T / dt)

    pos_hist = np.zeros((steps, 3))
    vel_hist = np.zeros((steps, 3))
    acc_hist = np.zeros((steps, 3))
    mu_hist = np.zeros(steps)

    for i in range(steps):
        t = i * dt

        mu_t = lattice.mu(t)
        a_drive_lattice = lattice.drive_accel(pos, t)

        # High-level commanded acceleration
        cmd_dir, cmd_mag = maneuver_accel_command(t, vel)
        a_cmd = cmd_dir * cmd_mag

        # Total drive acceleration is combination of lattice field and command
        a_drive = a_drive_lattice + a_cmd

        # Net acceleration including gravity and inertial-mass reduction:
        # a_total = (M_ship * g)/M_eff + a_drive,
        # where M_eff = mu_t * M_SHIP
        M_eff = mu_t * M_SHIP
        a_grav = (M_SHIP * GRAVITY) / M_eff
        a_total = a_grav + a_drive

        vel += a_total * dt
        pos += vel * dt

        pos_hist[i] = pos
        vel_hist[i] = vel
        acc_hist[i] = a_total
        mu_hist[i] = mu_t

    time = np.arange(steps) * dt
    speeds = np.linalg.norm(vel_hist, axis=1)
    felt_g = np.linalg.norm(acc_hist - GRAVITY, axis=1) / 9.81

    # ========================================================
    # 7. Plots
    # ========================================================

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # XY trajectory (top view)
    ax = axes[0, 0]
    ax.plot(pos_hist[:, 0], pos_hist[:, 1], 'b-')
    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_title("Ship XY Trajectory – Jump, 90° Turn, Brake")
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
    ax.semilogy(time, speeds + 1e-6, 'm-')
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Speed [m/s] (log)")
    ax.set_title("Speed Profile – Large Ship")
    ax.grid(True)

    # mu(t) and felt g-load
    ax = axes[1, 1]
    ax.plot(time, mu_hist, 'k-', label="mu(t) (inertial factor)")
    ax2 = ax.twinx()
    ax2.plot(time, felt_g, 'r--', label="felt g-load")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("mu(t)")
    ax2.set_ylabel("felt g [g]")
    ax.set_title("Inertial Reduction & Felt g-load")

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    ax.grid(True)

    plt.tight_layout()
    plt.show()

    print(f"Final position: {pos_hist[-1]}")
    print(f"Final speed: {speeds[-1]:.3e} m/s")
    print(f"Min mu(t): {mu_hist.min():.3f}")
    print(f"Max felt g: {felt_g.max():.2f} g")


if __name__ == "__main__":
    run_ship_scale_sim()
