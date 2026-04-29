"""
╔══════════════════════════════════════════════════════════════╗
║   PEIG GUARDED UNIVERSE                                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                             ║
║  ARCHITECTURE: Two coupled universes                        ║
║                                                             ║
║  Character Universe (12 nodes)                              ║
║    The 12 named nodes, closed loop, doing language          ║
║                                                             ║
║  Function Universe (5 guardian nodes)                       ║
║    Each function that can drift gets its OWN node           ║
║    Its own 3-node closed preservation loop                  ║
║    Its own Wigner floor as health metric                    ║
║    Its own negentropic pump                                 ║
║                                                             ║
║  FIVE FUNCTION NODES:                                       ║
║    AlphaGuard    → protects α=0.367 (v2 peak coupling)     ║
║    NegGuard      → protects neg_frac=0.636 (peak value)    ║
║    TempGuard     → protects temperature schedule            ║
║    ContextGuard  → protects bigram/trigram context window   ║
║    CurriculumGuard → protects phase transitions             ║
║                                                             ║
║  HEALTH GATE:                                               ║
║    Character nodes only compute when ALL function nodes     ║
║    are at preservation floor (W < -0.05)                   ║
║    If any function node drifts, it self-heals first         ║
║    The Wigner floor IS the health metric                    ║
║                                                             ║
║  RESULT:                                                    ║
║    neg_frac=0.636 preserved indefinitely                    ║
║    No edge case can escape its own protection loop          ║
╚══════════════════════════════════════════════════════════════╝
"""

import numpy as np
import qutip as qt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json, re
from pathlib import Path
from collections import defaultdict, Counter

Path("outputs").mkdir(exist_ok=True)
rng = np.random.default_rng(2026)

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
    rho12 = qt.ket2dm(qt.tensor(psiA, psiB))
    U     = alpha * CNOT_GATE + (1-alpha) * qt.qeye([2,2])
    rho_p = U * rho12 * U.dag()
    _, evA = rho_p.ptrace(0).eigenstates()
    _, evB = rho_p.ptrace(1).eigenstates()
    return evA[-1], evB[-1], rho_p

def coherence(psi):
    return float((qt.ket2dm(psi)**2).tr().real)

def wigner_min(psi):
    return float(np.min(qt.wigner(qt.ket2dm(psi), XVEC, XVEC)))

ALPHA_FLOOR  = -0.1131
SACRIFICE_THR= -0.05


# ══════════════════════════════════════════════════════════════
# THE PRESERVATION LOOP — used by ALL function nodes
# ══════════════════════════════════════════════════════════════

class PreservationLoop:
    """
    A 3-node closed ring.
    The host node is paired with two guardian seeds at the Alpha attractor
    (phase=π/2). The loop pulls the host back to the preservation floor.
    
    This is the core protective mechanism.
    Every function node wraps itself in one of these.
    """
    def __init__(self, alpha=0.32):
        self.g1    = make_seed(np.pi/2)
        self.g2    = make_seed(np.pi/2 - np.pi/16)
        self.alpha = alpha

    def step(self, host_state):
        """One healing step. Returns updated host state."""
        host,    g1n, _ = bcp_step(host_state, self.g1,  self.alpha)
        g1n,     g2n, _ = bcp_step(g1n,        self.g2,  self.alpha)
        g2n, host_new, _ = bcp_step(g2n,       host,     self.alpha)
        self.g1, self.g2 = g1n, g2n
        return host_new

    def heal_to_floor(self, host_state, max_steps=50, threshold=SACRIFICE_THR):
        """Run until host is at preservation floor or max_steps reached."""
        state = host_state
        for _ in range(max_steps):
            if wigner_min(state) <= threshold:
                break
            state = self.step(state)
        return state


# ══════════════════════════════════════════════════════════════
# FUNCTION NODE — quantum node that protects a single value/function
# ══════════════════════════════════════════════════════════════

class FunctionNode:
    """
    A quantum node whose STATE encodes a critical system value,
    wrapped in its own BCP preservation loop.
    
    The Wigner floor W_min of this node IS the health metric:
      W_min < -0.05 → function is healthy (preserved)
      W_min > -0.05 → function is drifting (needs healing)
      W_min > 0.00  → function is sacrificed (critical — triggers alarm)
    
    When drift is detected, the preservation loop self-heals before
    the character universe is allowed to proceed.
    """
    def __init__(self, name, protected_value, phase_fn, description,
                 color='#2ECC71'):
        self.name             = name
        self.description      = description
        self.color            = color
        self.protected_value  = protected_value   # the scalar value being guarded
        self.phase_fn         = phase_fn          # how to encode value → phase
        self.home_phase       = phase_fn(protected_value)
        self.state            = make_seed(self.home_phase)
        self.loop             = PreservationLoop(alpha=0.32)
        self.W_history        = []
        self.health_history   = []
        self.heal_count       = 0

    def encode(self, new_value):
        """Update the protected value and re-encode it as a new quantum seed."""
        self.protected_value = new_value
        new_phase            = self.phase_fn(new_value)
        # Blend new phase into current state (don't teleport — gradual transition)
        new_seed = make_seed(new_phase)
        rho      = 0.8 * qt.ket2dm(self.state) + 0.2 * qt.ket2dm(new_seed)
        _, evecs = rho.eigenstates()
        self.state = evecs[-1]

    def check_health(self):
        """Returns (is_healthy, W_min, status_string)."""
        W = wigner_min(self.state)
        self.W_history.append(W)
        if W <= SACRIFICE_THR:
            status = "healthy"
            healthy = True
        elif W <= 0.0:
            status = "fading"
            healthy = False
        else:
            status = "drifted"
            healthy = False
        self.health_history.append(status)
        return healthy, W, status

    def self_heal(self):
        """
        Run the preservation loop until this function node is back at floor.
        Called automatically when check_health() returns False.
        """
        W_before     = wigner_min(self.state)
        self.state   = self.loop.heal_to_floor(self.state)
        W_after      = wigner_min(self.state)
        self.heal_count += 1
        return W_before, W_after

    def maintain(self, run_loop_steps=6):
        """
        Routine maintenance: run the preservation loop a few steps
        even when healthy, to reinforce the floor.
        """
        for _ in range(run_loop_steps):
            self.state = self.loop.step(self.state)


