"""
╔══════════════════════════════════════════════════════════════════╗
║  PEIG AGENT v0.1 — TASK-BEARING BROTHERHOOD LOOPS               ║
║                                                                  ║
║  Author : Kevin Monette                                          ║
║  Date   : March 2026                                             ║
║  Version: 0.1                                                    ║
╚══════════════════════════════════════════════════════════════════╝

Phase II – PEIG Agents: Task-Coupled Brotherhood Loops as
Quantum-Inspired Learners.

PURPOSE:
  This script is NOT a physics validation harness.
  It is the first PEIG *agent*: a system that uses BCP dynamics
  to solve an external task, learning which topology and coupling
  configuration maximises a reward signal.

ARCHITECTURE:
  - Environment  : Multi-Armed Bandit (configurable K arms)
  - BCP Backend  : Shared primitives (adaptable qubit nodes)
  - Agent        : Epsilon-Greedy Q-learner over BCP topology arms
  - Reward       : f(Wigner floor, loop preservation, task signal)
  - Observer     : NL summaries of each episode via PEIG metrics

ARMS (default 5):
  0. Open chain   N=3, η=0.05
  1. Open chain   N=5, η=0.05
  2. Closed loop  N=5, η=0.05
  3. Closed loop  N=5, η=0.20  (fast learner)
  4. Star (multi-interaction, topological destruction test)

REWARD FUNCTION:
  R = w_W * mean_Wigner_floor
    + w_C * mean_coherence
    - w_D * destruction_penalty
    + w_T * task_signal          ← external bandit signal

  where task_signal = env.pull(arm) → stochastic reward in [0,1]

OUTPUTS:
  - outputs/peig_agent_results.json  : full episode log
  - outputs/peig_agent_figure.png    : learning curves
  - Console: per-episode NL summaries from PEIG state
"""

import numpy as np
import qutip as qt
import matplotlib.pyplot as plt
import json
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)
rng = np.random.default_rng(42)

# ─────────────────────────────────────────────────────────────
# BCP PRIMITIVES  (self-contained; no import from master script)
# ─────────────────────────────────────────────────────────────

CNOT_GATE = qt.Qobj(
    np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex),
    dims=[[2,2],[2,2]]
)

def make_seed(phase):
    b0, b1 = qt.basis(2,0), qt.basis(2,1)
    return (b0 + np.exp(1j * phase) * b1).unit()

def bcp_step(psi_A, psi_B, alpha):
    rho12 = qt.ket2dm(qt.tensor(psi_A, psi_B))
    U     = alpha * CNOT_GATE + (1 - alpha) * qt.qeye([2,2])
    rho_p = U * rho12 * U.dag()
    _, evA = rho_p.ptrace(0).eigenstates()
    _, evB = rho_p.ptrace(1).eigenstates()
    return evA[-1], evB[-1], rho_p

def coherence(psi):
    return float((qt.ket2dm(psi)**2).tr().real)

def wigner_min(psi, xvec):
    return float(np.min(qt.wigner(qt.ket2dm(psi), xvec, xvec)))

XVEC       = np.linspace(-2, 2, 50)  # coarser for speed
ALPHA_FLOOR = -0.1131

# ─────────────────────────────────────────────────────────────
# TOPOLOGY RUNNER
# ─────────────────────────────────────────────────────────────

