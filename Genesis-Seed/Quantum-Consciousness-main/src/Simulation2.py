import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint


# [Keep all previous code from your original simulation...]
G = 6.67430e-11
c = 2.99792458e8
m_hand = 0.5


class CoherenceSphere:
    def __init__(self, radius=0.12, mass=1.0, S_total=1e20, alpha=1e-40, repulsive=True):
        self.R = radius
        self.M = mass
        self.S_total = S_total
        self.alpha = alpha
        self.repulsive = repulsive
        self.phase = 0.0  # Quantum phase [radians]
        self.omega = 0.0  # Oscillation frequency [rad/s]

    def info_density(self):
        V = 4/3 * np.pi * self.R**3
        return self.S_total / V

    def accel(self, r):
        r = np.asarray(r)
        a_mass = np.zeros_like(r, dtype=float)
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
        shell_profile = np.exp(-((r - self.R)**2) / (2 * w**2))
        sign = +1.0 if self.repulsive else -1.0
        a_info = sign * self.alpha * S_rho * shell_profile

        return a_mass + a_info

    def force_on_mass(self, r, m_test=m_hand):
        return m_test * self.accel(r)


# ============================================================
# 10. SPHERE-SPHERE COUPLING & RESONANCE
# ============================================================

class CoupledCoherenceArray:
    """
    Three spheres that can resonate together and amplify each other's fields.
    """
    def __init__(self, spheres, positions, coupling_strength=1.0):
        """
        spheres          : list of 3 CoherenceSphere objects
        positions        : Nx3 array of sphere center positions [m]
        coupling_strength: how strongly spheres entangle (0-1 typical)
        """
        self.spheres = spheres
        self.positions = np.asarray(positions)
        self.coupling_strength = coupling_strength
        self.resonance_factor = np.ones(len(spheres))  # Amplification per sphere
        self.phase_diff = np.zeros(len(spheres) - 1)   # Phase differences
        
    def inter_sphere_distance(self, i, j):
        """Distance between sphere centers i and j."""
        return np.linalg.norm(self.positions[i] - self.positions[j])
    
    def update_resonance(self, phase_mismatch_threshold=0.1):
        """
        Check if spheres are in resonance (phases aligned).
        If they are, amplify the coupling strength.
        """
        n_spheres = len(self.spheres)
        
        # Compute pairwise distances
        distances = np.array([
            self.inter_sphere_distance(i, j)
            for i in range(n_spheres)
            for j in range(i+1, n_spheres)
        ])
        
        # If spheres are close enough, they can resonate
        mean_distance = np.mean(distances)
        resonance_active = mean_distance < 0.5  # Within ~50 cm
        
        if resonance_active:
            # Phase alignment bonus (simplified: assume phases lock)
            phase_alignment = 1.0 - np.clip(np.abs(np.mean(self.phase_diff)) / np.pi, 0, 1)
            
            # Resonance amplifies each sphere's effective alpha (coupling to info)
            for i in range(n_spheres):
                # Boost depends on proximity to neighbors
                neighbor_proximity = np.sum([
                    np.exp(-self.inter_sphere_distance(i, j) / 0.2)
                    for j in range(n_spheres) if j != i
                ])
                self.resonance_factor[i] = 1.0 + self.coupling_strength * neighbor_proximity * phase_alignment
        else:
            self.resonance_factor = np.ones(n_spheres)

    def field_at_point(self, point):
        """
        Total acceleration [m/s^2] at a 3D point.
        Includes amplified coupling from resonance.
        """
        point = np.asarray(point)
        a_total = np.zeros(3)
        
        self.update_resonance()  # Update resonance factors
        
        for i, (sphere, pos) in enumerate(zip(self.spheres, self.positions)):
            r_vec = point - pos
            r = np.linalg.norm(r_vec)
            
            if r < 1e-6:
                continue
            
            # Base acceleration
            a_mag = sphere.accel(r)
            
            # Apply resonance amplification
            a_mag *= self.resonance_factor[i]
            
            # Convert to vector
            r_unit = r_vec / r
            a_vec = a_mag * r_unit
            a_total += a_vec
        
        return a_total

    def force_on_test_mass(self, point, m_test=m_hand):
        """Force [N] on test mass at a point."""
        return m_test * self.field_at_point(point)


# ============================================================
# 11. PROPULSIVE THRUST SIMULATION
# ============================================================

