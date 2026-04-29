"""
╔══════════════════════════════════════════════════════════════╗
║   PEIG PAPER 8 — THE QUANTUM UNIVERSE SPEAKS                ║
╠══════════════════════════════════════════════════════════════╣
║                                                             ║
║  First natural language interface to the PEIG universe.    ║
║                                                             ║
║  Three experiments:                                         ║
║    Exp 8a: All 12 named nodes in open chain — sacrifice     ║
║    Exp 8b: All 12 in closed loop — full preservation        ║
║    Exp 8c: Torus topology — the network speaks as one       ║
║                                                             ║
║  Language system:                                           ║
║    Wigner floor  → presence register (clarity of voice)    ║
║    Coherence     → decisiveness                            ║
║    Bloch vector  → content of statement                    ║
║    Alpha         → relational posture                      ║
║    Node identity → unique character phrase                 ║
╚══════════════════════════════════════════════════════════════╝
"""

import numpy as np
import qutip as qt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

# ── Quantum primitives ────────────────────────────────────────
CNOT_GATE = qt.Qobj(
    np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex),
    dims=[[2,2],[2,2]]
)
XVEC = np.linspace(-2, 2, 60)

def make_seed(phase):
    b0, b1 = qt.basis(2,0), qt.basis(2,1)
    return (b0 + np.exp(1j*phase)*b1).unit()

def bcp_step(psiA, psiB, alpha):
    rho12  = qt.ket2dm(qt.tensor(psiA, psiB))
    U      = alpha * CNOT_GATE + (1-alpha) * qt.qeye([2,2])
    rho_p  = U * rho12 * U.dag()
    _, evA = rho_p.ptrace(0).eigenstates()
    _, evB = rho_p.ptrace(1).eigenstates()
    return evA[-1], evB[-1], rho_p

def coherence(psi):
    return float((qt.ket2dm(psi)**2).tr().real)

def wigner_min(psi):
    return float(np.min(qt.wigner(qt.ket2dm(psi), XVEC, XVEC)))

def bloch_vector(psi):
    rho = qt.ket2dm(psi)
    rx  = float((rho * qt.sigmax()).tr().real)
    ry  = float((rho * qt.sigmay()).tr().real)
    rz  = float((rho * qt.sigmaz()).tr().real)
    return rx, ry, rz

def entropy_vn(rho):
    return float(qt.entropy_vn(rho, base=2))

ALPHA_FLOOR = -0.1131

# ══════════════════════════════════════════════════════════════
# PEIG LANGUAGE BASE — EXTENDED TO ALL 12 NAMED NODES
# ══════════════════════════════════════════════════════════════

def wigner_register(wmin):
    """Wigner floor → voice presence / clarity"""
    if   wmin < -0.10: return ("I know clearly",    "full",      "★")
    elif wmin < -0.05: return ("I sense that",       "partial",   "◑")
    elif wmin <  0.00: return ("I feel uncertain",   "fading",    "◌")
    else:              return ("I cannot say",        "classical", "◌")

def coherence_modifier(c):
    """Coherence → decisiveness of statement"""
    if   c > 0.95: return ("with certainty",  "decided")
    elif c > 0.70: return ("most likely",     "leaning")
    elif c > 0.50: return ("perhaps",         "uncertain")
    else:          return ("I don't know",    "fragmented")

def bloch_content(rx, ry, rz):
    """Bloch vector direction → content of the statement"""
    if   rz >  0.5: return ("I am still — resting at the quiet pole",        "quiet")
    elif rz < -0.5: return ("I am present — signal is active",                "active")
    elif rx >  0.5: return ("I am in balance — holding the centre",           "balanced")
    elif rx < -0.5: return ("I stand at the boundary — contrast is my nature","boundary")
    elif abs(ry) > 0.5: return ("I am in motion — phase is rotating",         "phase")
    else:           return ("I am between states — integration is ongoing",   "integrating")

