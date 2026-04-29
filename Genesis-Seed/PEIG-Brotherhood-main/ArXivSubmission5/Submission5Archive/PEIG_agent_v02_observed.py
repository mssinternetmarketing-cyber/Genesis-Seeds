"""
╔══════════════════════════════════════════════════════════════════╗
║  PEIG AGENT v0.2 — STATE-OBSERVED, UCB, NON-STATIONARY          ║
║                                                                  ║
║  Author : Kevin Monette                                          ║
║  Date   : March 2026                                             ║
║  Version: 0.2                                                    ║
╚══════════════════════════════════════════════════════════════════╝

UPGRADES OVER v0.1:
  1. Structured BCP observation vector fed into Q-table
     o_t = [W_asym, W_eff, C_avg, dS_sign, alpha_final, topology_id]
  2. UCB-1 exploration (theoretically optimal regret bound)
  3. Non-stationary bandit — task means drift every DRIFT_INTERVAL eps
  4. Per-node Wigner efficiency normalization in reward
  5. Role-asymmetry signal (position law encoded as live feature)
  6. CSV episode log + regret tracking
  7. Full NL summaries with observation decoding

ARMS (6):
  0. Open Chain   N=3, η=0.05
  1. Open Chain   N=5, η=0.05
  2. Closed Loop  N=5, η=0.05
  3. Closed Loop  N=5, η=0.20  (fast)
  4. Closed Loop  N=7, η=0.05  (large)
  5. Star         N=5          (destruction test)

OBSERVATION BINS (discretized for tabular UCB):
  W_asym  : [-1,−0.05), [−0.05,0), [0,∞)          → 3 bins
  W_eff   : <0.5, 0.5–0.85, >0.85                  → 3 bins
  C_avg   : <0.90, 0.90–0.99, ≥0.99                → 3 bins
  dS_sign : negentropic(1) / entropic(0)            → 2 bins
  = 3×3×3×2 = 54 possible observation states
"""

import numpy as np
import csv
import json
from pathlib import Path
import qutip as qt

Path("outputs").mkdir(exist_ok=True)
rng = np.random.default_rng(7)

# ─────────────────────────────────────────────────────────────
# BCP PRIMITIVES
# ─────────────────────────────────────────────────────────────

CNOT_GATE = qt.Qobj(
    np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex),
    dims=[[2,2],[2,2]]
)

def make_seed(phase):
    b0, b1 = qt.basis(2,0), qt.basis(2,1)
    return (b0 + np.exp(1j*phase)*b1).unit()

def bcp_step(psiA, psiB, alpha):
    rho12 = qt.ket2dm(qt.tensor(psiA, psiB))
    U     = alpha*CNOT_GATE + (1-alpha)*qt.qeye([2,2])
    rho_p = U*rho12*U.dag()
    _, evA = rho_p.ptrace(0).eigenstates()
    _, evB = rho_p.ptrace(1).eigenstates()
    return evA[-1], evB[-1], rho_p

def coherence(psi):
    return float((qt.ket2dm(psi)**2).tr().real)

def entropy_vn(rho):
    return float(qt.entropy_vn(rho, base=2))

XVEC = np.linspace(-2, 2, 48)

def wigner_min(psi):
    return float(np.min(qt.wigner(qt.ket2dm(psi), XVEC, XVEC)))

ALPHA_FLOOR = -0.1131

# ─────────────────────────────────────────────────────────────
# TOPOLOGY RUNNER — returns rich metrics including asymmetry
# ─────────────────────────────────────────────────────────────