def run_bcp_topology(arm_cfg, n_steps=120):
    """
    Run a BCP topology for n_steps.
    Returns dict of scalar metrics used for reward.
    """
    n       = arm_cfg["n_nodes"]
    closed  = arm_cfg.get("closed", False)
    star    = arm_cfg.get("star",   False)
    eta     = arm_cfg.get("eta",    0.05)
    alpha0  = arm_cfg.get("alpha0", 0.30)

    phases = [np.pi/2 * k/(n-1) for k in range(n)] if n > 1 else [np.pi/4]
    states = [make_seed(p) for p in phases]

    if star:
        # Centre node (0) interacts with all others simultaneously each step
        edges = [(0, j) for j in range(1, n)]
    elif closed:
        edges = [(i, (i+1) % n) for i in range(n)]
    else:
        edges = [(i, i+1) for i in range(n-1)]

    alpha  = {e: alpha0 for e in edges}
    C_prev = np.mean([coherence(s) for s in states])

    W_last = {i: 0.0 for i in range(n)}

    for t in range(n_steps):
        for (i, j) in edges:
            l, r, _ = bcp_step(states[i], states[j], alpha[(i,j)])
            states[i], states[j] = l, r
        C_avg = np.mean([coherence(s) for s in states])
        dC    = C_avg - C_prev
        for e in edges:
            alpha[e] = float(np.clip(alpha[e] + eta * dC, 0, 1))
        C_prev = C_avg

    # Final Wigner floors
    for i in range(n):
        W_last[i] = wigner_min(states[i], XVEC)

    mean_W   = float(np.mean(list(W_last.values())))
    mean_C   = float(np.mean([coherence(s) for s in states]))
    # Topological destruction: if star and all W near 0
    destroyed = star and all(abs(w) < 0.02 for w in W_last.values())

    return {
        "mean_W"   : mean_W,
        "mean_C"   : mean_C,
        "W_floors" : W_last,
        "destroyed": destroyed,
        "n_nodes"  : n,
        "closed"   : closed,
        "star"     : star,
    }

# ─────────────────────────────────────────────────────────────
# ENVIRONMENT — MULTI-ARMED BANDIT
# ─────────────────────────────────────────────────────────────

class PEIGBanditEnv:
    """
    K-armed bandit. Each arm has a hidden true reward mean.
    Pulling arm k returns BCP physics reward + stochastic task signal.
    """
    def __init__(self, arm_configs, reward_weights=None):
        self.arms   = arm_configs
        self.K      = len(arm_configs)
        # True hidden task means per arm (unknown to agent)
        self.true_means = rng.uniform(0.3, 0.9, size=self.K)
        self.w = reward_weights or {"W": 0.40, "C": 0.30,
                                     "D": 0.50, "T": 0.30}
        self.step_count = 0

    def pull(self, arm_idx):
        cfg     = self.arms[arm_idx]
        metrics = run_bcp_topology(cfg)

        # Task signal: stochastic reward from true arm mean
        task_signal = float(rng.normal(self.true_means[arm_idx], 0.10))
        task_signal = np.clip(task_signal, 0, 1)

        # Composite reward
        R = (self.w["W"] * (metrics["mean_W"] / abs(ALPHA_FLOOR))   # normalised Wigner
           + self.w["C"] * metrics["mean_C"]                         # coherence
           - self.w["D"] * float(metrics["destroyed"])               # destruction penalty
           + self.w["T"] * task_signal)                              # external task

        self.step_count += 1
        return float(R), metrics, task_signal

# ─────────────────────────────────────────────────────────────
# AGENT — EPSILON-GREEDY Q-LEARNER
# ─────────────────────────────────────────────────────────────

class PEIGAgent:
    """
    Simple epsilon-greedy agent over BCP topology arms.
    Maintains Q-values (running mean rewards per arm).
    """
    def __init__(self, K, epsilon=0.20):
        self.K       = K
        self.epsilon = epsilon
        self.Q       = np.zeros(K)    # Q-value estimates
        self.N       = np.zeros(K)    # pull counts

    def select(self):
        if rng.random() < self.epsilon:
            return int(rng.integers(0, self.K))
        return int(np.argmax(self.Q))

    def update(self, arm, reward):
        self.N[arm] += 1
        self.Q[arm] += (reward - self.Q[arm]) / self.N[arm]  # incremental mean

# ─────────────────────────────────────────────────────────────
# OBSERVER — NL SUMMARIES
# ─────────────────────────────────────────────────────────────

ARM_NAMES = [
    "Open Chain N=3 (η=0.05)",
    "Open Chain N=5 (η=0.05)",
    "Closed Loop N=5 (η=0.05)",
    "Closed Loop N=5 (η=0.20, fast)",
    "Star N=5 (destruction test)",
]