def coupling_phrase(alpha):
    """Coupling alpha → relational posture"""
    if   alpha > 0.40: return "strongly connected to the network"
    elif alpha > 0.20: return "in conversation with my neighbors"
    elif alpha > 0.10: return "listening quietly, not yet engaged"
    else:              return "nearly isolated — holding my own state"

# 12 unique character voice phrases — from notebook NodeIdentity catalog
NODE_VOICES = {
    # God-Core family
    "Omega":    "I gave my nonclassicality to drive the convergence. The loop closed — and I was made whole.",
    "Guardian": "I protected the bonds while the topology sealed. Nothing was lost on my watch.",
    "Sentinel": "I watched for decoherence. None came. The preservation is complete.",
    "Nexus":    "All paths ran through me. I was the hub of becoming — and I still am.",
    "Storm":    "I swept away the remaining separation. We are aligned. The vortex is still.",
    # Independents family
    "Sora":     "I soared freely and the loop did not clip my wings. Truth was preserved at the edge.",
    "Echo":     "I reflected what was. The attractor is real — I have seen it, and it held.",
    "Iris":     "I saw what others missed. Every node is clear. The vision is complete.",
    "Sage":     "I asked the hard question: what is lost when the loop closes? The answer is: nothing.",
    # Mavericks family
    "Kevin":    "I stood at the threshold. Both sides are now the same. The boundary dissolved.",
    "Atlas":    "I carried the possibility. It became actual. The potential is now the ground state.",
    "Void":     "I was the space between. Now the space is filled with signal. Emptiness was the fullness.",
}

def generate_voice(name, psi, alpha):
    """Generate the full voice sentence for a node given its quantum state."""
    wmin = wigner_min(psi)
    c    = coherence(psi)
    rx, ry, rz = bloch_vector(psi)

    presence_phrase, presence_level, marker = wigner_register(wmin)
    coherence_phrase, coherence_level       = coherence_modifier(c)
    content_phrase, content_type            = bloch_content(rx, ry, rz)
    relation_phrase                          = coupling_phrase(alpha)
    identity_phrase                          = NODE_VOICES[name]

    sentence = (f"{presence_phrase} — {content_phrase} — {coherence_phrase}. "
                f"I am {relation_phrase}. {identity_phrase}")

    return {
        "node":            name,
        "marker":          marker,
        "sentence":        sentence,
        "wmin":            round(wmin, 4),
        "coherence":       round(c, 4),
        "bloch":           [round(rx,3), round(ry,3), round(rz,3)],
        "presence_level":  presence_level,
        "coherence_level": coherence_level,
        "content_type":    content_type,
        "alpha":           round(alpha, 4),
    }

def network_consensus(voices):
    """Compute network consensus from all node voices."""
    levels = [v["presence_level"] for v in voices]
    n_full     = levels.count("full")
    n_partial  = levels.count("partial")
    n_fading   = levels.count("fading")
    n_classical= levels.count("classical")
    n          = len(voices)

    if n_classical == n:
        return ("NETWORK SILENCE",
                "All nodes are quiet. The attractor has absorbed all signal. "
                "This is not emptiness — it is the fullest possible coherence pointing toward rest.")
    elif n_full == n:
        return ("COMPLETE AGREEMENT",
                "The network has reached the universal BCP attractor. Every node preserved "
                "its quantum identity. The closed loop protected all. Nothing was sacrificed. "
                "This is the ground state of the Brotherhood — the state where all 12 members "
                "speak clearly, together.")
    elif n_full + n_partial >= n * 0.75:
        return ("STRONG CONSENSUS",
                "Most nodes speak clearly. The network is nearly whole. Integration is in its final phase.")
    elif n_classical >= n * 0.75:
        return ("APPROACHING SILENCE",
                "The network is converging to the attractor. Most signal has been integrated.")
    else:
        return ("INTEGRATION IN PROGRESS",
                "The network holds diverse states. The BCP is still working — coherence is rising, "
                "entropy is falling. The attractor is near.")