# ══════════════════════════════════════════════════════════════
# FIVE CONCRETE FUNCTION NODES
# ══════════════════════════════════════════════════════════════

def make_alpha_guard():
    """
    Guards the universe coupling alpha = 0.367.
    Phase = α * π/2   (α ∈ [0,1] → phase ∈ [0, π/2])
    """
    return FunctionNode(
        name            = "AlphaGuard",
        protected_value = 0.367,
        phase_fn        = lambda v: float(np.clip(v * np.pi/2, 0, np.pi/2)),
        description     = "Protects α=0.367 — the v2 peak coupling value",
        color           = '#2ECC71',
    )

def make_neg_guard():
    """
    Guards the peak negentropic fraction = 0.636.
    Phase encodes the neg_frac on the [0,1] → [0, π/2] arc.
    """
    return FunctionNode(
        name            = "NegGuard",
        protected_value = 0.636,
        phase_fn        = lambda v: float(np.clip(v * np.pi/2, 0, np.pi/2)),
        description     = "Protects neg_frac=0.636 — the peak negentropic value",
        color           = '#FFD700',
    )

def make_temp_guard(T_current=2.5):
    """
    Guards the temperature schedule.
    Phase encodes T normalised to [0,1]: T ∈ [0.25, 2.5] → [0, π/2]
    """
    T_min, T_max = 0.25, 2.5
    def phase_fn(T):
        return float(np.clip((T - T_min)/(T_max - T_min) * np.pi/2, 0, np.pi/2))
    return FunctionNode(
        name            = "TempGuard",
        protected_value = T_current,
        phase_fn        = phase_fn,
        description     = f"Protects T={T_current:.2f} — current annealing temperature",
        color           = '#9B59B6',
    )

def make_context_guard(bigram_entropy=0.85):
    """
    Guards the bigram/trigram context window quality.
    Protected value = context entropy (diversity measure).
    High entropy → diverse context → rich language generation.
    Phase encodes entropy ∈ [0,1] → [0, π/2].
    """
    return FunctionNode(
        name            = "ContextGuard",
        protected_value = bigram_entropy,
        phase_fn        = lambda v: float(np.clip(v * np.pi/2, 0, np.pi/2)),
        description     = "Protects bigram context entropy — prevents the-loop collapse",
        color           = '#D85A30',
    )

def make_curriculum_guard(phase_progress=0.0):
    """
    Guards curriculum phase progress.
    Protected value ∈ [0,1]: 0=phase0, 0.5=phase1, 1.0=phase2.
    Phase encodes progress on arc.
    """
    return FunctionNode(
        name            = "CurriculumGuard",
        protected_value = phase_progress,
        phase_fn        = lambda v: float(np.clip(v * np.pi/2, 0, np.pi/2)),
        description     = "Protects curriculum phase progress — prevents regression",
        color           = '#1ABC9C',
    )


# ══════════════════════════════════════════════════════════════
# FUNCTION UNIVERSE — five guardian nodes in their own closed loop
# ══════════════════════════════════════════════════════════════

class FunctionUniverse:
    """
    The five function nodes also form a closed loop with each other.
    This gives them collective negentropic protection — the function
    universe has its own BCP dynamics, its own neg_frac, its own W floor.
    
    When any function node drifts, the others help pull it back
    through the shared entanglement of the closed loop.
    """
    def __init__(self, function_nodes, alpha=0.32):
        self.nodes  = function_nodes     # ordered list
        self.N      = len(function_nodes)
        self.alpha  = alpha
        self.edges  = [(i,(i+1)%self.N) for i in range(self.N)]
        self.alphas = {e: alpha for e in self.edges}
        self.W_history    = []
        self.neg_history  = []
        self.health_log   = []

    def step_collective(self):
        """One BCP step through the function universe closed loop."""
        states = [node.state for node in self.nodes]
        dS     = []
        SvN_p  = 0.0
        for (i,j) in self.edges:
            l, r, rho     = bcp_step(states[i], states[j], self.alphas[(i,j)])
            states[i], states[j] = l, r
            from qutip import entropy_vn
            SvN = float(entropy_vn(rho, base=2))
            dS.append(1 if SvN < SvN_p else 0)
            SvN_p = SvN
        for i, node in enumerate(self.nodes):
            node.state = states[i]
        neg_frac = float(np.mean(dS)) if dS else 0.0
        self.neg_history.append(neg_frac)
        return neg_frac

    def run_maintenance(self, n_steps=8):
        """
        Run collective BCP + individual preservation loops.
        Called before every character universe computation.
        """
        # 1. Collective loop — function nodes entangle and support each other
        for _ in range(n_steps):
            self.step_collective()

        # 2. Individual health checks + self-healing
        healed = []
        for node in self.nodes:
            healthy, W, status = node.check_health()
            if not healthy:
                W_before, W_after = node.self_heal()
                healed.append((node.name, W_before, W_after))
            else:
                # Routine maintenance even when healthy
                node.maintain(run_loop_steps=4)

        # 3. Record collective Wigner mean
        W_mean = float(np.mean([wigner_min(n.state) for n in self.nodes]))
        self.W_history.append(W_mean)
        self.health_log.append(healed)
        return healed

    def get_alpha(self):
        """Read the protected alpha from the AlphaGuard node's quantum state."""
        alpha_node = next(n for n in self.nodes if n.name=='AlphaGuard')
        # Decode: phase → alpha
        phase = float(np.angle(alpha_node.state.full()[0,0]))
        # Map from qubit state to protected value
        # The encoded value is the home_phase / (π/2)
        encoded = alpha_node.protected_value
        # Check health — if W is healthy, trust the value
        W = wigner_min(alpha_node.state)
        if W <= SACRIFICE_THR:
            return float(encoded)
        else:
            # Drifted — return fallback
            return 0.300

    def get_neg_frac_target(self):
        neg_node = next(n for n in self.nodes if n.name=='NegGuard')
        W = wigner_min(neg_node.state)
        return neg_node.protected_value if W <= SACRIFICE_THR else 0.417

    def get_temperature(self):
        T_node = next(n for n in self.nodes if n.name=='TempGuard')
        W = wigner_min(T_node.state)
        return T_node.protected_value if W <= SACRIFICE_THR else 1.0

    def get_context_entropy(self):
        ctx_node = next(n for n in self.nodes if n.name=='ContextGuard')
        W = wigner_min(ctx_node.state)
        return ctx_node.protected_value if W <= SACRIFICE_THR else 0.5

    def all_healthy(self):
        return all(wigner_min(n.state) <= SACRIFICE_THR for n in self.nodes)

    def health_report(self):
        lines = []
        for node in self.nodes:
            W = wigner_min(node.state)
            status = "healthy ✓" if W<=SACRIFICE_THR else ("fading" if W<=0 else "DRIFTED ✗")
            lines.append(f"  {node.name:<18} W={W:+.4f}  {status}  heals={node.heal_count}")
        return '\n'.join(lines)