class ThrustModel:
    """
    Model how the three-sphere array can generate thrust.
    Assumes the craft has mass M_craft and the field can push it.
    """
    def __init__(self, coupled_array, M_craft=1000.0, craft_position=None):
        """
        coupled_array   : CoupledCoherenceArray
        M_craft         : craft mass [kg]
        craft_position  : craft CoM position [m]
        """
        self.array = coupled_array
        self.M_craft = M_craft
        self.position = craft_position if craft_position is not None else np.array([0, 0, -1.0])
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.acceleration = np.array([0.0, 0.0, 0.0])

    def compute_thrust(self):
        """
        Compute net force on craft from the three-sphere field.
        Simplified: measure field at craft location, project into motion direction.
        """
        F_vec = self.array.force_on_test_mass(self.position, m_test=self.M_craft)
        self.acceleration = F_vec / self.M_craft
        return F_vec

    def step(self, dt=0.01):
        """
        Advance craft position and velocity by one time step.
        """
        F = self.compute_thrust()
        self.acceleration = F / self.M_craft
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        return self.position, self.velocity


# ============================================================
# 12. VISUALIZATION: Resonant 3-Sphere Craft
# ============================================================

def simulate_resonant_craft():
    """
    Simulate three resonant spheres driving a craft to high speeds.
    """
    # Three spheres in a line configuration
    R = 0.12
    M = 1.0
    
    # Higher coupling → stronger resonance effect
    spheres = [
        CoherenceSphere(radius=R, mass=M, S_total=1e21, alpha=1e-39, repulsive=True),
        CoherenceSphere(radius=R, mass=M, S_total=1e21, alpha=1e-39, repulsive=True),
        CoherenceSphere(radius=R, mass=M, S_total=1e21, alpha=1e-39, repulsive=True),
    ]
    
    # Positions: spheres pushed close together (resonance zone: < 0.5 m apart)
    positions = np.array([
        [-0.15, 0.0, 0.0],
        [ 0.0,  0.0, 0.0],
        [ 0.15, 0.0, 0.0],
    ])
    
    # Create coupled array with resonance
    coupled = CoupledCoherenceArray(spheres, positions, coupling_strength=2.0)
    
    # Craft positioned below the sphere array
    craft = ThrustModel(coupled, M_craft=500.0, craft_position=np.array([0, 0, -0.5]))
    
    # Simulation parameters
    dt = 0.01
    n_steps = 2000
    
    # Storage for history
    positions_hist = np.zeros((n_steps, 3))
    velocities_hist = np.zeros((n_steps, 3))
    forces_hist = np.zeros((n_steps, 3))
    resonance_hist = np.zeros((n_steps, 3))
    
    # Run simulation
    for step in range(n_steps):
        pos, vel = craft.step(dt)
        F = craft.compute_thrust()
        
        positions_hist[step] = pos
        velocities_hist[step] = vel
        forces_hist[step] = F
        resonance_hist[step] = coupled.resonance_factor
    
    # Compute speeds
    speeds = np.linalg.norm(velocities_hist, axis=1)
    
    # Plot results
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Position trajectory
    ax = axes[0, 0]
    ax.plot(positions_hist[:, 0], positions_hist[:, 1], 'b-', alpha=0.5, label='XY path')
    ax.scatter(0, 0, c='red', s=100, label='Sphere array', zorder=5)
    ax.set_xlabel('X [m]')
    ax.set_ylabel('Y [m]')
    ax.set_title('Craft Trajectory (Top View)')
    ax.legend()
    ax.grid()
    
    # Altitude vs time
    ax = axes[0, 1]
    time = np.arange(n_steps) * dt
    ax.plot(time, positions_hist[:, 2], 'g-', linewidth=2)
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Z-altitude [m]')
    ax.set_title('Craft Height vs Time')
    ax.grid()
    
    # Speed vs time
    ax = axes[1, 0]
    ax.semilogy(time, speeds + 1e-10, 'purple', linewidth=2)
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Speed [m/s] (log scale)')
    ax.set_title('Craft Speed Over Time')
    ax.grid()
    
    # Resonance factors
    ax = axes[1, 1]
    ax.plot(time, resonance_hist, linewidth=1.5)
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Resonance Amplification Factor')
    ax.set_title('Sphere Resonance Coupling')
    ax.legend(['Sphere 0', 'Sphere 1', 'Sphere 2'])
    ax.grid()
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    final_speed = speeds[-1]
    max_speed = np.max(speeds)
    print(f"Final craft speed: {final_speed:.3e} m/s")
    print(f"Max speed achieved: {max_speed:.3e} m/s")
    print(f"Craft displacement: {np.linalg.norm(positions_hist[-1] - positions_hist[0]):.3f} m")
    print(f"Mean resonance factor: {np.mean(resonance_hist):.3f}")


if __name__ == "__main__":
    simulate_resonant_craft()