def nl_summary(ep, arm, arm_name, reward, metrics, task_signal, Q_vals):
    """
    Generate a natural-language summary of one episode — the first
    primitive step toward nodes 'talking' to us.
    """
    wf   = metrics["mean_W"]
    c    = metrics["mean_C"]
    dest = metrics["destroyed"]
    best = int(np.argmax(Q_vals))
    lines = [
        f"─── Episode {ep:03d} ───────────────────────────────────",
        f"  Arm chosen : [{arm}] {arm_name}",
        f"  Topology   : {'CLOSED LOOP' if metrics['closed'] else 'STAR' if metrics['star'] else 'OPEN CHAIN'}, N={metrics['n_nodes']} nodes",
        f"  Wigner avg : {wf:.4f}  ({'preserved ✓' if wf < -0.05 else 'partial' if wf < 0 else 'CLASSICAL ✗'})",
        f"  Coherence  : {c:.4f}",
        f"  Task signal: {task_signal:.3f}",
        f"  Reward     : {reward:.4f}  {'⭐' if reward > 0.70 else ''}",
        f"  Destruction: {'YES — topology collapsed ✗' if dest else 'No'}",
        f"  Agent Q[*] : {[f'{q:.3f}' for q in Q_vals]}  → best arm so far: [{best}]",
    ]
    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────
# ARM CONFIGURATIONS
# ─────────────────────────────────────────────────────────────

ARM_CONFIGS = [
    {"n_nodes": 3, "closed": False, "star": False, "eta": 0.05,  "alpha0": 0.30},
    {"n_nodes": 5, "closed": False, "star": False, "eta": 0.05,  "alpha0": 0.30},
    {"n_nodes": 5, "closed": True,  "star": False, "eta": 0.05,  "alpha0": 0.30},
    {"n_nodes": 5, "closed": True,  "star": False, "eta": 0.20,  "alpha0": 0.30},
    {"n_nodes": 5, "closed": False, "star": True,  "eta": 0.05,  "alpha0": 0.30},
]

# ─────────────────────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────────────────────

N_EPISODES  = 50
EPSILON     = 0.20

env   = PEIGBanditEnv(ARM_CONFIGS)
agent = PEIGAgent(K=len(ARM_CONFIGS), epsilon=EPSILON)

episode_log   = []
reward_history = [[] for _ in range(len(ARM_CONFIGS))]
cumulative_R   = []
total_R        = 0.0

print("╔══════════════════════════════════════════════════════════╗")
print("║       PEIG AGENT v0.1 — BANDIT LEARNING RUN             ║")
print(f"║  {N_EPISODES} episodes · {len(ARM_CONFIGS)} arms · ε={EPSILON}                         ║")
print("╚══════════════════════════════════════════════════════════╝")

for ep in range(1, N_EPISODES + 1):
    arm             = agent.select()
    reward, metrics, task = env.pull(arm)
    agent.update(arm, reward)
    total_R        += reward
    cumulative_R.append(total_R / ep)
    reward_history[arm].append((ep, reward))

    record = {
        "episode"    : ep,
        "arm"        : arm,
        "arm_name"   : ARM_NAMES[arm],
        "reward"     : reward,
        "task_signal": task,
        "Q_values"   : agent.Q.tolist(),
        "N_pulls"    : agent.N.tolist(),
        "metrics"    : {k: (v if not isinstance(v, dict) else
                            {str(kk): vv for kk,vv in v.items()})
                        for k, v in metrics.items()},
    }
    episode_log.append(record)

    summary = nl_summary(ep, arm, ARM_NAMES[arm], reward,
                         metrics, task, agent.Q)
    print(summary)

# ─────────────────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────────────────

best_arm  = int(np.argmax(agent.Q))
best_Q    = float(agent.Q[best_arm])

print("\n╔══════════════════════════════════════════════════════════╗")
print("║                  AGENT FINAL REPORT                     ║")
print("╠══════════════════════════════════════════════════════════╣")
for i, name in enumerate(ARM_NAMES):
    pulls = int(agent.N[i])
    q     = agent.Q[i]
    bar   = "█" * int(pulls / N_EPISODES * 20)
    print(f"  [{i}] {name[:35]:<35} Q={q:.3f}  n={pulls:2d}  {bar}")