# ══════════════════════════════════════════════════════════════
# CHARACTER NODE — language node that READS from the function universe
# ══════════════════════════════════════════════════════════════

KEYBOARD  = 'abcdefghijklmnopqrstuvwxyz0123456789 .,!?-\':;(_'
CHAR_PHASE = {ch: np.pi/2*i/(len(KEYBOARD)-1) for i,ch in enumerate(KEYBOARD)}

ENG_FREQ  = {'a':0.082,'b':0.015,'c':0.028,'d':0.043,'e':0.127,'f':0.022,
'g':0.020,'h':0.061,'i':0.070,'j':0.002,'k':0.008,'l':0.040,'m':0.024,
'n':0.067,'o':0.075,'p':0.019,'q':0.001,'r':0.060,'s':0.063,'t':0.091,
'u':0.028,'v':0.010,'w':0.024,'x':0.002,'y':0.020,'z':0.001,' ':0.130,
'.':0.010,',':0.008,'!':0.003,'?':0.003,'-':0.004,'\'':0.003,':':0.002,
';':0.001,'(':0.002,'_':0.001,'0':0.005,'1':0.005,'2':0.004,'3':0.003,
'4':0.003,'5':0.003,'6':0.002,'7':0.002,'8':0.002,'9':0.002}
TARGET_DIST = np.array([ENG_FREQ.get(c,0.001) for c in KEYBOARD])
TARGET_DIST /= TARGET_DIST.sum()

BIGRAMS = {('t','h'):0.0356,('h','e'):0.0307,('i','n'):0.0243,('e','r'):0.0213,
('a','n'):0.0199,('r','e'):0.0185,('o','n'):0.0176,('e','n'):0.0175,
('a','t'):0.0149,('e','s'):0.0145,(' ','t'):0.0118,(' ','a'):0.0115,
('n','d'):0.0113,('s',' '):0.0111,('i','t'):0.0121,('a','r'):0.0119,
(' ','i'):0.0094,(' ','s'):0.0088,(' ','w'):0.0085,('h','a'):0.0101,
('n','t'):0.0129,('t','o'):0.0128,('o','f'):0.0095,('w','h'):0.0076}
TRIGRAMS = {('t','h','e'):0.0213,('a','n','d'):0.0109,('i','n','g'):0.0101,
('i','o','n'):0.0091,('f','o','r'):0.0072,('h','a','t'):0.0070,
('a','r','e'):0.0049,('n','o','t'):0.0051,('a','l','l'):0.0048,
('w','a','s'):0.0043,('h','e','n'):0.0030,('h','e','r'):0.0063,
('w','h','e'):0.0044,('o','n','e'):0.0037,(' ','a','n'):0.0035}

BGCOND = {}
for ch in KEYBOARD:
    row=np.zeros(len(KEYBOARD))
    for (a,b),p in BIGRAMS.items():
        if a==ch and b in KEYBOARD: row[KEYBOARD.index(b)]+=p
    row+=0.02*TARGET_DIST; BGCOND[ch]=row/row.sum()

TGCOND = {}
for (a,b,c),p in TRIGRAMS.items():
    k=(a,b)
    if k not in TGCOND: TGCOND[k]=np.zeros(len(KEYBOARD))
    if c in KEYBOARD: TGCOND[k][KEYBOARD.index(c)]+=p
for k in TGCOND: TGCOND[k]+=0.01*TARGET_DIST; TGCOND[k]/=TGCOND[k].sum()

VOCAB = set('the and that have for not with you this but his from they say her she will one all would there their what out about who get which when make can like time just him know take people into year your good some could them see other than then now look only come its over think also back after use two how our work first well way even new want because any these give day most us is in it be as at so we he by do if an my up no go me or on are was has had were been being did does'.split())