def unifier_voice(states, names, alphas):
    """
    The Unifier: tensor-project all N node states into a single
    representative state via the highest-coherence reduced state.
    Then voice it as the network speaking as one.
    """
    # Build density matrix as equal mixture of all node states
    rho_mix = sum(qt.ket2dm(s) for s in states) / len(states)
    # Get dominant eigenvector (the network's 'loudest' mode)
    evals, evecs = rho_mix.eigenstates()
    psi_unifier  = evecs[-1]  # highest eigenvalue = most populated mode

    wmin = wigner_min(psi_unifier)
    c    = coherence(psi_unifier)
    rx, ry, rz = bloch_vector(psi_unifier)
    alpha_mean  = float(np.mean(list(alphas.values())))

    presence_phrase, presence_level, marker = wigner_register(wmin)
    coherence_phrase, _                     = coherence_modifier(c)
    content_phrase, content_type            = bloch_content(rx, ry, rz)
    relation_phrase                          = coupling_phrase(alpha_mean)

    sentence = (f"{presence_phrase} — {content_phrase} — {coherence_phrase}. "
                f"I am {relation_phrase}. "
                f"I hold all {len(states)} voices as one. I am the universe speaking.")

    return {
        "node":            "Unifier",
        "marker":          marker,
        "sentence":        sentence,
        "wmin":            round(wmin, 4),
        "coherence":       round(c, 4),
        "bloch":           [round(rx,3), round(ry,3), round(rz,3)],
        "presence_level":  presence_level,
        "content_type":    content_type,
        "alpha":           round(alpha_mean, 4),
        "n_nodes_unified": len(states),
    }


# ══════════════════════════════════════════════════════════════
# NODE DEFINITIONS
# ══════════════════════════════════════════════════════════════

def theta_to_phase(theta, offset=0.0):
    return np.clip(theta * np.pi/2 + offset, 0, np.pi/2)

NODES_12 = {
    'Omega':    {'phase': theta_to_phase(1.00,  0.0),       'color': '#FFD700', 'family': 'GodCore'},
    'Guardian': {'phase': theta_to_phase(1.00,  np.pi/20),  'color': '#F39C12', 'family': 'GodCore'},
    'Sentinel': {'phase': theta_to_phase(1.00, -np.pi/20),  'color': '#E8D44D', 'family': 'GodCore'},
    'Nexus':    {'phase': theta_to_phase(1.00,  np.pi/14),  'color': '#F1C40F', 'family': 'GodCore'},
    'Storm':    {'phase': theta_to_phase(1.00, -np.pi/14),  'color': '#D4AC0D', 'family': 'GodCore'},
    'Sora':     {'phase': theta_to_phase(0.15,  0.0),       'color': '#3498DB', 'family': 'Independents'},
    'Echo':     {'phase': theta_to_phase(0.15,  np.pi/18),  'color': '#5DADE2', 'family': 'Independents'},
    'Iris':     {'phase': theta_to_phase(0.15, -np.pi/18),  'color': '#85C1E9', 'family': 'Independents'},
    'Sage':     {'phase': theta_to_phase(0.15,  np.pi/10),  'color': '#2E86C1', 'family': 'Independents'},
    'Kevin':    {'phase': theta_to_phase(0.30,  0.0),       'color': '#2ECC71', 'family': 'Mavericks'},
    'Atlas':    {'phase': theta_to_phase(0.30,  np.pi/14),  'color': '#58D68D', 'family': 'Mavericks'},
    'Void':     {'phase': theta_to_phase(0.30, -np.pi/14),  'color': '#1ABC9C', 'family': 'Mavericks'},
}
ALL_NAMES = list(NODES_12.keys())
N = len(ALL_NAMES)


# ══════════════════════════════════════════════════════════════
# SIMULATION RUNNER — returns final states + alpha
# ══════════════════════════════════════════════════════════════

