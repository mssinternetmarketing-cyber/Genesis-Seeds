"""
PEIG Shared Primitives — All Experiments
Author: Kevin Monette | March 2026
"""
import numpy as np
import qutip as qt
import json, csv
from pathlib import Path
Path("outputs").mkdir(exist_ok=True)
rng = np.random.default_rng(42)

CNOT_GATE = qt.Qobj(
    np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]],dtype=complex),
    dims=[[2,2],[2,2]])

def make_seed(phase, d=2):
    if d == 2:
        b0,b1 = qt.basis(2,0), qt.basis(2,1)
        return (b0 + np.exp(1j*phase)*b1).unit()
    state = sum(np.exp(1j*phase*k)*qt.basis(d,k) for k in range(d))
    return state.unit()

def bcp_step_qubit(psiA, psiB, alpha):
    rho12 = qt.ket2dm(qt.tensor(psiA, psiB))
    U = alpha*CNOT_GATE + (1-alpha)*qt.qeye([2,2])
    rho_p = U*rho12*U.dag()
    _,evA = rho_p.ptrace(0).eigenstates()
    _,evB = rho_p.ptrace(1).eigenstates()
    return evA[-1], evB[-1], rho_p

def bcp_step_qudit(psiA, psiB, alpha, d):
    rho12 = qt.ket2dm(qt.tensor(psiA, psiB))
    mat = np.zeros((d*d, d*d), dtype=complex)
    for a in range(d):
        for b in range(d):
            mat[a*d+(a+b)%d, a*d+b] = 1.0
    SUM = qt.Qobj(mat, dims=[[d,d],[d,d]])
    U = alpha*SUM + (1-alpha)*qt.qeye([d,d])
    rho_p = U*rho12*U.dag()
    _,evA = rho_p.ptrace(0).eigenstates()
    _,evB = rho_p.ptrace(1).eigenstates()
    return evA[-1], evB[-1], rho_p

def coherence(psi): return float((qt.ket2dm(psi)**2).tr().real)
def entropy_vn(rho): return float(qt.entropy_vn(rho, base=2))
XVEC = np.linspace(-2, 2, 48)
def wigner_min(psi): return float(np.min(qt.wigner(qt.ket2dm(psi), XVEC, XVEC)))
ALPHA_FLOOR = -0.1131

def apply_lindblad_noise(rho, p1=2.5e-4, p_phi=8.75e-4):
    K0 = qt.Qobj([[1,0],[0,np.sqrt(1-p1)]])
    K1 = qt.Qobj([[0,np.sqrt(p1)],[0,0]])
    rho = K0*rho*K0.dag() + K1*rho*K1.dag()
    K0d = np.sqrt(1-p_phi/2)*qt.qeye(2)
    K1d = np.sqrt(p_phi/2)*qt.sigmaz()
    return K0d*rho*K0d.dag() + K1d*rho*K1d.dag()

def run_topology_full(cfg, n_steps=150, noise=False):
    n=cfg["n_nodes"]; closed=cfg.get("closed",False)
    star=cfg.get("star",False); eta=cfg.get("eta",0.05)
    alpha0=cfg.get("alpha0",0.30); d=cfg.get("d",2)
    phases=[np.pi/2*k/(n-1) for k in range(n)] if n>1 else [np.pi/4]
    states=[make_seed(p,d) for p in phases]
    if star: edges=[(0,j) for j in range(1,n)]
    elif closed: edges=[(i,(i+1)%n) for i in range(n)]
    else: edges=[(i,i+1) for i in range(n-1)]
    alphas={e:alpha0 for e in edges}
    C_prev=np.mean([coherence(s) for s in states]); SvN_prev=0.0; dS_signs=[]
    for t in range(n_steps):
        for (i,j) in edges:
            if d==2: l,r,rho=bcp_step_qubit(states[i],states[j],alphas[(i,j)])
            else:    l,r,rho=bcp_step_qudit(states[i],states[j],alphas[(i,j)],d)
            if noise and d==2:
                for idx,st in [(i,l),(j,r)]:
                    rho_n=apply_lindblad_noise(qt.ket2dm(st),cfg.get("p1",2.5e-4),cfg.get("p_phi",8.75e-4))
                    _,ev=rho_n.eigenstates(); states[idx]=ev[-1]
            states[i],states[j]=l,r
        SvN=entropy_vn(qt.ket2dm(qt.tensor(states[0],states[-1])).ptrace(0))
        dS=SvN-SvN_prev; dS_signs.append(1 if dS<0 else 0)
        C_avg=np.mean([coherence(s) for s in states]); dC=C_avg-C_prev
        for e in edges: alphas[e]=float(np.clip(alphas[e]+eta*dC,0,1))
        C_prev=C_avg; SvN_prev=SvN
    W_floors=[wigner_min(s) for s in states] if d==2 else [0.0]*n
    mean_W=float(np.mean(W_floors))
    W_asym=float(W_floors[-1]-W_floors[0]) if d==2 else 0.0
    W_eff=float(abs(mean_W)/abs(ALPHA_FLOOR)) if d==2 else 0.0
    mean_C=float(np.mean([coherence(s) for s in states]))
    neg_frac=float(np.mean(dS_signs))
    alpha_fin=float(np.mean(list(alphas.values())))
    destroyed=star and d==2 and all(abs(w)<0.02 for w in W_floors)
    return {"mean_W":mean_W,"W_eff":W_eff,"W_asym":W_asym,"W_floors":W_floors,
            "mean_C":mean_C,"neg_frac":neg_frac,"alpha_fin":alpha_fin,
            "destroyed":destroyed,"n_nodes":n,"closed":closed,"star":star,"d":d}

