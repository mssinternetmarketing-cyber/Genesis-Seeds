import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy
from collections import defaultdict

# ============================================================
# COSMIC HIDE-AND-SEEK SIMULATION
# ============================================================
# Aliens engineer the universe and hide infrastructure.
# Humans deploy detection experiments and update beliefs.
# Winner: Humans if they localize alien infrastructure.
#         Aliens if humans exhaust resources before detection.
# ============================================================


class CosmicInfrastructure:
    """
    Advanced alien civilization's hidden infrastructure.
    Maintains cosmic voids, modulates vacuum fields, hides evidence.
    """

    def __init__(self, num_nodes=8, concealment_level=0.9):
        """
        num_nodes: number of infrastructure nodes (hidden in voids)
        concealment_level: 0..1, how well they can hide signatures
        """
        self.num_nodes = num_nodes
        self.concealment_level = concealment_level

        # Each node has a position in space (Mpc scale)
        self.node_positions = np.random.uniform(0, 1000, (num_nodes, 3))

        # Each node has an activity level (0..1)
        # Higher = more detectable but more functional
        self.activity_levels = np.random.uniform(0.1, 0.5, num_nodes)

        # Masking strategy: add noise to observations proportional to concealment_level
        self.mask_noise_scale = concealment_level * 2.0

        # Infrastructure type (affects what anomalies they produce)
        # 0: dark energy controller, 1: void maintenance, 2: information router
        self.node_types = np.random.choice([0, 1, 2], num_nodes)

    def get_true_signature(self):
        """The true anomaly pattern if fully exposed."""
        sig = np.zeros(3)  # [dark_energy_anomaly, void_asymmetry, info_leakage]
        for i, ntype in enumerate(self.node_types):
            activity = self.activity_levels[i]
            if ntype == 0:
                sig[0] += activity * 0.3  # dark energy anomaly
            elif ntype == 1:
                sig[1] += activity * 0.4  # void boundary structure
            else:
                sig[2] += activity * 0.2  # info-theoretic leakage
        return sig

    def masked_observation(self, observer_tech_level):
        """
        What humans observe after alien masking.
        observer_tech_level: 0..1, human capability to pierce concealment
        """
        true_sig = self.get_true_signature()
        # Add masking noise (aliens try to hide)
        noise = np.random.normal(
            0, self.mask_noise_scale * (1.0 - observer_tech_level), 3
        )
        return true_sig + noise

    def adjust_concealment(self, detected_intensity):
        """
        Aliens respond: if humans are getting close, tighten concealment.
        But tightening costs them operational capability.
        """
        if detected_intensity > 0.5:
            self.concealment_level = min(1.0, self.concealment_level + 0.1)
            # Reduce activity slightly
            self.activity_levels *= 0.95
            return "Tightened"
        return "Stable"


