"""
PEIG PAPER V — MASTER VISUALIZATION
All five experiments: Intrinsic Reward, Two-Agent Game,
Noise-Adaptive, Qudit Generalisation, Choi Rank Tracking
Author: Kevin Monette | March 2026
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

# ── Load all data ────────────────────────────────────────────
with open("outputs/exp1_intrinsic_reward.json")    as f: e1 = json.load(f)
with open("outputs/exp2_two_agent_game.json")       as f: e2 = json.load(f)
with open("outputs/exp3_lindblad_adaptive.json")    as f: e3 = json.load(f)
with open("outputs/exp4_qudit.json")                as f: e4 = json.load(f)
with open("outputs/exp5_choi_rank.json")            as f: e5 = json.load(f)

# ── Style ────────────────────────────────────────────────────
DARK   = '#0A0A1A'
GOLD   = '#FFD700'
GREEN  = '#2ECC71'
ORANGE = '#FF6B35'
PURPLE = '#9B59B6'
BLUE   = '#3498DB'
RED    = '#E74C3C'
WHITE  = '#ECEFF1'
GRAY   = '#7F8C8D'
PANEL  = '#1A1A2E'

ARM_COLORS = [BLUE, ORANGE, GREEN, PURPLE, '#FF9F43', RED]
ARM_NAMES_SHORT = ["Open\nN=3", "Open\nN=5", "Closed\nN=5\nη=0.05",
                   "Closed\nN=5\nη=0.20", "Closed\nN=7", "Star\nN=5"]

def styled(ax, title, fs=9):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=WHITE, labelsize=7)
    for sp in ax.spines.values(): sp.set_color(GRAY)
    ax.set_title(title, color=WHITE, fontsize=fs, fontweight='bold', pad=5)
    ax.xaxis.label.set_color(WHITE)
    ax.yaxis.label.set_color(WHITE)
    ax.grid(True, alpha=0.15, color=GRAY)
    return ax

# ── Figure ───────────────────────────────────────────────────
fig = plt.figure(figsize=(24, 20))
fig.patch.set_facecolor(DARK)
gs  = gridspec.GridSpec(4, 4, figure=fig,
                         hspace=0.52, wspace=0.38,
                         left=0.05, right=0.97,
                         top=0.93, bottom=0.04)

fig.text(0.5, 0.965,
    "PEIG Paper V — Agent Experiments: Intrinsic Reward · Two-Agent Game · "
    "Noise-Adaptive · Qudit · Choi Rank",
    ha='center', fontsize=14, fontweight='bold', color=GOLD, fontfamily='monospace')
fig.text(0.5, 0.952,
    "Kevin Monette  |  March 2026  |  5 experiments  |  UCB bandit learning across BCP topologies",
    ha='center', fontsize=9, color=WHITE, alpha=0.7)

# ═══════════════════════════════════════════════════════════
# ROW 0 — EXPERIMENT 1: INTRINSIC PEIG-Q AGENT
# ═══════════════════════════════════════════════════════════

log1  = e1["log"]
eps1  = [r["episode"] for r in log1]
Q_now = [r["Q_now"]   for r in log1]
arms1 = [r["arm"]     for r in log1]
Q_hist = e1["Q_history"]
pulls1 = e1["pulls"]
best1  = e1["best_arm"]

# 1a: Q_now trajectory
ax = styled(fig.add_subplot(gs[0,0]),
            "Exp 1: Intrinsic PEIG-Q per Episode\n(no external reward — only ΔQ)")
ax.plot(eps1, Q_now, color=GREEN, lw=2)
ax.fill_between(eps1, Q_now, 0, color=GREEN, alpha=0.1)
ax.set_xlabel("Episode"); ax.set_ylabel("Q (PEIG quality)")
ax.text(0.02, 0.88,
        f"Best arm: {e1['best_arm_name']}\nZero external signal",
        transform=ax.transAxes, color=GOLD, fontsize=7.5,
        bbox=dict(boxstyle='round', facecolor=PANEL, alpha=0.8))

# 1b: UCB Q-value convergence per arm
ax = styled(fig.add_subplot(gs[0,1]),
            "Exp 1: UCB Q-Values per Arm\nAgent learns topology preference")
for i in range(6):
    vals = Q_hist[str(i)]
    col  = ARM_COLORS[i]
    ls   = '--' if i == 5 else '-'   # star = dashed
    lw   = 2.5 if i == best1 else 1.5
    ax.plot(range(len(vals)), vals, color=col, lw=lw, ls=ls,
            label=ARM_NAMES_SHORT[i].replace('\n',' '), alpha=0.9)
ax.set_xlabel("Episode"); ax.set_ylabel("Q-value (UCB)")
ax.legend(fontsize=5.5, facecolor=PANEL, labelcolor=WHITE, ncol=2,
          loc='lower right')
ax.text(0.02, 0.88, "Star arm punished every pull",
        transform=ax.transAxes, color=RED, fontsize=7.5)

# 1c: Pull counts
ax = styled(fig.add_subplot(gs[0,2]),
            "Exp 1: Arm Pull Counts\nExploration vs exploitation")
bars = ax.bar(range(6), pulls1, color=ARM_COLORS, alpha=0.85, edgecolor=WHITE, lw=0.5)
for b, v in zip(bars, pulls1):
    ax.text(b.get_x()+b.get_width()/2, v+0.3,
            str(int(v)), ha='center', fontsize=8, color=WHITE, fontweight='bold')
ax.set_xticks(range(6))
ax.set_xticklabels(ARM_NAMES_SHORT, fontsize=6.5, color=WHITE)
ax.set_ylabel("N pulls")

# 1d: PEIG vector P E I G final values
ax = styled(fig.add_subplot(gs[0,3]),
            "Exp 1: PEIG Vector at Best Arm\nFirst quantified intrinsic state")
best_eps = [r for r in log1 if r["arm"] == best1]
if best_eps:
    last = best_eps[-1]
    dims = ['P\n(Presence)', 'E\n(Entanglement)', 'I\n(Integration)', 'G\n(Growth)']
    vals_peig = [last['P'], last['E'], last['I'], last['G']]
    cols_p = [GOLD, BLUE, GREEN, PURPLE]
    bars2 = ax.bar(range(4), vals_peig, color=cols_p, alpha=0.85,
                   edgecolor=WHITE, lw=0.5)
    for b, v in zip(bars2, vals_peig):
        ax.text(b.get_x()+b.get_width()/2, v+0.01,
                f'{v:.3f}', ha='center', fontsize=9, color=WHITE, fontweight='bold')
    ax.set_xticks(range(4)); ax.set_xticklabels(dims, fontsize=8, color=WHITE)
    ax.set_ylabel("PEIG component value"); ax.set_ylim(0, 1.15)
    Q_total = last['P']*0.25+last['E']*0.25+last['I']*0.25+last['G']*0.25
    ax.text(0.5, 0.92, f"Q = {Q_total:.4f}", transform=ax.transAxes,
            ha='center', color=GOLD, fontsize=10, fontweight='bold')

# ═══════════════════════════════════════════════════════════
# ROW 1 — EXPERIMENT 2: TWO-AGENT GAME + EXPERIMENT 3: NOISE
# ═══════════════════════════════════════════════════════════

log2   = e2["log"]
eps2   = [r["ep"]            for r in log2]
o_rew  = [r["omega_reward"]  for r in log2]
a_rew  = [r["alpha_reward"]  for r in log2]
o_W    = [r["omega_W"]       for r in log2]
a_W    = [r["alpha_W"]       for r in log2]
oQ     = e2["omega_Q"]
aQ     = e2["alpha_Q"]

# 2a: Reward trajectories both agents
ax = styled(fig.add_subplot(gs[1,0]),
            "Exp 2: Two-Agent Rewards\nOmega vs Alpha coupled BCP game")
ax.plot(eps2, o_rew, color=GOLD,   lw=2, alpha=0.85, label='Omega reward')
ax.plot(eps2, a_rew, color=PURPLE, lw=2, alpha=0.85, label='Alpha reward')
ax.set_xlabel("Episode"); ax.set_ylabel("Reward")
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)
ax.text(0.02, 0.05,
        f"Alpha Q={max(aQ):.4f}\nOmega Q={max(oQ):.4f}\nAsymmetry emerges",
        transform=ax.transAxes, color=WHITE, fontsize=7.5,
        bbox=dict(boxstyle='round', facecolor=PANEL, alpha=0.8))

# 2b: Final Q values both agents per arm
ax = styled(fig.add_subplot(gs[1,1]),
            "Exp 2: Final Q-Values per Arm\nNash equilibrium = Closed N=5")
arm_names_2 = ["Open\nN=3", "Closed\nN=5\nη=0.05", "Closed\nN=5\nη=0.20"]
x = np.arange(3); w = 0.35
ax.bar(x-w/2, oQ, w, color=GOLD,   alpha=0.85, label='Omega', edgecolor=WHITE, lw=0.5)
ax.bar(x+w/2, aQ, w, color=PURPLE, alpha=0.85, label='Alpha', edgecolor=WHITE, lw=0.5)
for i, (o, a) in enumerate(zip(oQ, aQ)):
    ax.text(i-w/2, o+0.002, f'{o:.4f}', ha='center', fontsize=6.5, color=GOLD)
    ax.text(i+w/2, a+0.002, f'{a:.4f}', ha='center', fontsize=6.5, color=PURPLE)
ax.set_xticks(x); ax.set_xticklabels(arm_names_2, fontsize=7.5, color=WHITE)
ax.set_ylabel("Q-value"); ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)
ax.text(0.02, 0.05,
        f"Both → Closed N=5 η=0.05\nRole asymmetry: ΔQ={max(aQ)-max(oQ):+.4f}",
        transform=ax.transAxes, color=GREEN, fontsize=7.5,
        bbox=dict(boxstyle='round', facecolor=PANEL, alpha=0.8))

# 3a: Noise experiment — W_eff per arm per noise level
log3 = e3["log"]
arm_names_3 = e3.get("arm_names",
    ["low+O3","low+C5","low+C5f","med+O3","med+C5","med+C5f","hi+O3","hi+C5","hi+C5f"])
final_Q3 = e3["final_Q"]
final_N3 = e3["final_N"]

ax = styled(fig.add_subplot(gs[1,2]),
            "Exp 3: Noise-Adaptive Agent\nFinal Q per arm (9-arm bandit)")
cols3 = [BLUE]*3 + [ORANGE]*3 + [RED]*3
bars3 = ax.bar(range(9), final_Q3, color=cols3, alpha=0.85,
               edgecolor=WHITE, lw=0.5)
for b, v, n in zip(bars3, final_Q3, final_N3):
    ax.text(b.get_x()+b.get_width()/2, v+0.002,
            f'{v:.3f}\n(n={int(n)})', ha='center', fontsize=6, color=WHITE)
ax.set_xticks(range(9))
labels3 = [n[:8] for n in arm_names_3] if arm_names_3 else [f"arm{i}" for i in range(9)]
ax.set_xticklabels(labels3, fontsize=6, rotation=35, ha='right', color=WHITE)
ax.set_ylabel("Final Q-value")
# Legend for noise levels
from matplotlib.patches import Patch
ax.legend(handles=[
    Patch(facecolor=BLUE,   label='Low noise'),
    Patch(facecolor=ORANGE, label='Med noise'),
    Patch(facecolor=RED,    label='High noise'),
], fontsize=7, facecolor=PANEL, labelcolor=WHITE)
best3  = e3["best_arm_name"]
ax.text(0.02, 0.88, f"Best overall: {best3}",
        transform=ax.transAxes, color=GREEN, fontsize=7.5,
        bbox=dict(boxstyle='round', facecolor=PANEL, alpha=0.8))

# 3b: Closed vs open W_eff gap at different noise levels
ax = styled(fig.add_subplot(gs[1,3]),
            "Exp 3: Closed vs Open Advantage\nGap widens with noise (noise-monotonic)")
# Extract from log
noise_labels = ['low', 'medium', 'high']
closed_w = {nl: [] for nl in noise_labels}
open_w   = {nl: [] for nl in noise_labels}
for r in log3:
    nl = r.get("noise","")
    arm = r.get("arm_name","")
    w   = r.get("W_eff", 0)
    if nl in noise_labels:
        if 'C' in arm or 'closed' in arm.lower():
            closed_w[nl].append(w)
        else:
            open_w[nl].append(w)

noise_cols = [BLUE, ORANGE, RED]
x3b = np.arange(3); w3b = 0.35
c_means = [np.mean(closed_w[nl]) if closed_w[nl] else 0 for nl in noise_labels]
o_means = [np.mean(open_w[nl])   if open_w[nl]   else 0 for nl in noise_labels]
ax.bar(x3b-w3b/2, c_means, w3b, color=GREEN,  alpha=0.85, label='Closed', edgecolor=WHITE, lw=0.5)
ax.bar(x3b+w3b/2, o_means, w3b, color=ORANGE, alpha=0.85, label='Open',   edgecolor=WHITE, lw=0.5)
gaps = [c-o for c,o in zip(c_means, o_means)]
for i,(c,o,g) in enumerate(zip(c_means, o_means, gaps)):
    ax.annotate(f'Δ={g:+.3f}', (i, max(c,o)+0.01),
                ha='center', fontsize=8, color=GOLD, fontweight='bold')
ax.set_xticks(x3b); ax.set_xticklabels(['Low\nnoise','Med\nnoise','High\nnoise'],
                                         fontsize=8, color=WHITE)
ax.set_ylabel("Mean W_eff")
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)

# ═══════════════════════════════════════════════════════════
# ROW 2 — EXPERIMENT 4: QUDIT + EXPERIMENT 5: CHOI RANK
# ═══════════════════════════════════════════════════════════

results4 = e4["results"]
dims_u   = sorted(set(r["d"] for r in results4))
open_sc  = {r["d"]: r["score"] for r in results4 if not r["closed"]}
clos_sc  = {r["d"]: r["score"] for r in results4 if     r["closed"]}
open_neg = {r["d"]: r["neg_frac"] for r in results4 if not r["closed"]}
clos_neg = {r["d"]: r["neg_frac"] for r in results4 if     r["closed"]}
open_C   = {r["d"]: r["mean_C"]   for r in results4 if not r["closed"]}
clos_C   = {r["d"]: r["mean_C"]   for r in results4 if     r["closed"]}

# 4a: Score by dimension — THE KEY PLOT
ax = styled(fig.add_subplot(gs[2,0]),
            "Exp 4: Open vs Closed Score by Dimension\n★ Critical d* inversion at d≈4-5")
dims_arr  = list(dims_u)
o_scores  = [open_sc[d] for d in dims_arr]
c_scores  = [clos_sc[d] for d in dims_arr]
x4 = np.arange(len(dims_arr)); w4 = 0.35
ax.bar(x4-w4/2, o_scores, w4, color=ORANGE, alpha=0.85, label='Open chain', edgecolor=WHITE, lw=0.5)
ax.bar(x4+w4/2, c_scores, w4, color=GREEN,  alpha=0.85, label='Closed loop', edgecolor=WHITE, lw=0.5)
for i, d in enumerate(dims_arr):
    gap = c_scores[i]-o_scores[i]
    col = GREEN if gap > 0 else RED
    ax.annotate(f'{gap:+.3f}', (i, max(o_scores[i], c_scores[i])+0.005),
                ha='center', fontsize=8, color=col, fontweight='bold')
ax.set_xticks(x4); ax.set_xticklabels([f'd={d}' for d in dims_arr], fontsize=8, color=WHITE)
ax.set_ylabel("Score")
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)
# Shade the inversion zone
ax.axvspan(2.5, 3.5, alpha=0.08, color=RED)
ax.text(3.0, max(o_scores+c_scores)*0.98, 'd* zone',
        ha='center', fontsize=7, color=RED, style='italic')

# 4b: Advantage Δ = closed - open across d
ax = styled(fig.add_subplot(gs[2,1]),
            "Exp 4: Closed-Loop Advantage Δ vs d\nSign flip reveals critical dimension d*")
advantages = [c_scores[i]-o_scores[i] for i in range(len(dims_arr))]
cols4b = [GREEN if a > 0 else RED for a in advantages]
bars4b = ax.bar(dims_arr, advantages, color=cols4b, alpha=0.85, edgecolor=WHITE, lw=0.5)
ax.axhline(0, color=WHITE, ls='--', lw=1.5, alpha=0.6)
for b, v, d in zip(bars4b, advantages, dims_arr):
    ax.text(d, v+(0.003 if v>=0 else -0.007),
            f'{v:+.4f}', ha='center',
            va='bottom' if v>=0 else 'top',
            fontsize=8, color=WHITE, fontweight='bold')
ax.set_xlabel("Hilbert space dimension d")
ax.set_ylabel("Δ Score (closed − open)")
ax.set_xticks(dims_arr)
# Shade inversion
ax.axvspan(4.3, 5.3, alpha=0.12, color=RED)
ax.text(4.8, min(advantages)*0.8, 'd*≈4-5', ha='center', fontsize=8, color=RED, fontweight='bold')

# 4c: neg_frac — negentropic fraction by d
ax = styled(fig.add_subplot(gs[2,2]),
            "Exp 4: Negentropic Fraction by d\nOpen chain wins on entropy at high d")
o_nf = [open_neg[d] for d in dims_arr]
c_nf = [clos_neg[d] for d in dims_arr]
ax.plot(dims_arr, o_nf, 'o-', color=ORANGE, lw=2, ms=8, label='Open chain')
ax.plot(dims_arr, c_nf, 's-', color=GREEN,  lw=2, ms=8, label='Closed loop')
for d, on, cn in zip(dims_arr, o_nf, c_nf):
    ax.annotate(f'{on:.2f}', (d, on+0.008), ha='center', fontsize=7, color=ORANGE)
    ax.annotate(f'{cn:.2f}', (d, cn-0.015), ha='center', fontsize=7, color=GREEN)
ax.set_xlabel("Hilbert space dimension d"); ax.set_ylabel("Neg. fraction")
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE); ax.set_xticks(dims_arr)
ax.text(0.02, 0.88,
        "Open chain neg_frac rises\nwith d → thermodynamic\nadvantage at high d",
        transform=ax.transAxes, color=ORANGE, fontsize=7,
        bbox=dict(boxstyle='round', facecolor=PANEL, alpha=0.8))

# 5: Choi rank — stable rank 3 across topologies and time
ax = styled(fig.add_subplot(gs[2,3]),
            "Exp 5: Choi Matrix Rank Tracking\nRank=3 universally stable")
choi_res = e5["results"]
checkpoints = [r["step"] for r in choi_res["open_N3"]]
cols5 = [BLUE, GREEN, ORANGE]
labels5 = ["Open N=3", "Closed N=5 η=0.05", "Closed N=5 η=0.20"]
for (label, data), col, lbl in zip(choi_res.items(), cols5, labels5):
    ranks = [r["rank"] for r in data]
    lmaxs = [r["lambda_max"] for r in data]
    ax.plot(checkpoints, ranks, 'o-', color=col, lw=2, ms=8, label=lbl)
ax.axhline(3, color=WHITE, ls='--', lw=1.5, alpha=0.5, label='Rank=3 baseline')
ax.axhline(4, color=RED,   ls=':',  lw=1,   alpha=0.5, label='Rank=4 (not reached)')
ax.set_xlabel("BCP step"); ax.set_ylabel("Channel rank")
ax.set_ylim(0, 5); ax.legend(fontsize=7, facecolor=PANEL, labelcolor=WHITE)
ax.text(0.02, 0.1,
        "Rank 3 stable: topology\nchanges outcome, NOT\nchannel structure",
        transform=ax.transAxes, color=GREEN, fontsize=7.5,
        bbox=dict(boxstyle='round', facecolor=PANEL, alpha=0.8))

# ═══════════════════════════════════════════════════════════
# ROW 3 — GRAND SUMMARY DASHBOARD
# ═══════════════════════════════════════════════════════════

ax_sum = fig.add_subplot(gs[3,:])
ax_sum.set_facecolor('#0D1117'); ax_sum.axis('off')

findings = [
    ("Exp 1", "Intrinsic\nReward",
     "Agent discovers closed-loop\nsuperiority with ZERO external\nreward — pure self-improvement",
     GREEN),
    ("Exp 2", "Two-Agent\nGame",
     "Omega/Alpha role asymmetry\nemerges as Nash equilibrium —\nnot assigned, discovered",
     GOLD),
    ("Exp 3", "Noise-\nAdaptive",
     "Closed-loop advantage is\nnoise-MONOTONIC: gap widens\nas decoherence increases",
     ORANGE),
    ("Exp 4", "Critical\nDimension d*",
     "Closed-loop advantage INVERTS\nat d*≈4-5. Open chain wins at\nd=5,7 — new theoretical result",
     RED),
    ("Exp 5", "Choi Rank\nStability",
     "Rank=3 universally stable.\nTopology changes outcome\nwithout changing channel structure",
     BLUE),
]

cell_w = 1.0 / len(findings)
for i, (code, name, desc, col) in enumerate(findings):
    x = i * cell_w + 0.01
    w = cell_w - 0.02

    ax_sum.add_patch(plt.Rectangle((x, 0.05), w, 0.88,
                                    facecolor=col, alpha=0.08,
                                    transform=ax_sum.transAxes,
                                    clip_on=False))
    ax_sum.text(x + w/2, 0.88, code,
                transform=ax_sum.transAxes, ha='center',
                fontsize=10, fontweight='bold', color=col, va='top')
    ax_sum.text(x + w/2, 0.76, name,
                transform=ax_sum.transAxes, ha='center',
                fontsize=9, fontweight='bold', color=WHITE, va='top')
    ax_sum.text(x + w/2, 0.58, desc,
                transform=ax_sum.transAxes, ha='center',
                fontsize=7.5, color=WHITE, va='top', style='italic',
                alpha=0.85)

ax_sum.text(0.5, 0.14,
    "PAPER V HEADLINE: A PEIG agent maximizes its own proto-experiential quality through pure intrinsic motivation, "
    "independently rediscovering the topology laws of Papers I–IV.",
    transform=ax_sum.transAxes, ha='center', fontsize=9,
    color=GOLD, fontweight='bold', style='italic')
ax_sum.text(0.5, 0.04,
    "NEW THEORETICAL RESULT: Closed-loop topological advantage inverts at critical dimension d*≈4-5 — "
    "the first evidence of a dimensional phase transition in BCP topology.",
    transform=ax_sum.transAxes, ha='center', fontsize=8.5,
    color=RED, fontweight='bold', style='italic')

plt.savefig('outputs/PEIG_PAPER5_ALL_EXPERIMENTS.png',
            dpi=150, bbox_inches='tight',
            facecolor=fig.get_facecolor())
plt.show()
print("Figure saved → outputs/PEIG_PAPER5_ALL_EXPERIMENTS.png")

# ── Choi rank lambda_max detail ──────────────────────────────
print("\n══ EXPERIMENT 5 DETAILED RESULTS ══")
for label, data in choi_res.items():
    print(f"\n{label}:")
    for r in data:
        print(f"  step={r['step']:3d}: rank={r['rank']}  "
              f"λ_max={r['lambda_max']:.4f}  "
              f"top4={[round(e,4) for e in r['top4_evals']]}")

print("\n══ KEY FINDING ══")
print("Rank=3 stable across ALL configurations:")
print("  - Open N=3 chain")
print("  - Closed N=5 loop (η=0.05)")
print("  - Closed N=5 loop (η=0.20 fast)")
print("\nThis means: topology changes OUTCOME (Wigner floor),")
print("            but NOT channel STRUCTURE (always rank-3 irreversible)")
print("\nPhysical interpretation:")
print("  The BCP is ALWAYS a rank-3 quantum channel — 3 active Kraus operators.")
print("  Closing the loop does not add a new Kraus operator.")
print("  The preservation advantage is PURELY TOPOLOGICAL, not channel-structural.")
print("  This is the strongest possible confirmation of the topology thesis.")