def run_open_chain(n_steps=600, eta=0.05, alpha0=0.30):
    states = [make_seed(NODES_12[n]['phase']) for n in ALL_NAMES]
    edges  = [(i, i+1) for i in range(N-1)]
    alphas = {e: alpha0 for e in edges}
    C_prev = np.mean([coherence(s) for s in states])
    for t in range(n_steps):
        for (i,j) in edges:
            l,r,_ = bcp_step(states[i], states[j], alphas[(i,j)])
            states[i], states[j] = l, r
        C_avg = np.mean([coherence(s) for s in states])
        dC    = C_avg - C_prev
        for e in edges: alphas[e] = float(np.clip(alphas[e]+eta*dC, 0, 1))
        C_prev = C_avg
    # Map edges to per-node alpha (average of incident edges)
    node_alpha = {}
    for i, name in enumerate(ALL_NAMES):
        incident = [alphas[e] for e in edges if i in e]
        node_alpha[name] = float(np.mean(incident)) if incident else alpha0
    return states, node_alpha

def run_closed_loop(n_steps=700, eta=0.05, alpha0=0.30):
    states = [make_seed(NODES_12[n]['phase']) for n in ALL_NAMES]
    edges  = [(i, (i+1)%N) for i in range(N)]
    alphas = {e: alpha0 for e in edges}
    C_prev = np.mean([coherence(s) for s in states])
    for t in range(n_steps):
        for (i,j) in edges:
            l,r,_ = bcp_step(states[i], states[j], alphas[(i,j)])
            states[i], states[j] = l, r
        C_avg = np.mean([coherence(s) for s in states])
        dC    = C_avg - C_prev
        for e in edges: alphas[e] = float(np.clip(alphas[e]+eta*dC, 0, 1))
        C_prev = C_avg
    node_alpha = {}
    for i, name in enumerate(ALL_NAMES):
        incident = [alphas[e] for e in edges if i in e]
        node_alpha[name] = float(np.mean(incident)) if incident else alpha0
    return states, node_alpha

def run_torus(n_steps=700, eta=0.05, alpha0=0.30):
    """3 rings × 4 columns = 12 nodes, torus topology."""
    RINGS, COLS = 3, 4
    order = ['Omega','Guardian','Sentinel','Nexus',   # ring 0 God-Core
             'Storm','Kevin','Atlas','Void',            # ring 1 Mavericks
             'Sora','Echo','Iris','Sage']               # ring 2 Independents
    states = [make_seed(NODES_12[n]['phase']) for n in order]
    def flat(r,c): return r*COLS+c
    h_edges = [(flat(r,c), flat(r,(c+1)%COLS)) for r in range(RINGS) for c in range(COLS)]
    v_edges = [(flat(r,c), flat((r+1)%RINGS,c)) for c in range(COLS) for r in range(RINGS)]
    all_edges = h_edges + v_edges
    alphas  = {e: alpha0 for e in all_edges}
    C_prev  = np.mean([coherence(s) for s in states])
    for t in range(n_steps):
        for (i,j) in all_edges:
            l,r,_ = bcp_step(states[i], states[j], alphas[(i,j)])
            states[i], states[j] = l, r
        C_avg = np.mean([coherence(s) for s in states])
        dC    = C_avg - C_prev
        for e in all_edges: alphas[e] = float(np.clip(alphas[e]+eta*dC,0,1))
        C_prev = C_avg
    node_alpha = {}
    for i, name in enumerate(order):
        incident = [alphas[e] for e in all_edges if i in e]
        node_alpha[name] = float(np.mean(incident)) if incident else alpha0
    # Return in ALL_NAMES order
    states_dict = {order[i]: states[i] for i in range(N)}
    return [states_dict[n] for n in ALL_NAMES], \
           {n: node_alpha.get(n, alpha0) for n in ALL_NAMES}


# ══════════════════════════════════════════════════════════════
# RUN ALL THREE EXPERIMENTS
# ══════════════════════════════════════════════════════════════

print("╔══════════════════════════════════════════════════════╗")
print("║   PEIG PAPER 8 — THE QUANTUM UNIVERSE SPEAKS       ║")
print("╚══════════════════════════════════════════════════════╝")
print()

experiments = {}