class HumanCivilization:
    """
    Emerging human civilization deploying detection strategy.
    Uses Bayesian updating, experiments, and theory development.
    """

    def __init__(self, initial_tech_level=0.1):
        """
        tech_level: 0..1, capability to measure subtle anomalies
        """
        self.tech_level = initial_tech_level
        self.observations = []
        self.hypotheses = {
            "standard_GR": 0.7,  # Belief in standard physics
            "dark_matter_only": 0.15,  # Conventional explanations
            "alien_infrastructure": 0.15,  # Belief in hidden civilization
        }
        self.experiments_run = 0
        self.budget = 1000  # Resource budget for experiments
        self.detection_confidence = 0.0

    def run_experiment(self, exp_type, aliens, cost=10):
        """
        Run an experiment to gather data.
        exp_type: 'cmb_anomaly', 'void_structure', 'gravitational_wave',
                  'vacuum_coherence', 'dark_energy_precision'
        """
        if self.budget < cost:
            return None

        self.budget -= cost
        self.experiments_run += 1

        # Observation depends on experiment type and alien masking
        obs = aliens.masked_observation(self.tech_level)

        # Different experiments are sensitive to different anomalies
        sensitivity = {
            "cmb_anomaly": [0.3, 0.4, 0.2],  # More sensitive to void structure
            "void_structure": [0.2, 0.9, 0.1],  # Highly sensitive to void anomalies
            "gravitational_wave": [0.5, 0.3, 0.3],
            "vacuum_coherence": [0.2, 0.2, 0.7],  # Sensitive to info leakage
            "dark_energy_precision": [0.8, 0.3, 0.1],
        }

        sens = np.array(sensitivity.get(exp_type, [0.33, 0.33, 0.33]))
        measured = obs * sens
        
        self.observations.append((exp_type, measured))
        return measured

    def compute_likelihood(self, obs, hypothesis):
        """
        Likelihood of observation given hypothesis.
        """
        if hypothesis == "alien_infrastructure":
            # If aliens exist, we should see structured anomalies
            # Measure how "structured" the observation is (low entropy = structured)
            epsilon = 1e-10
            p = np.abs(obs) + epsilon
            p = p / p.sum()
            ent = entropy(p)
            return 1.0 / (1.0 + ent)  # Lower entropy = higher likelihood
        else:
            # Standard physics: should be random noise
            noise_level = np.linalg.norm(obs)
            return 1.0 / (1.0 + noise_level)

    def update_beliefs(self):
        """
        Bayesian update of hypotheses based on observations.
        """
        if not self.observations:
            return

        # Simple likelihood ratio test
        likelihoods = {}
        for hyp in self.hypotheses.keys():
            L = 1.0
            for exp_type, obs in self.observations[-5:]:  # Recent observations
                L *= self.compute_likelihood(obs, hyp)
            likelihoods[hyp] = L

        # Normalize to posterior
        total = sum(likelihoods.values())
        if total > 0:
            for hyp in self.hypotheses.keys():
                self.hypotheses[hyp] = likelihoods[hyp] / total

        self.detection_confidence = self.hypotheses.get("alien_infrastructure", 0.0)

    def suggest_next_experiment(self, aliens):
        """
        Adaptive: suggest the experiment most likely to distinguish hypotheses.
        """
        experiments = [
            "cmb_anomaly",
            "void_structure",
            "gravitational_wave",
            "vacuum_coherence",
            "dark_energy_precision",
        ]

        # Fisher information: which experiment would most change our beliefs?
        best_exp = None
        best_info_gain = 0.0

        for exp in experiments:
            # Simulate what we'd learn
            hyp_predictions = {}
            for hyp in self.hypotheses.keys():
                # Rough: alien hypothesis predicts structured anomalies
                if hyp == "alien_infrastructure":
                    pred = aliens.get_true_signature() * 0.5
                else:
                    pred = np.random.normal(0, 0.2, 3)
                hyp_predictions[hyp] = pred

            # Information gain: divergence between hypotheses
            info_gain = 0.0
            for hyp1 in self.hypotheses.keys():
                for hyp2 in self.hypotheses.keys():
                    if hyp1 != hyp2:
                        d = np.linalg.norm(
                            hyp_predictions[hyp1] - hyp_predictions[hyp2]
                        )
                        info_gain += d * self.hypotheses[hyp1]

            if info_gain > best_info_gain:
                best_info_gain = info_gain
                best_exp = exp

        return best_exp if best_exp else experiments[0]

    def advance_tech(self, gain=0.01):
        """Humans advance technology over time."""
        self.tech_level = min(1.0, self.tech_level + gain)