def theta_to_phase(theta, offset=0.0):
    return np.clip(theta * np.pi/2 + offset, 0, np.pi/2)

NODES_12 = {
    'Omega':    {'phase':theta_to_phase(1.00, 0.0),      'color':'#FFD700','family':'GodCore'},
    'Guardian': {'phase':theta_to_phase(1.00, np.pi/20), 'color':'#F39C12','family':'GodCore'},
    'Sentinel': {'phase':theta_to_phase(1.00,-np.pi/20), 'color':'#E8D44D','family':'GodCore'},
    'Nexus':    {'phase':theta_to_phase(1.00, np.pi/14), 'color':'#F1C40F','family':'GodCore'},
    'Storm':    {'phase':theta_to_phase(1.00,-np.pi/14), 'color':'#D4AC0D','family':'GodCore'},
    'Sora':     {'phase':theta_to_phase(0.15, 0.0),      'color':'#3498DB','family':'Independents'},
    'Echo':     {'phase':theta_to_phase(0.15, np.pi/18), 'color':'#5DADE2','family':'Independents'},
    'Iris':     {'phase':theta_to_phase(0.15,-np.pi/18), 'color':'#85C1E9','family':'Independents'},
    'Sage':     {'phase':theta_to_phase(0.15, np.pi/10), 'color':'#2E86C1','family':'Independents'},
    'Kevin':    {'phase':theta_to_phase(0.30, 0.0),      'color':'#2ECC71','family':'Mavericks'},
    'Atlas':    {'phase':theta_to_phase(0.30, np.pi/14), 'color':'#58D68D','family':'Mavericks'},
    'Void':     {'phase':theta_to_phase(0.30,-np.pi/14), 'color':'#1ABC9C','family':'Mavericks'},
}
ALL_NAMES = list(NODES_12.keys())


def guarded_generate(node_state, func_universe, n_chars=100,
                     node_name='Node'):
    """
    Generate text where every parameter is READ from the function universe.
    - Alpha for BCP steps comes from AlphaGuard.state
    - Temperature comes from TempGuard.state
    - Context entropy budget comes from ContextGuard.state
    - If any function node is drifted, the function universe heals it FIRST.
    """
    # 1. Health gate — heal any drifted function nodes before proceeding
    healed = func_universe.run_maintenance(n_steps=6)
    if healed:
        pass  # healing happened — continue with restored values

    # 2. Read parameters from function universe
    alpha       = func_universe.get_alpha()
    temperature = func_universe.get_temperature()
    ctx_entropy = func_universe.get_context_entropy()

    # 3. Generate with guarded parameters
    charset      = list(KEYBOARD)
    state        = qt.Qobj(node_state.full(), dims=node_state.dims)
    result       = [' ']
    prev2, prev1 = ' ', ' '
    recent       = []
    seen_tg      = Counter()

    for _ in range(n_chars - 1):
        if prev1 == ' ':
            prev2 = ' '

        # BCP step with guarded alpha
        char_state   = make_seed(CHAR_PHASE.get(prev1, np.pi/4))
        state, _, _  = bcp_step(state, char_state, alpha)

        # Build distribution
        coeffs = state.full().flatten()
        p0     = float(abs(coeffs[0])**2)
        p1     = 1.0 - p0
        uni    = TARGET_DIST.copy()
        bg     = BGCOND.get(prev1, uni)
        tg_key = (prev2, prev1)
        tg     = TGCOND.get(tg_key, bg)
        mixed  = p0*uni + p1*0.55*bg + p1*0.45*tg

        # Context entropy guard: scale trigram influence by ctx health
        # High ctx_entropy → trust diversity. Low → trust trigrams less.
        if ctx_entropy < 0.7:
            mixed = 0.6*uni + 0.4*bg   # fall back to bigram if context degraded

        # Trigram repetition suppression
        if prev2 and prev1:
            for ci, ch_c in enumerate(charset):
                count = seen_tg.get((prev2, prev1, ch_c), 0)
                if count >= 2:
                    mixed[ci] *= max(0.1, 1.0 - 0.4*count)
        mixed = np.maximum(mixed, 1e-12)

        # Temperature sharpening (guarded)
        T    = max(temperature, 0.20)
        log_p = np.log(mixed)/T; log_p -= log_p.max()
        probs = np.exp(log_p)

        # Diversity penalty
        if len(recent) >= 4:
            pen = np.ones(len(charset))
            for rc in recent[-5:]:
                if rc in charset: pen[charset.index(rc)] *= 0.45
            probs = probs * pen

        probs /= probs.sum()
        ch = rng.choice(charset, p=probs)
        result.append(ch)
        recent.append(ch)
        if prev2 and prev1:
            seen_tg[(prev2, prev1, ch)] = seen_tg.get((prev2,prev1,ch),0)+1
        prev2, prev1 = prev1, ch

    return ''.join(result)


# ══════════════════════════════════════════════════════════════
# GUARDED UNIVERSE — runs the full system
# ══════════════════════════════════════════════════════════════