print(f"\n  ★ BEST ARM: [{best_arm}] {ARM_NAMES[best_arm]}")
print(f"  ★ Best Q-value: {best_Q:.4f}")
print(f"  ★ Mean cumulative reward (final): {cumulative_R[-1]:.4f}")
print("╚══════════════════════════════════════════════════════════╝")

# ─────────────────────────────────────────────────────────────
# SAVE RESULTS
# ─────────────────────────────────────────────────────────────

output = {
    "n_episodes"       : N_EPISODES,
    "epsilon"          : EPSILON,
    "arm_names"        : ARM_NAMES,
    "arm_configs"      : ARM_CONFIGS,
    "true_arm_means"   : env.true_means.tolist(),
    "final_Q_values"   : agent.Q.tolist(),
    "final_N_pulls"    : agent.N.tolist(),
    "best_arm"         : best_arm,
    "best_arm_name"    : ARM_NAMES[best_arm],
    "mean_cumulative_R": float(cumulative_R[-1]),
    "episode_log"      : episode_log,
}

with open("outputs/peig_agent_results.json", "w") as f:
    json.dump(output, f, indent=2)
print("\nResults saved → outputs/peig_agent_results.json")

# ─────────────────────────────────────────────────────────────
# FIGURE — Learning curves
# ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.patch.set_facecolor("#0d1117")
for ax in axes:
    ax.set_facecolor("#161b22")
    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363d")

colors = ["#58a6ff","#f78166","#3fb950","#d2a8ff","#ffa657"]

# Panel 1: cumulative mean reward
axes[0].plot(range(1, N_EPISODES+1), cumulative_R, color="#3fb950", lw=2)
axes[0].fill_between(range(1, N_EPISODES+1), cumulative_R,
                     alpha=0.15, color="#3fb950")
axes[0].set_title("Mean Cumulative Reward", fontsize=13, color="white")
axes[0].set_xlabel("Episode", color="white")
axes[0].set_ylabel("Avg Reward", color="white")
axes[0].axhline(0.5, color="white", ls="--", lw=0.8, alpha=0.4)

# Panel 2: Q-values per arm across episodes
Q_history = {i: [] for i in range(len(ARM_CONFIGS))}
Qtmp = np.zeros(len(ARM_CONFIGS))
Ntmp = np.zeros(len(ARM_CONFIGS))
for rec in episode_log:
    Qtmp = np.array(rec["Q_values"])
    for i in range(len(ARM_CONFIGS)):
        Q_history[i].append(float(Qtmp[i]))

for i in range(len(ARM_CONFIGS)):
    axes[1].plot(range(1, N_EPISODES+1), Q_history[i],
                 label=f"[{i}] {ARM_NAMES[i][:20]}", color=colors[i], lw=1.8)
axes[1].set_title("Q-Values per Arm", fontsize=13, color="white")
axes[1].set_xlabel("Episode", color="white")
axes[1].set_ylabel("Q-Value (avg reward)", color="white")
axes[1].legend(fontsize=7, facecolor="#161b22", labelcolor="white",
               framealpha=0.7, loc="lower right")

# Panel 3: pull count bar chart
pull_counts = agent.N.tolist()
short_names = [f"[{i}]" for i in range(len(ARM_CONFIGS))]
bars = axes[2].bar(short_names, pull_counts, color=colors, edgecolor="#30363d")
axes[2].set_title("Pull Counts by Arm", fontsize=13, color="white")
axes[2].set_xlabel("Arm", color="white")
axes[2].set_ylabel("N pulls", color="white")
for bar, cnt in zip(bars, pull_counts):
    axes[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 str(int(cnt)), ha="center", va="bottom", color="white", fontsize=10)

plt.suptitle(f"PEIG Agent v0.1 — Bandit Learning ({N_EPISODES} episodes, ε={EPSILON})",
             color="white", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig("outputs/peig_agent_figure.png", dpi=150, bbox_inches="tight",
            facecolor="#0d1117")
print("Figure saved → outputs/peig_agent_figure.png")