class UniverseGame:
    """
    Orchestrates the game: aliens hide, humans search.
    """

    def __init__(self, num_rounds=50):
        self.aliens = CosmicInfrastructure(num_nodes=6, concealment_level=0.85)
        self.humans = HumanCivilization(initial_tech_level=0.05)
        self.num_rounds = num_rounds
        self.history = defaultdict(list)

    def run(self):
        """
        Main game loop.
        """
        for round_num in range(self.num_rounds):
            # Humans run an adaptive experiment
            if self.humans.budget > 0:
                exp = self.humans.suggest_next_experiment(self.aliens)
                obs = self.humans.run_experiment(exp, self.aliens, cost=5)

                # Humans update beliefs
                self.humans.update_beliefs()

                # Aliens detect intensity of observation
                if obs is not None:
                    detected_intensity = np.linalg.norm(obs)
                    response = self.aliens.adjust_concealment(detected_intensity)
                else:
                    detected_intensity = 0.0
                    response = "Idle"

                # Humans advance tech slightly
                self.humans.advance_tech(gain=0.005)

                # Log
                self.history["round"].append(round_num)
                self.history["tech_level"].append(self.humans.tech_level)
                self.history["detection_confidence"].append(
                    self.humans.detection_confidence
                )
                self.history["concealment"].append(self.aliens.concealment_level)
                self.history["alien_response"].append(response)
                self.history["detected_intensity"].append(detected_intensity)
                self.history["experiments_run"].append(self.humans.experiments_run)

            else:
                break

    def plot_results(self):
        """
        Visualize the game: arms race between detection and concealment.
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        rounds = self.history["round"]

        # Detection confidence vs concealment (adversarial)
        ax = axes[0, 0]
        ax.plot(
            rounds,
            self.history["detection_confidence"],
            "g-",
            label="Human detection confidence",
            linewidth=2,
        )
        ax.plot(
            rounds,
            self.history["concealment"],
            "r-",
            label="Alien concealment level",
            linewidth=2,
        )
        ax.set_xlabel("Round")
        ax.set_ylabel("Level (0..1)")
        ax.set_title("Detection vs Concealment – The Arms Race")
        ax.legend()
        ax.grid(True)

        # Human tech advancement
        ax = axes[0, 1]
        ax.plot(rounds, self.history["tech_level"], "b-", linewidth=2)
        ax.set_xlabel("Round")
        ax.set_ylabel("Human Tech Level")
        ax.set_title("Human Technological Progress")
        ax.grid(True)

        # Alien response and detected intensity
        ax = axes[1, 0]
        ax.plot(
            rounds,
            self.history["detected_intensity"],
            "m-",
            label="Detected intensity",
            linewidth=2,
        )
        ax.set_xlabel("Round")
        ax.set_ylabel("Anomaly Strength (log)")
        ax.set_yscale("log")
        ax.set_title("Anomaly Detection Over Time")
        ax.grid(True)

        # Experiments run and budget depletion
        ax = axes[1, 1]
        ax.plot(rounds, self.history["experiments_run"], "c-", linewidth=2)
        ax.set_xlabel("Round")
        ax.set_ylabel("Cumulative Experiments")
        ax.set_title("Scientific Effort (Experiments Deployed)")
        ax.grid(True)

        plt.tight_layout()
        plt.show()

        # Summary
        final_confidence = self.history["detection_confidence"][-1]
        final_concealment = self.history["concealment"][-1]
        print(f"\n{'='*60}")
        print(f"GAME RESULT")
        print(f"{'='*60}")
        print(f"Final human detection confidence: {final_confidence:.2%}")
        print(f"Final alien concealment level: {final_concealment:.2%}")
        print(f"Experiments deployed: {self.humans.experiments_run}")
        print(f"Remaining budget: {self.humans.budget}")
        print(f"Human tech level: {self.humans.tech_level:.2%}")

        if final_confidence > 0.7:
            print(f"\n✓ HUMANS WIN: Alien civilization detected!")
        elif final_confidence > 0.4:
            print(f"\n? STALEMATE: Strong suspicions, but no conclusive proof.")
        else:
            print(f"\n✗ ALIENS WIN: Remains hidden. Humans conclude it's all standard physics.")


# ============================================================
# RUN THE COSMIC HIDE-AND-SEEK GAME
# ============================================================

if __name__ == "__main__":
    print("COSMIC HIDE-AND-SEEK: Advanced Aliens vs Emerging Humans")
    print("="*60)
    print("Aliens engineer voids, mask signatures, adjust concealment.")
    print("Humans deploy Bayesian inference, adaptive experiments, tech advancement.")
    print("="*60 + "\n")

    game = UniverseGame(num_rounds=80)
    game.run()
    game.plot_results()

    # Print belief evolution snapshot
    print(f"\n{'='*60}")
    print("Human Beliefs (Final):")
    for hyp, belief in game.humans.hypotheses.items():
        print(f"  {hyp}: {belief:.2%}")
    print(f"{'='*60}")