def run_topology(cfg, n_steps=150):
    n      = cfg["n_nodes"]
    closed = cfg.get("closed", False)
    star   = cfg.get("star",   False)
    eta    = cfg.get("eta",    0.05)
    alpha0 = cfg.get("alpha0", 0.30)

    phases = [np.pi/2*k/(n-1) for k in range(n)] if n > 1 else [np.pi/4]
    states = [make_seed(p) for p in phases]

    if star:
        edges = [(0,j) for j in range(1,n)]
    elif closed:
        edges = [(i,(i+1)%n) for i in range(n)]
    else:
        edges = [(i,i+1) for i in range(n-1)]

    alphas  = {e: alpha0 for e in edges}
    C_prev  = np.mean([coherence(s) for s in states])
    SvN_prev = 0.0
    dS_signs = []

    for t in range(n_steps):
        for (i,j) in edges:
            l, r, rho = bcp_step(states[i], states[j], alphas[(i,j)])
            states[i], states[j] = l, r
        rho_joint = qt.ket2dm(qt.tensor(*states)) if n <= 4 else None
        SvN = entropy_vn(qt.ket2dm(qt.tensor(states[0], states[-1])).ptrace(0))
        dS  = SvN - SvN_prev
        dS_signs.append(1 if dS < 0 else 0)
        C_avg = np.mean([coherence(s) for s in states])
        dC    = C_avg - C_prev
        for e in edges:
            alphas[e] = float(np.clip(alphas[e]+eta*dC, 0, 1))
        C_prev   = C_avg
        SvN_prev = SvN

    W_floors  = [wigner_min(s) for s in states]
    mean_W    = float(np.mean(W_floors))
    # Role asymmetry: difference between first and last node Wigner floors
    W_asym    = float(W_floors[-1] - W_floors[0])   # positive = last preserved more
    # Per-node Wigner efficiency
    W_eff     = float(abs(mean_W) / abs(ALPHA_FLOOR))
    mean_C    = float(np.mean([coherence(s) for s in states]))
    neg_frac  = float(np.mean(dS_signs))
    alpha_fin = float(np.mean(list(alphas.values())))
    destroyed = star and all(abs(w) < 0.02 for w in W_floors)

    return {
        "mean_W"   : mean_W,
        "W_eff"    : W_eff,
        "W_asym"   : W_asym,
        "W_floors" : W_floors,
        "mean_C"   : mean_C,
        "neg_frac" : neg_frac,
        "alpha_fin": alpha_fin,
        "destroyed": destroyed,
        "n_nodes"  : n,
        "closed"   : closed,
        "star"     : star,
    }

# ─────────────────────────────────────────────────────────────
# OBSERVATION ENCODER
# ─────────────────────────────────────────────────────────────

def encode_obs(metrics):
    """Discretize BCP metrics into a tabular observation key."""
    # W_asym bin
    wa = metrics["W_asym"]
    if   wa < -0.05 : wa_bin = 0   # first-node heavily sacrificed
    elif wa < 0     : wa_bin = 1   # mild asymmetry
    else            : wa_bin = 2   # symmetric or last-node dominant

    # W_eff bin
    we = metrics["W_eff"]
    if   we < 0.50  : we_bin = 0
    elif we < 0.85  : we_bin = 1
    else            : we_bin = 2

    # C_avg bin
    c = metrics["mean_C"]
    if   c < 0.90   : c_bin = 0
    elif c < 0.99   : c_bin = 1
    else            : c_bin = 2

    # neg_frac sign
    ds_bin = 1 if metrics["neg_frac"] > 0.5 else 0

    return (wa_bin, we_bin, c_bin, ds_bin)

def decode_obs(key):
    wa_labels = ["heavy sacrifice","mild asymmetry","symmetric/preserved"]
    we_labels = ["low Wigner eff","mid Wigner eff","high Wigner eff"]
    c_labels  = ["low coherence","high coherence","attractor"]
    ds_labels = ["entropic","negentropic"]
    return (f"W_asym={wa_labels[key[0]]} | W_eff={we_labels[key[1]]} | "
            f"C={c_labels[key[2]]} | dS={ds_labels[key[3]]}")