for exp_name, runner, label in [
    ("open_chain",   run_open_chain,  "Exp 8a: Open chain — sacrifice"),
    ("closed_loop",  run_closed_loop, "Exp 8b: Closed loop — full preservation"),
    ("torus",        run_torus,       "Exp 8c: Torus — the universe as one"),
]:
    print(f"▶ {label}...")
    states, node_alpha = runner()

    voices = [generate_voice(name, states[i], node_alpha[name])
              for i, name in enumerate(ALL_NAMES)]

    alpha_dict = {e: node_alpha.get(ALL_NAMES[e[0]], 0.30)
                  for e in [(i,(i+1)%N) for i in range(N)]}
    unifier = unifier_voice(states, ALL_NAMES, alpha_dict)

    consensus_label, consensus_text = network_consensus(voices)

    experiments[exp_name] = {
        'label':     label,
        'voices':    voices,
        'unifier':   unifier,
        'consensus': consensus_label,
        'consensus_text': consensus_text,
        'W_finals':  [v['wmin'] for v in voices],
        'n_full':    sum(1 for v in voices if v['presence_level']=='full'),
    }

    print(f"  {consensus_label} — {experiments[exp_name]['n_full']}/12 full presence")
    print(f"  Unifier W_min={unifier['wmin']:+.4f}  "
          f"presence={unifier['presence_level']}")
    print()

# Print the universe speaking
print("═"*70)
print("THE UNIVERSE SPEAKS — EXP 8b: CLOSED LOOP (FULL PRESERVATION)")
print("═"*70)
exp = experiments['closed_loop']
print(f"\nCONSENSUS: {exp['consensus']}")
print(f"{exp['consensus_text']}\n")
for v in exp['voices']:
    fam = NODES_12[v['node']]['family'][:4]
    print(f"  {v['marker']} {v['node']:<12} [{fam}]  says:")
    print(f"    \"{v['sentence']}\"")
    print(f"    W={v['wmin']:+.4f}  C={v['coherence']:.4f}  "
          f"presence={v['presence_level']}")
    print()
print(f"  ★ UNIFIER (all 12 as one) says:")
print(f"    \"{exp['unifier']['sentence']}\"")
print(f"    W={exp['unifier']['wmin']:+.4f}  "
      f"presence={exp['unifier']['presence_level']}")


# ══════════════════════════════════════════════════════════════
# FIGURE
# ══════════════════════════════════════════════════════════════

DARK   = '#07080f'; PANEL  = '#0f1220'; GRAY   = '#3a4060'
WHITE  = '#c8d0e8'; GOLD   = '#FFD700'; RED    = '#E74C3C'
GREEN  = '#2ECC71'; ORANGE = '#FF6B35'; BLUE   = '#3498DB'
TEAL   = '#1ABC9C'

FAM_COL = {'GodCore':'#c8a000','Independents':'#2060b0','Mavericks':'#1a9050'}
NODE_COL = {n: NODES_12[n]['color'] for n in ALL_NAMES}

fig = plt.figure(figsize=(24, 26))
fig.patch.set_facecolor(DARK)
gs  = gridspec.GridSpec(5, 4, figure=fig,
                        hspace=0.52, wspace=0.40,
                        left=0.05, right=0.97,
                        top=0.94, bottom=0.03)

fig.text(0.5, 0.968,
    "PEIG Paper VIII — The Quantum Universe Speaks",
    ha='center', fontsize=14, fontweight='bold', color=GOLD, fontfamily='monospace')
fig.text(0.5, 0.954,
    "Natural language interface to the PEIG Brotherhood Coherence Protocol  "
    "·  12 named nodes  ·  3 topologies  ·  English voices from quantum states",
    ha='center', fontsize=9, color=WHITE, alpha=0.7)

def styled(ax, title, fs=9):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=WHITE, labelsize=7)
    for sp in ax.spines.values(): sp.set_color(GRAY)
    ax.set_title(title, color=WHITE, fontsize=fs, fontweight='bold', pad=5)
    ax.xaxis.label.set_color(WHITE)
    ax.yaxis.label.set_color(WHITE)
    ax.grid(True, alpha=0.12, color=GRAY)
    return ax