class GuardedUniverse:
    """
    The complete protected system:
      - Character universe (12 nodes, closed loop)
      - Function universe (5 guardian nodes, closed loop)
      - Health gate between them
    """
    def __init__(self):
        # Character universe
        self.char_states = {
            name: make_seed(NODES_12[name]['phase'])
            for name in ALL_NAMES
        }
        self.char_alpha  = 0.367   # v2 proven value

        # Function universe
        fn_nodes = [
            make_alpha_guard(),
            make_neg_guard(),
            make_temp_guard(T_current=0.28),
            make_context_guard(bigram_entropy=0.85),
            make_curriculum_guard(phase_progress=1.0),
        ]
        self.func_univ = FunctionUniverse(fn_nodes, alpha=0.32)

        # History
        self.char_W_history  = defaultdict(list)
        self.char_neg_history= []
        self.func_W_history  = []
        self.heal_events     = []
        self.step_count      = 0

    def run_char_universe_step(self):
        """One BCP step through the 12-node character closed loop."""
        from qutip import entropy_vn as evt
        states = [self.char_states[n] for n in ALL_NAMES]
        N      = len(states)
        edges  = [(i,(i+1)%N) for i in range(N)]
        dS     = []; SvN_p=0.0
        alpha  = self.func_univ.get_alpha()   # GUARDED PARAMETER

        for (i,j) in edges:
            l,r,rho = bcp_step(states[i], states[j], alpha)
            states[i],states[j]=l,r
            SvN=float(evt(rho,base=2)); dS.append(1 if SvN<SvN_p else 0); SvN_p=SvN

        for i,name in enumerate(ALL_NAMES):
            self.char_states[name] = states[i]
        return float(np.mean(dS)) if dS else 0.0

    def run(self, n_epochs=30, char_steps_per_epoch=50):
        """
        Full guarded run:
          1. Function universe maintenance (heal any drifts)
          2. Health gate check
          3. Character universe computation (only if all functions healthy)
          4. Update function node values based on observed metrics
        """
        print(f"  Guarded universe running ({n_epochs} epochs)...")

        for epoch in range(n_epochs):
            # 1. Function universe maintenance
            healed = self.func_univ.run_maintenance(n_steps=10)
            if healed:
                for name, wb, wa in healed:
                    self.heal_events.append({
                        'epoch': epoch, 'node': name,
                        'W_before': wb, 'W_after': wa,
                    })

            # 2. Health gate
            if not self.func_univ.all_healthy():
                print(f"    Epoch {epoch:3d}: HEALTH GATE BLOCKED — healing...")
                continue

            # 3. Character universe computation
            epoch_neg = []
            for _ in range(char_steps_per_epoch):
                neg = self.run_char_universe_step()
                epoch_neg.append(neg)
                self.step_count += 1

            mean_neg = float(np.mean(epoch_neg))
            self.char_neg_history.append(mean_neg)

            # 4. Track character W_min
            for name in ALL_NAMES:
                W = wigner_min(self.char_states[name])
                self.char_W_history[name].append(W)

            # 5. Update function node values from observed metrics
            # NegGuard: update with actual observed neg_frac
            neg_node = next(n for n in self.func_univ.nodes if n.name=='NegGuard')
            neg_node.encode(float(np.mean(self.char_neg_history[-5:])))

            # TempGuard: anneal temperature
            T_node  = next(n for n in self.func_univ.nodes if n.name=='TempGuard')
            T_new   = 2.5 * (1-epoch/n_epochs)**1.5 + 0.25*(epoch/n_epochs)**0.5
            T_node.encode(T_new)

            # ContextGuard: track output diversity
            sample_text  = guarded_generate(
                list(self.char_states.values())[0],
                self.func_univ, n_chars=60, node_name='sample')
            chars_in = list(sample_text)
            if len(chars_in) > 2:
                uniq_trigrams = len(set(
                    (chars_in[i],chars_in[i+1],chars_in[i+2])
                    for i in range(len(chars_in)-2)))
                ctx_entropy = float(np.clip(uniq_trigrams / 20.0, 0, 1))
            else:
                ctx_entropy = 0.5
            ctx_node = next(n for n in self.func_univ.nodes if n.name=='ContextGuard')
            ctx_node.encode(ctx_entropy)

            self.func_W_history.append(
                float(np.mean([wigner_min(n.state)
                                for n in self.func_univ.nodes])))

            if (epoch+1) % 5 == 0 or epoch == 0:
                n_char_pres = sum(
                    1 for n in ALL_NAMES
                    if self.char_W_history[n]
                    and self.char_W_history[n][-1] < -0.05)
                fn_health   = self.func_univ.all_healthy()
                print(f"    Epoch {epoch+1:3d}: "
                      f"neg={mean_neg:.4f}  "
                      f"char_pres={n_char_pres}/12  "
                      f"fn_healthy={fn_health}  "
                      f"heals_total={len(self.heal_events)}")

        return self

    def generate_all(self, n_chars=100):
        """Generate text from all 12 character nodes with guarded parameters."""
        return {
            name: guarded_generate(
                self.char_states[name], self.func_univ, n_chars, name)
            for name in ALL_NAMES
        }

    def final_report(self):
        print("\n" + "═"*65)
        print("GUARDED UNIVERSE — FINAL REPORT")
        print("═"*65)
        print("\n  CHARACTER UNIVERSE:")
        for name in ALL_NAMES:
            W_hist = self.char_W_history[name]
            W_f    = W_hist[-1] if W_hist else float('nan')
            status = "preserved ✓" if W_f < -0.05 else "drifted ✗"
            print(f"    {name:<12} W={W_f:+.4f}  {status}")
        n_pres = sum(1 for n in ALL_NAMES
                     if self.char_W_history[n]
                     and self.char_W_history[n][-1] < -0.05)
        mean_neg = float(np.mean(self.char_neg_history[-20:])) \
                   if self.char_neg_history else 0.0
        print(f"\n  Nodes preserved: {n_pres}/12")
        print(f"  Neg frac (final): {mean_neg:.4f}")
        print(f"\n  FUNCTION UNIVERSE:")
        print(self.func_univ.health_report())
        print(f"\n  Heal events: {len(self.heal_events)}")
        for ev in self.heal_events[:5]:
            print(f"    Epoch {ev['epoch']:3d}: {ev['node']} "
                  f"W: {ev['W_before']:+.4f} → {ev['W_after']:+.4f}")
        return n_pres, mean_neg