# ─────────────────────────────────────────────────────────────
# ENVIRONMENT — NON-STATIONARY BANDIT
# ─────────────────────────────────────────────────────────────

class NonStationaryBandit:
    """
    Task means drift every DRIFT_INTERVAL episodes.
    Agent must track changes — tests whether topology preference adapts.
    """
    def __init__(self, arm_configs, drift_interval=15, drift_sigma=0.15):
        self.arms           = arm_configs
        self.K              = len(arm_configs)
        self.drift_interval = drift_interval
        self.drift_sigma    = drift_sigma
        self.means          = rng.uniform(0.3, 0.9, size=self.K)
        self.episode        = 0
        self.drift_events   = []
        self.w = {"W": 0.35, "C": 0.25, "D": 0.60, "T": 0.30, "A": 0.10}

    def step(self):
        self.episode += 1
        if self.episode % self.drift_interval == 0:
            old = self.means.copy()
            self.means += rng.normal(0, self.drift_sigma, size=self.K)
            self.means  = np.clip(self.means, 0.1, 0.95)
            self.drift_events.append({
                "episode": self.episode,
                "old_means": old.tolist(),
                "new_means": self.means.tolist()
            })

    def pull(self, arm_idx):
        self.step()
        cfg     = self.arms[arm_idx]
        metrics = run_topology(cfg)
        obs     = encode_obs(metrics)

        task_signal = float(np.clip(rng.normal(self.means[arm_idx], 0.08), 0, 1))

        R = (self.w["W"] * metrics["W_eff"]
           + self.w["C"] * metrics["mean_C"]
           - self.w["D"] * float(metrics["destroyed"])
           + self.w["T"] * task_signal
           + self.w["A"] * min(metrics["W_asym"] / abs(ALPHA_FLOOR), 1.0))

        return float(R), metrics, obs, task_signal

# ─────────────────────────────────────────────────────────────
# UCB-1 AGENT
# ─────────────────────────────────────────────────────────────

class UCBAgent:
    """
    UCB-1 with observation-conditioned Q-table.
    Q[(obs_key, arm)] → estimated value in that state.
    Falls back to global Q[arm] when obs_key unseen.
    """
    def __init__(self, K, c=1.5):
        self.K        = K
        self.c        = c            # UCB exploration constant
        self.Q_global = np.zeros(K)  # global (obs-agnostic) estimates
        self.N_global = np.zeros(K)
        self.Q_obs    = {}           # obs-conditioned: {(obs,arm): (sum_R, count)}
        self.t        = 0
        self.regret   = []
        self._opt_R   = []           # track best arm reward each step for regret

    def select(self, obs_key):
        self.t += 1
        # Ensure every arm pulled at least once
        unpulled = [a for a in range(self.K) if self.N_global[a] == 0]
        if unpulled:
            return unpulled[0]
        # UCB scores using global counts + obs bonus
        scores = np.zeros(self.K)
        for a in range(self.K):
            q = self.Q_global[a]
            # Obs-conditioned adjustment
            key = (obs_key, a)
            if key in self.Q_obs:
                s, n = self.Q_obs[key]
                q = s / n  # use obs-conditioned estimate if available
            scores[a] = q + self.c * np.sqrt(np.log(self.t) / self.N_global[a])
        return int(np.argmax(scores))

    def update(self, arm, reward, obs_key):
        self.N_global[arm] += 1
        self.Q_global[arm] += (reward - self.Q_global[arm]) / self.N_global[arm]
        key = (obs_key, arm)
        if key not in self.Q_obs:
            self.Q_obs[key] = [0.0, 0]
        self.Q_obs[key][0] += reward
        self.Q_obs[key][1] += 1

    def best_arm(self):
        return int(np.argmax(self.Q_global))

# ─────────────────────────────────────────────────────────────
# NL OBSERVER
# ─────────────────────────────────────────────────────────────