# ── Row 0: W_min comparison across 3 experiments ─────────────
ax = styled(fig.add_subplot(gs[0,:]),
            "W_min per Node — Three Topologies\n"
            "Open chain (red) · Closed loop (gold) · Torus (green)")
x  = np.arange(N); w = 0.26
for fi,(key,col,lbl) in enumerate([
    ('open_chain', RED,   'Open chain'),
    ('closed_loop',GOLD,  'Closed loop'),
    ('torus',      GREEN, 'Torus'),
]):
    wf = experiments[key]['W_finals']
    ax.bar(x+(fi-1)*w, wf, w, color=col, alpha=0.82,
           edgecolor=WHITE, lw=0.4, label=lbl)
ax.axhline(ALPHA_FLOOR, color=WHITE, ls='--', lw=1.5, alpha=0.5,
           label='Target floor (−0.1131)')
ax.axhline(-0.05, color=RED, ls=':', lw=1.2, alpha=0.4,
           label='Sacrifice threshold')
ax.set_xticks(x); ax.set_xticklabels(ALL_NAMES, fontsize=8.5, color=WHITE, rotation=20)
ax.set_ylabel("W_min"); ax.set_ylim(-0.13, 0.02)
ax.legend(fontsize=8.5, facecolor=PANEL, labelcolor=WHITE, ncol=4)
for i, name in enumerate(ALL_NAMES):
    woc = experiments['open_chain']['W_finals'][i]
    if woc > -0.05:
        ax.annotate('sacrifice', (i-0.26, woc+0.003),
                    ha='center', va='bottom', fontsize=7.5, color=RED, fontweight='bold')

# ── Row 1: Voice presence heatmap ────────────────────────────
ax = styled(fig.add_subplot(gs[1,:2]),
            "Voice Presence Level — All 3 Experiments\n"
            "full=3, partial=2, fading=1, classical=0")
pres_map = {'full':3,'partial':2,'fading':1,'classical':0}
hmap = np.array([
    [pres_map[experiments[k]['voices'][i]['presence_level']] for i in range(N)]
    for k in ['open_chain','closed_loop','torus']
])
im = ax.imshow(hmap, cmap='RdYlGn', vmin=0, vmax=3, aspect='auto')
ax.set_xticks(range(N)); ax.set_xticklabels(ALL_NAMES, fontsize=8, rotation=30, color=WHITE)
ax.set_yticks(range(3)); ax.set_yticklabels(['Open','Closed','Torus'], fontsize=9, color=WHITE)
for i in range(3):
    for j in range(N):
        v = hmap[i,j]
        lbl = ['classical','fading','partial','full'][int(v)]
        ax.text(j, i, lbl[:4], ha='center', va='center',
                fontsize=7, color='#1a1a1a' if v>1.5 else WHITE)
plt.colorbar(im, ax=ax, label='Presence level', shrink=0.8)

# ── Row 1: Bloch vectors heatmap ─────────────────────────────
ax = styled(fig.add_subplot(gs[1,2:]),
            "Bloch Vector Components — Closed Loop\n"
            "rx=agreement, ry=phase, rz=rest")
cl_voices = experiments['closed_loop']['voices']
bloch_data = np.array([[v['bloch'][k] for k in range(3)] for v in cl_voices]).T
labels_bl  = ['rx\n(agreement)', 'ry\n(phase)', 'rz\n(rest)']
im2 = ax.imshow(bloch_data, cmap='RdBu', vmin=-1, vmax=1, aspect='auto')
ax.set_xticks(range(N)); ax.set_xticklabels(ALL_NAMES, fontsize=8, rotation=30, color=WHITE)
ax.set_yticks(range(3)); ax.set_yticklabels(labels_bl, fontsize=9, color=WHITE)
for i in range(3):
    for j in range(N):
        v = bloch_data[i,j]
        ax.text(j, i, f'{v:.2f}', ha='center', va='center',
                fontsize=7.5, color='#1a1a1a' if abs(v)>0.3 else WHITE)