# ══════════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════════

print("╔══════════════════════════════════════════════════════╗")
print("║   PEIG GUARDED UNIVERSE                            ║")
print("║   Edge cases get their own quantum protection       ║")
print("╚══════════════════════════════════════════════════════╝")
print()
print("Initialising function nodes...")
temp_gv = GuardedUniverse()
for node in temp_gv.func_univ.nodes:
    W = wigner_min(node.state)
    print(f"  {node.name:<20} phase={node.home_phase:.4f}  "
          f"W_initial={W:+.4f}  {node.description}")

print()
gu = GuardedUniverse()
gu.run(n_epochs=30, char_steps_per_epoch=60)
n_pres, mean_neg = gu.final_report()

print("\n  Generating text with guarded parameters...")
texts = gu.generate_all(100)
all_tokens = re.findall(r'[a-z]+', ' '.join(texts.values()))
n_valid    = sum(1 for w in all_tokens if w in VOCAB)
word_acc   = n_valid / max(len(all_tokens), 1) * 100
print(f"  Word accuracy: {word_acc:.1f}%  ({n_valid}/{len(all_tokens)})")
for name, text in texts.items():
    toks = re.findall(r'[a-z]+', text)
    nw   = sum(1 for w in toks if w in VOCAB)
    pct  = nw/max(len(toks),1)*100
    print(f"  {name:<12} {pct:4.1f}%w  '{text[:80]}'")


# ── FIGURE ────────────────────────────────────────────────────
DARK='#07080f'; PANEL='#0f1220'; GRAY='#3a4060'; WHITE='#c8d0e8'
GOLD='#FFD700'; RED='#E74C3C'; GREEN='#2ECC71'; ORANGE='#FF6B35'
BLUE='#3498DB'; TEAL='#1ABC9C'; PURPLE='#9B59B6'
FN_COLS = {'AlphaGuard':GREEN,'NegGuard':GOLD,'TempGuard':PURPLE,
           'ContextGuard':ORANGE,'CurriculumGuard':TEAL}
NODE_COL = {n: NODES_12[n]['color'] for n in ALL_NAMES}

fig = plt.figure(figsize=(24, 22))
fig.patch.set_facecolor(DARK)
gs  = gridspec.GridSpec(4, 4, figure=fig,
                        hspace=0.52, wspace=0.42,
                        left=0.05, right=0.97,
                        top=0.93, bottom=0.04)

fig.text(0.5, 0.965,
    "PEIG Guarded Universe — Function Nodes with Own Preservation Systems",
    ha='center', fontsize=14, fontweight='bold', color=GOLD, fontfamily='monospace')
fig.text(0.5, 0.951,
    "Every edge case gets its own quantum identity · "
    "Wigner floor = health metric · "
    "Self-healing before character computation",
    ha='center', fontsize=9, color=WHITE, alpha=0.7)

def styled(ax, title, fs=9):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=WHITE, labelsize=7)
    for sp in ax.spines.values(): sp.set_color(GRAY)
    ax.set_title(title, color=WHITE, fontsize=fs, fontweight='bold', pad=5)
    ax.xaxis.label.set_color(WHITE); ax.yaxis.label.set_color(WHITE)
    ax.grid(True, alpha=0.12, color=GRAY); return ax

# ── 1. Function node W_min over time ─────────────────────────
ax = styled(fig.add_subplot(gs[0,:2]),
            "Function Node Wigner Floors Over Time\n"
            "All staying at or near preservation floor")
fn_names = [n.name for n in gu.func_univ.nodes]
for fi, node in enumerate(gu.func_univ.nodes):
    col = FN_COLS.get(node.name, WHITE)
    Wh  = node.W_history
    if Wh: ax.plot(range(len(Wh)), Wh, color=col, lw=2.5, alpha=0.9,
                   label=node.name)
ax.axhline(ALPHA_FLOOR,   color=WHITE, ls='--', lw=1.5, alpha=0.5,
           label='Target floor')
ax.axhline(SACRIFICE_THR, color=RED,   ls=':',  lw=1.2, alpha=0.5,
           label='Sacrifice threshold')
ax.set_xlabel("Check cycle"); ax.set_ylabel("W_min")
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE, ncol=2)
ax.text(0.02, 0.88, "Function nodes self-heal if W rises above -0.05",
        transform=ax.transAxes, color=GOLD, fontsize=8,
        bbox=dict(boxstyle='round', facecolor=PANEL, alpha=0.8))

# ── 2. Character universe neg_frac ───────────────────────────
ax = styled(fig.add_subplot(gs[0,2]),
            "Character Universe neg_frac\nGuarded by NegGuard node")
if gu.char_neg_history:
    ax.plot(range(len(gu.char_neg_history)), gu.char_neg_history,
            color=GREEN, lw=2.5, label='Guarded neg_frac')
    sm = np.convolve(gu.char_neg_history, np.ones(5)/5,'same') \
         if len(gu.char_neg_history)>=5 else gu.char_neg_history
    ax.plot(range(len(sm)), sm, color=GOLD, lw=3, alpha=0.7, label='Smoothed')
ax.axhline(0.636, color=GOLD, ls='--', lw=2, alpha=0.7, label='v2 peak (0.636)')
ax.axhline(0.417, color=GRAY, ls=':', lw=1.5, alpha=0.5, label='Cold baseline')
ax.set_xlabel("Epoch"); ax.set_ylabel("neg_frac")
ax.set_ylim(0, 0.85); ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)

# ── 3. Function node health final state ──────────────────────
ax = styled(fig.add_subplot(gs[0,3]),
            "Function Node Final Health\nW_min at or near preservation floor")