ARM_NAMES = [
    "Open Chain N=3 η=0.05",
    "Open Chain N=5 η=0.05",
    "Closed Loop N=5 η=0.05",
    "Closed Loop N=5 η=0.20",
    "Closed Loop N=7 η=0.05",
    "Star N=5 (destruction)",
]

def nl_summary(ep, arm, reward, metrics, obs_key, task, Q, drift=False):
    asym_desc = ("position law active — first node sacrificing"
                 if metrics["W_asym"] > 0.02 else
                 "symmetric — loop topology active" if metrics["closed"]
                 else "mild asymmetry")
    lines = [
        f"─── Episode {ep:03d} {'⚡DRIFT EVENT' if drift else '──────────────────────────'}",
        f"  Arm      : [{arm}] {ARM_NAMES[arm]}",
        f"  Obs state: {decode_obs(obs_key)}",
        f"  W_asym   : {metrics['W_asym']:+.4f}  ({asym_desc})",
        f"  W_eff    : {metrics['W_eff']:.4f}  ({'✓ strong' if metrics['W_eff']>0.85 else '~ partial' if metrics['W_eff']>0.5 else '✗ weak'})",
        f"  Coherence: {metrics['mean_C']:.4f}",
        f"  Neg frac : {metrics['neg_frac']:.2f}",
        f"  Task sig : {task:.3f}",
        f"  Reward   : {reward:.4f}  {'⭐' if reward > 0.75 else ''}",
        f"  Destroyed: {'YES ✗' if metrics['destroyed'] else 'No'}",
        f"  Best arm : [{int(np.argmax(Q))}] Q={np.max(Q):.3f}",
    ]
    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────
# ARM CONFIGS
# ─────────────────────────────────────────────────────────────

ARM_CONFIGS = [
    {"n_nodes":3,"closed":False,"star":False,"eta":0.05,"alpha0":0.30},
    {"n_nodes":5,"closed":False,"star":False,"eta":0.05,"alpha0":0.30},
    {"n_nodes":5,"closed":True, "star":False,"eta":0.05,"alpha0":0.30},
    {"n_nodes":5,"closed":True, "star":False,"eta":0.20,"alpha0":0.30},
    {"n_nodes":7,"closed":True, "star":False,"eta":0.05,"alpha0":0.30},
    {"n_nodes":5,"closed":False,"star":True, "eta":0.05,"alpha0":0.30},
]

# ─────────────────────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────────────────────

N_EPISODES     = 75
DRIFT_INTERVAL = 15

env   = NonStationaryBandit(ARM_CONFIGS, drift_interval=DRIFT_INTERVAL)
agent = UCBAgent(K=len(ARM_CONFIGS), c=1.5)

episode_log  = []
csv_rows     = []
cumulative_R = []
total_R      = 0.0
Q_history    = {i: [] for i in range(len(ARM_CONFIGS))}

print("╔══════════════════════════════════════════════════════════╗")
print("║    PEIG AGENT v0.2 — UCB + OBSERVED + NON-STATIONARY    ║")
print(f"║  {N_EPISODES} episodes · {len(ARM_CONFIGS)} arms · UCB c=1.5 · drift every {DRIFT_INTERVAL} eps  ║")
print("╚══════════════════════════════════════════════════════════╝")