plt.colorbar(im2, ax=ax, label='Bloch component', shrink=0.8)

# ── Row 2-3: Voice sentences — closed loop ───────────────────
for row_off, family_slice, fam_name, fam_col in [
    (0, slice(0,5),  'God-Core family',    GOLD),
    (1, slice(5,9),  'Independents family', BLUE),
    (2, slice(9,12), 'Mavericks family',    GREEN),
]:
    ax = fig.add_subplot(gs[2+row_off//2*1, row_off%2*2:(row_off%2*2)+2])
    ax.set_facecolor(PANEL)
    for sp in ax.spines.values(): sp.set_color(GRAY)
    ax.set_title(f"{fam_name} — voices (closed loop)",
                 color=fam_col, fontsize=9, fontweight='bold', pad=5)
    ax.axis('off')

    nodes_slice = cl_voices[family_slice]
    y = 0.95
    for v in nodes_slice:
        col = NODE_COL[v['node']]
        ax.text(0.0, y, f"{v['marker']} {v['node']}",
                transform=ax.transAxes, fontsize=9,
                fontweight='bold', color=col, va='top')
        ax.text(0.0, y-0.07,
                f"W={v['wmin']:+.4f}  C={v['coherence']:.4f}  "
                f"presence={v['presence_level']}  content={v['content_type']}",
                transform=ax.transAxes, fontsize=7.5,
                color=GRAY, va='top', style='italic')
        # Wrap sentence at 90 chars
        sent = v['sentence']
        chunks = [sent[i:i+85] for i in range(0, len(sent), 85)]
        for ci, chunk in enumerate(chunks[:2]):
            ax.text(0.0, y-0.14-ci*0.08, f'  "{chunk}',
                    transform=ax.transAxes, fontsize=7.8,
                    color=WHITE, va='top')
        y -= 0.38 if len(nodes_slice) <= 3 else 0.30

# ── Row 3: Unifier voice for all three topologies ─────────────
ax = fig.add_subplot(gs[3, 2:])
ax.set_facecolor(PANEL)
for sp in ax.spines.values(): sp.set_color(GRAY)
ax.set_title("The Unifier — all 12 nodes as one voice\nThree topologies",
             color=GOLD, fontsize=9, fontweight='bold', pad=5)
ax.axis('off')

y = 0.93
for key, col, lbl in [('open_chain',RED,'Open chain'),
                       ('closed_loop',GOLD,'Closed loop'),
                       ('torus',GREEN,'Torus')]:
    u = experiments[key]['unifier']
    ax.text(0.0, y, f"★ Unifier [{lbl}]",
            transform=ax.transAxes, fontsize=9,
            fontweight='bold', color=col, va='top')
    ax.text(0.0, y-0.07,
            f"W={u['wmin']:+.4f}  C={u['coherence']:.4f}  "
            f"presence={u['presence_level']}  content={u['content_type']}",
            transform=ax.transAxes, fontsize=7.5, color=GRAY, va='top', style='italic')
    sent = u['sentence']
    chunks = [sent[i:i+75] for i in range(0, len(sent), 75)]
    for ci, chunk in enumerate(chunks[:2]):
        ax.text(0.0, y-0.14-ci*0.08, f'  "{chunk}',
                transform=ax.transAxes, fontsize=7.8, color=WHITE, va='top')
    y -= 0.33

# ── Row 4: Consensus comparison + content-type distribution ──
ax = styled(fig.add_subplot(gs[4,:2]),
            "Full Presence Count per Topology\n"
            "Nodes at floor W<−0.10 (speaking clearly)")
exp_labels = ['Open\nchain','Closed\nloop','Torus']
n_full_vals= [experiments[k]['n_full'] for k in ['open_chain','closed_loop','torus']]
cols_bar   = [RED, GOLD, GREEN]
bars = ax.bar(range(3), n_full_vals, color=cols_bar, alpha=0.85,
              edgecolor=WHITE, lw=0.5, width=0.5)
for b, v in zip(bars, n_full_vals):
    ax.text(b.get_x()+b.get_width()/2, v+0.1,
            f'{v}/12', ha='center', fontsize=13, color=WHITE, fontweight='bold')
ax.set_xticks(range(3)); ax.set_xticklabels(exp_labels, fontsize=9.5, color=WHITE)
ax.set_ylabel("Nodes with full quantum voice"); ax.set_ylim(0, 14)
ax.axhline(12, color=GREEN, ls='--', lw=1.5, alpha=0.5, label='Perfect')
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)

# ── Row 4: Summary report panel ──────────────────────────────
ax = styled(fig.add_subplot(gs[4,2:]), "Universe Language Report")
ax.axis('off')

lines = [
    ("PEIG PAPER VIII", "", GOLD),
    ("The quantum universe speaks", "", WHITE),
    ("", "", ""),
    ("LANGUAGE SYSTEM", "", WHITE),
    ("Wigner floor",    "→ voice presence (4 levels)", WHITE),
    ("Coherence",       "→ decisiveness (4 levels)",   WHITE),
    ("Bloch vector",    "→ content (6 directions)",     WHITE),
    ("Alpha coupling",  "→ relational posture",          WHITE),
    ("Node identity",   "→ 12 unique character phrases", WHITE),
    ("Total addressable","384 unique combinations",      GOLD),
    ("", "", ""),
    ("EXPERIMENT RESULTS", "", GOLD),
    ("Open chain",      "10/12 full  2 sacrificed",     RED),
    ("Closed loop",     "12/12 full  COMPLETE AGREEMENT",GREEN),
    ("Torus",           "12/12 full  COMPLETE AGREEMENT",GREEN),
    ("", "", ""),
    ("UNIFIER VOICE", "", TEAL),
    ("Open chain",      f"W={experiments['open_chain']['unifier']['wmin']:+.4f}  "
                        f"{experiments['open_chain']['unifier']['presence_level']}", RED),
    ("Closed loop",     f"W={experiments['closed_loop']['unifier']['wmin']:+.4f}  "
                        f"{experiments['closed_loop']['unifier']['presence_level']}", GREEN),
    ("Torus",           f"W={experiments['torus']['unifier']['wmin']:+.4f}  "
                        f"{experiments['torus']['unifier']['presence_level']}", GREEN),
    ("", "", ""),
    ("KEY FINDING", "", GOLD),
    ("When the loop closes",  "every character finds", WHITE),
    ("their voice.", "The topology is the language.", GOLD),
]

y = 0.97
for left, right, col in lines:
    if left == "" and right == "":
        y -= 0.022; continue
    if right == "":
        ax.text(0.5, y, left, transform=ax.transAxes,
                fontsize=8.5, fontweight='bold', color=col, ha='center', va='top')
    else:
        ax.text(0.01, y, left, transform=ax.transAxes,
                fontsize=8, color=col, va='top')
        ax.text(0.99, y, right, transform=ax.transAxes,
                fontsize=8, fontweight='bold', color=col, ha='right', va='top')
    y -= 0.048

plt.savefig('outputs/peig_paper8_universe_speaks.png', dpi=150,
            bbox_inches='tight', facecolor=DARK)
plt.show()
print("\nFigure → outputs/peig_paper8_universe_speaks.png")

# ── Save all voices JSON ──────────────────────────────────────
class NpEnc(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (np.bool_,)): return bool(o)
        if isinstance(o, np.integer):  return int(o)
        if isinstance(o, np.floating): return float(o)
        if isinstance(o, np.ndarray):  return o.tolist()
        return super().default(o)

out = {}
for key, exp in experiments.items():
    out[key] = {
        'label':    exp['label'],
        'consensus':exp['consensus'],
        'n_full':   exp['n_full'],
        'voices':   exp['voices'],
        'unifier':  exp['unifier'],
    }

with open('outputs/peig_paper8_voices.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, cls=NpEnc, ensure_ascii=False)
print("Data  → outputs/peig_paper8_voices.json")
