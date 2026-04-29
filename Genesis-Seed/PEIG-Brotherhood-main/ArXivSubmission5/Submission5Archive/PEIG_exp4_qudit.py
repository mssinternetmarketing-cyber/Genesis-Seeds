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
# EXPERIMENT 4: QUDIT GENERALISATION d=2,3,4,5,7
# Tests whether closed-loop advantage holds across qudit dimensions
# Key finding: closed wins d=2,3,4; open wins d=5,7 (critical d* ~ 4-5)
# ══════════════════════════════════════════════════════════════════════
QUDIT_ARMS=[
    {"n_nodes":3,"closed":False,"d":2,"eta":0.05,"alpha0":0.30},
    {"n_nodes":3,"closed":True, "d":2,"eta":0.05,"alpha0":0.30},
    {"n_nodes":3,"closed":False,"d":3,"eta":0.05,"alpha0":0.30},
    {"n_nodes":3,"closed":True, "d":3,"eta":0.05,"alpha0":0.30},
    {"n_nodes":3,"closed":False,"d":4,"eta":0.05,"alpha0":0.30},
    {"n_nodes":3,"closed":True, "d":4,"eta":0.05,"alpha0":0.30},
    {"n_nodes":3,"closed":False,"d":5,"eta":0.05,"alpha0":0.30},
    {"n_nodes":3,"closed":True, "d":5,"eta":0.05,"alpha0":0.30},
    {"n_nodes":3,"closed":False,"d":7,"eta":0.05,"alpha0":0.30},
    {"n_nodes":3,"closed":True, "d":7,"eta":0.05,"alpha0":0.30},
]
QUDIT_NAMES=[f"d={c['d']}_{\'C\' if c['closed'] else \'O\'}" for c in QUDIT_ARMS]
print("EXPERIMENT 4: QUDIT GENERALISATION")
results=[]
for i,(cfg,name) in enumerate(zip(QUDIT_ARMS,QUDIT_NAMES)):
    m=run_topology_full(cfg,n_steps=100)
    score=(0.5*m["W_eff"]+0.3*m["mean_C"]+0.2*m["neg_frac"]
           if cfg["d"]==2 else 0.5*m["mean_C"]+0.5*m["neg_frac"])
    results.append({"arm":i,"name":name,"d":cfg["d"],"closed":cfg["closed"],
                    "mean_C":round(m["mean_C"],5),"neg_frac":round(m["neg_frac"],5),
                    "W_eff":round(m["W_eff"],5) if cfg["d"]==2 else None,
                    "alpha_fin":round(m["alpha_fin"],5),"score":round(score,5)})
    print(f"[{i}] {name:<12} d={cfg['d']} C={m['mean_C']:.5f} neg={m['neg_frac']:.3f} score={score:.4f}")

print("\n── CLOSED vs OPEN by dimension ──")
for d in [2,3,4,5,7]:
    o=[r for r in results if r["d"]==d and not r["closed"]][0]
    c=[r for r in results if r["d"]==d and     r["closed"]][0]
    adv=c["score"]-o["score"]
    print(f"  d={d}: Open={o['score']:.4f} Closed={c['score']:.4f} D={adv:+.4f} "
          f"{'CLOSED WINS' if adv>0 else 'OPEN WINS --- critical d* boundary'}")
with open("outputs/exp4_qudit.json","w") as f:
    json.dump({"experiment":"qudit_generalisation","results":results},f,indent=2)
print("Saved -> outputs/exp4_qudit.json")