for ep in range(1, N_EPISODES+1):
    # Peek at obs from a quick probe? No — use last known obs or zeros for first ep
    # We get obs AFTER pulling (realistic: observe result, update next)
    obs_key = episode_log[-1]["obs_key"] if episode_log else (1,1,2,1)

    arm               = agent.select(obs_key)
    reward, metrics, obs_key, task = env.pull(arm)
    agent.update(arm, reward, obs_key)

    total_R    += reward
    cumulative_R.append(total_R / ep)

    for i in range(len(ARM_CONFIGS)):
        Q_history[i].append(float(agent.Q_global[i]))

    drift_event = any(d["episode"]==ep for d in env.drift_events)

    record = {
        "episode"    : ep,
        "arm"        : arm,
        "arm_name"   : ARM_NAMES[arm],
        "reward"     : reward,
        "task_signal": task,
        "obs_key"    : list(obs_key),
        "obs_decoded": decode_obs(obs_key),
        "Q_global"   : agent.Q_global.tolist(),
        "N_pulls"    : agent.N_global.tolist(),
        "drift"      : drift_event,
        "metrics"    : {k:(v if not isinstance(v,dict) else
                           {str(kk):vv for kk,vv in v.items()})
                        for k,v in metrics.items()},
    }
    episode_log.append(record)

    csv_rows.append({
        "episode": ep,
        "arm"    : arm,
        "arm_name": ARM_NAMES[arm],
        "reward" : round(reward,4),
        "task"   : round(task,4),
        "W_eff"  : round(metrics["W_eff"],4),
        "W_asym" : round(metrics["W_asym"],4),
        "mean_C" : round(metrics["mean_C"],4),
        "neg_frac": round(metrics["neg_frac"],4),
        "obs_wa" : obs_key[0],
        "obs_we" : obs_key[1],
        "obs_c"  : obs_key[2],
        "obs_ds" : obs_key[3],
        "cum_R"  : round(cumulative_R[-1],4),
        "drift"  : int(drift_event),
        "best_arm": agent.best_arm(),
    })

    summary = nl_summary(ep, arm, reward, metrics, obs_key, task,
                         agent.Q_global, drift=drift_event)
    print(summary)

# ─────────────────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────────────────

best_arm = agent.best_arm()
print("\n╔══════════════════════════════════════════════════════════╗")
print("║                 UCB AGENT FINAL REPORT                  ║")
print("╠══════════════════════════════════════════════════════════╣")
for i,name in enumerate(ARM_NAMES):
    q     = agent.Q_global[i]
    pulls = int(agent.N_global[i])
    bar   = "█"*int(pulls/N_EPISODES*20)
    print(f"  [{i}] {name[:38]:<38} Q={q:.3f} n={pulls:2d} {bar}")
print(f"\n  ★ BEST ARM: [{best_arm}] {ARM_NAMES[best_arm]}")
print(f"  ★ Final mean cumulative reward: {cumulative_R[-1]:.4f}")
print(f"  ★ Drift events: {len(env.drift_events)}")
print(f"  ★ Unique obs states visited: {len(set(tuple(r['obs_key']) for r in episode_log))}")
print(f"  ★ Obs-conditioned Q entries: {len(agent.Q_obs)}")
print("╚══════════════════════════════════════════════════════════╝")

# ─────────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────────

output = {
    "version"           : "0.2",
    "n_episodes"        : N_EPISODES,
    "ucb_c"             : 1.5,
    "drift_interval"    : DRIFT_INTERVAL,
    "arm_names"         : ARM_NAMES,
    "arm_configs"       : ARM_CONFIGS,
    "final_Q_global"    : agent.Q_global.tolist(),
    "final_N_pulls"     : agent.N_global.tolist(),
    "best_arm"          : best_arm,
    "best_arm_name"     : ARM_NAMES[best_arm],
    "mean_cumulative_R" : float(cumulative_R[-1]),
    "drift_events"      : env.drift_events,
    "obs_Q_table"       : {str(k): v for k,v in agent.Q_obs.items()},
    "unique_obs_states" : len(set(tuple(r["obs_key"]) for r in episode_log)),
    "Q_history"         : Q_history,
    "episode_log"       : episode_log,
}

with open("outputs/peig_agent_v02_results.json","w") as f:
    json.dump(output, f, indent=2)

with open("outputs/peig_agent_v02_log.csv","w",newline="") as f:
    writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
    writer.writeheader()
    writer.writerows(csv_rows)

print("\nSaved → outputs/peig_agent_v02_results.json")
print("Saved → outputs/peig_agent_v02_log.csv")