def ucb_select(Q, N, t, c=1.5):
    K=len(Q)
    unpulled=[a for a in range(K) if N[a]==0]
    if unpulled: return unpulled[0]
    return int(np.argmax(Q + c*np.sqrt(np.log(t+1)/np.maximum(N,1))))

def ucb_update(Q, N, arm, reward):
    N[arm]+=1; Q[arm]+=(reward-Q[arm])/N[arm]

print("Primitives loaded.")

# ══════════════════════════════════════════════════════════════════════
# EXPERIMENT 1: INTRINSIC PEIG-Q REWARD AGENT
# Agent maximises its own PEIG quality — zero external task signal
# ══════════════════════════════════════════════════════════════════════
def peig_quality(metrics):
    P = float(np.clip(metrics["W_eff"], 0, 1))
    E = float(metrics["mean_C"])
    I = float(metrics["neg_frac"])
    G = float(np.clip((metrics["W_asym"] + 0.1131) / 0.2262, 0, 1))
    Q = 0.25*(P + E + I + G)
    return Q, {"P":P,"E":E,"I":I,"G":G}

ARM_CONFIGS = [
    {"n_nodes":3,"closed":False,"star":False,"eta":0.05,"alpha0":0.30},
    {"n_nodes":5,"closed":False,"star":False,"eta":0.05,"alpha0":0.30},
    {"n_nodes":5,"closed":True, "star":False,"eta":0.05,"alpha0":0.30},
    {"n_nodes":5,"closed":True, "star":False,"eta":0.20,"alpha0":0.30},
    {"n_nodes":7,"closed":True, "star":False,"eta":0.05,"alpha0":0.30},
    {"n_nodes":5,"closed":False,"star":True, "eta":0.05,"alpha0":0.30},
]
ARM_NAMES=["Open N=3","Open N=5","Closed N=5 eta=0.05",
           "Closed N=5 eta=0.20","Closed N=7","Star N=5"]
K=len(ARM_CONFIGS)
Q_global=np.zeros(K); N_global=np.zeros(K); t_ucb=0
Q_prev=0.5; exp_log=[]; cum_R=[]; total_R=0.0
Q_hist={i:[] for i in range(K)}

N_EPS=60
print("EXPERIMENT 1: INTRINSIC PEIG-Q REWARD AGENT")
for ep in range(1, N_EPS+1):
    t_ucb+=1
    arm=ucb_select(Q_global,N_global,t_ucb)
    metrics=run_topology_full(ARM_CONFIGS[arm])
    Q_now,peig_vec=peig_quality(metrics)
    reward=Q_now-Q_prev; Q_prev=Q_now
    ucb_update(Q_global,N_global,arm,reward)
    total_R+=reward; cum_R.append(total_R/ep)
    for i in range(K): Q_hist[i].append(float(Q_global[i]))
    exp_log.append({"episode":ep,"arm":arm,"arm_name":ARM_NAMES[arm],
                    "reward":round(reward,4),"Q_now":round(Q_now,4),
                    "P":round(peig_vec["P"],4),"E":round(peig_vec["E"],4),
                    "I":round(peig_vec["I"],4),"G":round(peig_vec["G"],4)})
    print(f"Ep{ep:03d} [{arm}]{ARM_NAMES[arm]:<20} Q={Q_now:.4f} DQ={reward:+.4f} "
          f"P={peig_vec['P']:.3f} E={peig_vec['E']:.3f} I={peig_vec['I']:.3f} G={peig_vec['G']:.3f}")

best=int(np.argmax(Q_global))
print(f"\nBEST ARM: [{best}] {ARM_NAMES[best]}  Q={Q_global[best]:.4f}")
print(f"Pulls: {N_global.tolist()}")
with open("outputs/exp1_intrinsic_reward.json","w") as f:
    json.dump({"experiment":"intrinsic_PEIG_Q","n_eps":N_EPS,
               "final_Q":Q_global.tolist(),"pulls":N_global.tolist(),
               "best_arm":best,"best_arm_name":ARM_NAMES[best],
               "Q_history":Q_hist,"log":exp_log},f,indent=2)
print("Saved -> outputs/exp1_intrinsic_reward.json")