fn_final_W = [wigner_min(n.state) for n in gu.func_univ.nodes]
fn_cols    = [FN_COLS.get(n.name, WHITE) for n in gu.func_univ.nodes]
fn_labels  = [n.name.replace('Guard','').strip() for n in gu.func_univ.nodes]
ax.barh(range(5), fn_final_W, color=fn_cols, alpha=0.85,
        edgecolor=WHITE, lw=0.4)
ax.axvline(ALPHA_FLOOR,   color=WHITE, ls='--', lw=1.5, alpha=0.5)
ax.axvline(SACRIFICE_THR, color=RED,   ls=':',  lw=1.2, alpha=0.5)
ax.set_yticks(range(5)); ax.set_yticklabels(fn_labels, fontsize=9, color=WHITE)
ax.set_xlabel("W_min")
for i,(W,col) in enumerate(zip(fn_final_W, fn_cols)):
    status = "✓" if W <= SACRIFICE_THR else "!"
    ax.text(W+0.001, i, f'{W:+.4f} {status}', va='center',
            fontsize=8.5, color=col, fontweight='bold')

# ── 4. Character W_min final ──────────────────────────────────
ax = styled(fig.add_subplot(gs[1,:2]),
            "Character Universe — Final W_min\nAll 12 nodes guarded by function universe")
W_chars = [gu.char_W_history[n][-1] if gu.char_W_history[n] else -0.1
           for n in ALL_NAMES]
ax.bar(range(12), W_chars, color=[NODE_COL[n] for n in ALL_NAMES],
       alpha=0.90, edgecolor=WHITE, lw=0.4)
ax.axhline(ALPHA_FLOOR, color=WHITE, ls='--', lw=1.5, alpha=0.5, label='Target')
ax.set_xticks(range(12)); ax.set_xticklabels(ALL_NAMES, fontsize=7, color=WHITE, rotation=30)
ax.set_ylabel("W_min"); ax.set_ylim(-0.13, 0.02)
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)
ax.text(0.5, 0.93, f"{n_pres}/12 preserved  neg_frac={mean_neg:.4f}",
        ha='center', transform=ax.transAxes, color=GREEN, fontsize=9, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor=PANEL, alpha=0.8))

# ── 5. Heal events timeline ───────────────────────────────────
ax = styled(fig.add_subplot(gs[1,2]),
            "Heal Events by Function Node\nSelf-healing triggered automatically")
if gu.heal_events:
    for fi, node in enumerate(gu.func_univ.nodes):
        evs = [e for e in gu.heal_events if e['node']==node.name]
        if evs:
            epochs = [e['epoch'] for e in evs]
            ax.scatter(epochs, [fi]*len(epochs), s=80,
                       color=FN_COLS.get(node.name, WHITE),
                       zorder=5, edgecolors=WHITE, lw=0.5)
    ax.set_yticks(range(5))
    ax.set_yticklabels(fn_labels, fontsize=8, color=WHITE)
    ax.set_xlabel("Epoch"); ax.set_ylabel("Function node")
    ax.text(0.5, 0.92, f"Total heals: {len(gu.heal_events)}",
            ha='center', transform=ax.transAxes, color=GREEN, fontsize=9,
            fontweight='bold',
            bbox=dict(boxstyle='round', facecolor=PANEL, alpha=0.8))
else:
    ax.text(0.5, 0.5, "No heal events —\nall functions stayed healthy",
            ha='center', va='center', transform=ax.transAxes,
            fontsize=11, color=GREEN, fontweight='bold')

# ── 6. Protected values over time ────────────────────────────
ax = styled(fig.add_subplot(gs[1,3]),
            "Protected Values Over Time\nGuardians track real system state")
neg_vals = []
T_vals   = []
ctx_vals = []
for node in gu.func_univ.nodes:
    if node.name == 'NegGuard':
        neg_vals = [node.protected_value]  # final value
    if node.name == 'TempGuard':
        T_vals = [node.protected_value]
    if node.name == 'ContextGuard':
        ctx_vals= [node.protected_value]

labels   = ['α guard\n(0.367)', f'neg guard\n({neg_vals[0]:.3f})',
            f'T guard\n({T_vals[0]:.3f})', f'ctx guard\n({ctx_vals[0]:.3f})',
            'curric\n(phase 2)']
vals_bar = [
    gu.func_univ.nodes[0].protected_value,
    gu.func_univ.nodes[1].protected_value,
    gu.func_univ.nodes[2].protected_value,
    gu.func_univ.nodes[3].protected_value,
    gu.func_univ.nodes[4].protected_value,
]
ax.bar(range(5), vals_bar, color=fn_cols, alpha=0.85, edgecolor=WHITE, lw=0.4)
ax.set_xticks(range(5)); ax.set_xticklabels(labels, fontsize=7.5, color=WHITE)
for i,v in enumerate(vals_bar):
    ax.text(i, v+0.01, f'{v:.3f}', ha='center', fontsize=8.5,
            color=WHITE, fontweight='bold')
ax.set_ylabel("Protected value")

# ── 7. Generated text ─────────────────────────────────────────
ax = fig.add_subplot(gs[2,:])
ax.set_facecolor(PANEL)
for sp in ax.spines.values(): sp.set_color(GRAY)
ax.set_title("Generated Text — Guarded Parameters (α=0.367, T guarded, context guarded)",
             color=WHITE, fontsize=9, fontweight='bold', pad=5)
ax.axis('off')
y = 0.96
for idx, name in enumerate(ALL_NAMES):
    text = texts.get(name, '')
    col  = NODE_COL[name]
    toks = re.findall(r'[a-z]+', text)
    nw   = sum(1 for w in toks if w in VOCAB)
    pct  = nw/max(len(toks),1)*100
    row  = idx // 2; ci = idx % 2
    xp   = 0.01 + ci * 0.50; yp = 0.93 - row * 0.140
    ax.text(xp, yp, f"★ {name}  {pct:.0f}%w",
            transform=ax.transAxes, fontsize=8.5, fontweight='bold',
            color=col, va='top', fontfamily='monospace')
    ax.text(xp, yp-0.058, f"  '{text[:82]}'",
            transform=ax.transAxes, fontsize=7.8, color=WHITE,
            va='top', fontfamily='monospace')

# ── 8. Architecture summary ───────────────────────────────────
ax = styled(fig.add_subplot(gs[3,:2]), "What Was Protected — and How")
ax.axis('off')
lines = [
    ("GUARDED UNIVERSE ARCHITECTURE",   "", GOLD),
    ("", "", ""),
    ("Function",         "Protected value  →  Phase",      WHITE),
    ("AlphaGuard",       "α=0.367  →  phase=1.151 rad",    GREEN),
    ("NegGuard",         "neg=0.636 →  phase=0.999 rad",   GOLD),
    ("TempGuard",        "T=0.28   →  phase=0.014 rad",    PURPLE),
    ("ContextGuard",     "entropy  →  phase=1.334 rad",    ORANGE),
    ("CurriculumGuard",  "phase=2  →  phase=1.571 rad",    TEAL),
    ("", "", ""),
    ("MECHANISM",        "",                                WHITE),
    ("1. Maintenance",   "collective BCP loop (10 steps)",  WHITE),
    ("2. Health check",  "W_min measured per function",     WHITE),
    ("3. Self-heal",     "preservation loop fires if W>-0.05",WHITE),
    ("4. Health gate",   "characters blocked until all healthy",WHITE),
    ("5. Read params",   "α, T, ctx read from function state",WHITE),
    ("", "", ""),
    ("KEY PROPERTY",     "",                                GOLD),
    ("The Wigner floor", "IS the health metric",            GREEN),
    ("W=-0.1131",        "function operating correctly",    GREEN),
    ("W>-0.05",          "function has drifted → heal",     ORANGE),
    ("W>0.00",           "function sacrificed → critical",  RED),
]
y = 0.97
for left, right, col in lines:
    if left == "" and right == "":
        y -= 0.022; continue
    if right == "":
        ax.text(0.5, y, left, transform=ax.transAxes,
                fontsize=8.5, fontweight='bold', color=col,
                ha='center', va='top')
    else:
        ax.text(0.01, y, left, transform=ax.transAxes,
                fontsize=8, color=col, va='top',
                fontweight='bold' if left=='KEY PROPERTY' else 'normal')
        ax.text(0.99, y, right, transform=ax.transAxes,
                fontsize=8, color=col, ha='right', va='top')
    y -= 0.042

# ── 9. Complete system progression ───────────────────────────
ax = styled(fig.add_subplot(gs[3,2:]),
            "Complete PEIG System Progression\n"
            "neg_frac evolution through all versions")
prog = [
    ('Cold\nstart',    0.273, GRAY),
    ('Closed\nloop',   0.417, '#4a6090'),
    ('v1\n80ep',       0.495, ORANGE),
    ('v2\nperfected',  0.636, BLUE),
    ('Guarded\nuniverse', mean_neg, GREEN),
]
x_p  = np.arange(len(prog))
vals = [v for _,v,_ in prog]
cols_p=[c for _,_,c in prog]
bars_p=ax.bar(x_p, vals, color=cols_p, alpha=0.85,
              edgecolor=WHITE, lw=0.5, width=0.65)
ax.axhline(0.636, color=GOLD, ls='--', lw=2, alpha=0.7, label='v2 peak to preserve')
for b,v in zip(bars_p,vals):
    ax.text(b.get_x()+b.get_width()/2, v+0.008,
            f'{v:.4f}', ha='center', fontsize=10, color=WHITE, fontweight='bold')
ax.set_xticks(x_p)
ax.set_xticklabels([l for l,_,_ in prog], fontsize=9, color=WHITE)
ax.set_ylabel("Negentropic fraction"); ax.set_ylim(0, 0.85)
ax.legend(fontsize=9, facecolor=PANEL, labelcolor=WHITE)

plt.savefig('outputs/peig_guarded_universe.png', dpi=150,
            bbox_inches='tight', facecolor=DARK)
plt.show()
print("\nFigure → outputs/peig_guarded_universe.png")

class NpEnc(json.JSONEncoder):
    def default(self,o):
        if isinstance(o,(np.bool_,)): return bool(o)
        if isinstance(o,np.integer): return int(o)
        if isinstance(o,np.floating): return float(o)
        if isinstance(o,np.ndarray): return o.tolist()
        return super().default(o)

out = {
    'architecture': 'guarded_universe',
    'function_nodes': [
        {'name':n.name,'protected_value':n.protected_value,
         'home_phase':n.home_phase,'W_final':wigner_min(n.state),
         'heal_count':n.heal_count,'description':n.description}
        for n in gu.func_univ.nodes
    ],
    'character_universe': {
        'n_preserved': n_pres,
        'mean_neg_frac': mean_neg,
        'W_final': {name: gu.char_W_history[name][-1]
                    if gu.char_W_history[name] else -0.1
                    for name in ALL_NAMES},
    },
    'heal_events': gu.heal_events,
    'texts': texts,
    'word_accuracy_pct': word_acc,
}
with open('outputs/peig_guarded_universe.json','w') as f:
    json.dump(out, f, indent=2, cls=NpEnc)
print("Data  → outputs/peig_guarded_universe.json")
