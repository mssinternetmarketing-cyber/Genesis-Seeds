import numpy as np, qutip as qt, matplotlib, json
from pathlib import Path
from collections import defaultdict
matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.gridspec as gridspec
Path("outputs").mkdir(exist_ok=True)

CNOT_GATE = qt.Qobj(np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]],dtype=complex),dims=[[2,2],[2,2]])
XVEC = np.linspace(-2,2,60)

def make_seed(phase):
    b0,b1=qt.basis(2,0),qt.basis(2,1); return (b0+np.exp(1j*phase)*b1).unit()

def bcp_step(psiA,psiB,alpha):
    rho12=qt.ket2dm(qt.tensor(psiA,psiB))
    U=alpha*CNOT_GATE+(1-alpha)*qt.qeye([2,2]); rho_p=U*rho12*U.dag()
    _,evA=rho_p.ptrace(0).eigenstates(); _,evB=rho_p.ptrace(1).eigenstates()
    return evA[-1],evB[-1],rho_p

def coherence(psi): return float((qt.ket2dm(psi)**2).tr().real)
def wigner_min(psi): return float(np.min(qt.wigner(qt.ket2dm(psi),XVEC,XVEC)))
def entropy_vn(rho): return float(qt.entropy_vn(rho,base=2))

ALPHA_FLOOR=-0.1131; N_STEPS=500

def canon(): return [make_seed(np.pi/2*k/4) for k in range(5)]

def run_core(states,edges_fn,alpha_fn,n_steps,inject_fn=None):
    n=len(states); edges=edges_fn(n); alphas={e:0.30 for e in edges}
    C_prev=np.mean([coherence(s) for s in states]); SvN_p=0.0; neg_h=[]; W_h=[]
    for t in range(n_steps):
        if inject_fn: states=inject_fn(states,t)
        alpha_t=alpha_fn(t,alphas)
        dS=[]
        for (i,j) in edges:
            a=alpha_t[(i,j)] if isinstance(alpha_t,dict) else alpha_t
            l,r,rho=bcp_step(states[i],states[j],a); states[i],states[j]=l,r
            SvN=entropy_vn(rho); dS.append(1 if SvN<SvN_p else 0); SvN_p=SvN
        C_avg=np.mean([coherence(s) for s in states]); dC=C_avg-C_prev
        if isinstance(alpha_t,dict):
            for e in edges: alphas[e]=float(np.clip(alphas[e]+0.05*dC,0,1))
        C_prev=C_avg; neg_h.append(float(np.mean(dS)) if dS else 0.0)
        if (t+1)%20==0: W_h.append(np.mean([wigner_min(s) for s in states]))
    return neg_h, W_h

closed_edges = lambda n: [(i,(i+1)%n) for i in range(n)]
adaptive_alpha = lambda t,alphas: alphas

# BASELINE
def run_baseline():
    return run_core(canon(), closed_edges, adaptive_alpha, N_STEPS)

# S1: Adversarial injection
def run_s1(reset_freq=10):
    def inject(states,t):
        if (t+1)%reset_freq==0: states[0]=make_seed(0.0)
        return states
    return run_core(canon(), closed_edges, adaptive_alpha, N_STEPS, inject)

# S2: Fractal nested
def run_s2():
    n_macro=5; n_inner=3
    macro=[[ make_seed(np.pi/2*k/(n_macro-1)+np.pi/20*(j-1)) for j in range(n_inner)] for k in range(n_macro)]
    ma={(i,(i+1)%n_macro):0.30 for i in range(n_macro)}
    SvN_p=0.0; neg_h=[]; W_h=[]
    for t in range(N_STEPS):
        for k in range(n_macro):
            for ci in range(n_inner):
                cj=(ci+1)%n_inner; l,r,_=bcp_step(macro[k][ci],macro[k][cj],0.35); macro[k][ci],macro[k][cj]=l,r
        reps=[max(macro[k],key=coherence) for k in range(n_macro)]
        dS=[]
        for i in range(n_macro):
            j=(i+1)%n_macro; l,r,rho=bcp_step(reps[i],reps[j],ma[(i,j)]); reps[i],reps[j]=l,r
            SvN=entropy_vn(rho); dS.append(1 if SvN<SvN_p else 0); SvN_p=SvN
        for k in range(n_macro): macro[k][0]=reps[k]
        C_avg=np.mean([coherence(reps[k]) for k in range(n_macro)])
        neg_h.append(float(np.mean(dS)) if dS else 0.0)
        if (t+1)%20==0: W_h.append(np.mean([wigner_min(reps[k]) for k in range(n_macro)]))
    return neg_h, W_h

# S3: Adaptive seed steering
def run_s3():
    phases=np.linspace(0,np.pi/2,10); K=len(phases)
    Q_u=np.zeros(K); N_u=np.zeros(K); t_u=0
    states=canon(); n=len(states); edges=closed_edges(n)
    alphas={e:0.30 for e in edges}; C_prev=np.mean([coherence(s) for s in states])
    SvN_p=0.0; neg_h=[]; W_h=[]
    for t in range(N_STEPS):
        t_u+=1
        unpulled=[a for a in range(K) if N_u[a]==0]
        arm=unpulled[0] if unpulled else int(np.argmax(Q_u+1.5*np.sqrt(np.log(t_u+1)/np.maximum(N_u,1))))
        states[0]=make_seed(phases[arm])
        dS=[]; dsTotal=0.0
        for (i,j) in edges:
            l,r,rho=bcp_step(states[i],states[j],alphas[(i,j)]); states[i],states[j]=l,r
            SvN=entropy_vn(rho); d=SvN-SvN_p; dS.append(1 if d<0 else 0); dsTotal+=(abs(d) if d<0 else 0); SvN_p=SvN
        N_u[arm]+=1; Q_u[arm]+=(dsTotal-Q_u[arm])/N_u[arm]
        C_avg=np.mean([coherence(s) for s in states]); dC=C_avg-C_prev
        for e in edges: alphas[e]=float(np.clip(alphas[e]+0.05*dC,0,1))
        C_prev=C_avg; neg_h.append(float(np.mean(dS)))
        if (t+1)%20==0: W_h.append(np.mean([wigner_min(s) for s in states]))
    return neg_h, W_h

# S4: Landauer
def run_s4():
    states=canon(); n=len(states); edges=closed_edges(n)
    alphas={e:0.30 for e in edges}; C_prev=np.mean([coherence(s) for s in states])
    SvN_p=0.0; neg_h=[]; W_h=[]; ancilla=make_seed(np.pi/4)
    for t in range(N_STEPS):
        dS=[]
        for (i,j) in edges:
            l,r,rho=bcp_step(states[i],states[j],alphas[(i,j)]); states[i],states[j]=l,r
            SvN=entropy_vn(rho); dS.append(1 if SvN<SvN_p else 0); SvN_p=SvN
        C_avg=np.mean([coherence(s) for s in states]); dC=C_avg-C_prev
        for e in edges:
            old=alphas[e]; new=float(np.clip(old+0.05*dC,0,1)); alphas[e]=new
            if abs(new-old)>1e-6:
                best=int(np.argmax([coherence(s) for s in states]))
                an_new,st_new,_=bcp_step(ancilla,states[best],0.25); ancilla=an_new; states[best]=st_new
        C_prev=C_avg; neg_h.append(float(np.mean(dS)))
        if (t+1)%20==0: W_h.append(np.mean([wigner_min(s) for s in states]))
    return neg_h, W_h

# S5: Floquet
def run_s5(A=0.15,omega=2*np.pi/9):
    states=canon(); n=len(states); edges=closed_edges(n)
    SvN_p=0.0; neg_h=[]; W_h=[]
    for t in range(N_STEPS):
        alpha_t=float(np.clip(0.30+A*np.sin(omega*t),0,1))
        dS=[]
        for (i,j) in edges:
            l,r,rho=bcp_step(states[i],states[j],alpha_t); states[i],states[j]=l,r
            SvN=entropy_vn(rho); dS.append(1 if SvN<SvN_p else 0); SvN_p=SvN
        neg_h.append(float(np.mean(dS)))
        if (t+1)%20==0: W_h.append(np.mean([wigner_min(s) for s in states]))
    return neg_h, W_h

# S6: Many-body
def run_s6():
    states=canon(); n=len(states); alpha=0.30
    SvN_p=0.0; neg_h=[]; W_h=[]; C_prev=np.mean([coherence(s) for s in states])
    for t in range(N_STEPS):
        total_SvN=0.0; npairs=0
        for i in range(n):
            for j in range(i+1,n):
                l,r,rho=bcp_step(states[i],states[j],alpha); states[i],states[j]=l,r; total_SvN+=entropy_vn(rho); npairs+=1
        avg_SvN=total_SvN/max(npairs,1); dS=1 if avg_SvN<SvN_p else 0; SvN_p=avg_SvN
        C_avg=np.mean([coherence(s) for s in states]); dC=C_avg-C_prev
        alpha=float(np.clip(alpha+0.05*dC,0,1)); C_prev=C_avg; neg_h.append(float(dS))
        if (t+1)%20==0: W_h.append(np.mean([wigner_min(s) for s in states]))
    return neg_h, W_h

# S7: S1+S5 combined
def run_s7(reset_freq=10,A=0.15,omega=2*np.pi/9):
    states=canon(); n=len(states); edges=closed_edges(n)
    SvN_p=0.0; neg_h=[]; W_h=[]
    for t in range(N_STEPS):
        if (t+1)%reset_freq==0: states[0]=make_seed(0.0)
        alpha_t=float(np.clip(0.30+A*np.sin(omega*t),0,1))
        dS=[]
        for (i,j) in edges:
            l,r,rho=bcp_step(states[i],states[j],alpha_t); states[i],states[j]=l,r
            SvN=entropy_vn(rho); dS.append(1 if SvN<SvN_p else 0); SvN_p=SvN
        neg_h.append(float(np.mean(dS)))
        if (t+1)%20==0: W_h.append(np.mean([wigner_min(s) for s in states]))
    return neg_h, W_h

print("Running all strategies...")
strats=[
    ("Baseline",       run_baseline, {}),
    ("S1 Adversarial", run_s1,       {'reset_freq':10}),
    ("S2 Fractal",     run_s2,       {}),
    ("S3 Adaptive",    run_s3,       {}),
    ("S4 Landauer",    run_s4,       {}),
    ("S5 Floquet",     run_s5,       {'A':0.15,'omega':2*np.pi/9}),
    ("S6 ManyBody",    run_s6,       {}),
    ("S7 Combined",    run_s7,       {'reset_freq':10,'A':0.15,'omega':2*np.pi/9}),
]

results={}
for name,fn,kwargs in strats:
    print(f"  {name}...",end=" ",flush=True)
    nh,wh=fn(**kwargs)
    mn=float(np.mean(nh[-100:])); pk=float(np.max(nh)); mw=float(np.mean(wh[-5:])) if wh else -0.11
    results[name]={'neg_hist':nh,'W_hist':wh,'mean_neg':mn,'peak_neg':pk,'mean_W':mw}
    print(f"neg={mn:.4f} peak={pk:.3f}")

base=results['Baseline']['mean_neg']
best=max(results,key=lambda k:results[k]['mean_neg'])
print(f"\nBest: {best} = {results[best]['mean_neg']:.4f} ({results[best]['mean_neg']/base:.2f}x baseline)")

# PLOT
DARK='#07080f'; PANEL='#0f1220'; GRAY='#3a4060'; WHITE='#c8d0e8'
GOLD='#FFD700'; RED='#E74C3C'; GREEN='#2ECC71'; ORANGE='#FF6B35'
BLUE='#3498DB'; TEAL='#1ABC9C'; PURPLE='#9B59B6'; PINK='#FF6B9E'
COLS={'Baseline':GRAY,'S1 Adversarial':RED,'S2 Fractal':PURPLE,'S3 Adaptive':ORANGE,
      'S4 Landauer':TEAL,'S5 Floquet':BLUE,'S6 ManyBody':PINK,'S7 Combined':GOLD}

fig=plt.figure(figsize=(24,18)); fig.patch.set_facecolor(DARK)
gs=gridspec.GridSpec(3,4,figure=fig,hspace=0.50,wspace=0.40,left=0.05,right=0.97,top=0.93,bottom=0.04)

fig.text(0.5,0.965,"PEIG Negentropic Magnification — Six Strategies + Best Combination",
    ha='center',fontsize=14,fontweight='bold',color=GOLD,fontfamily='monospace')
fig.text(0.5,0.951,"Adversarial · Fractal · Adaptive Seed · Landauer · Floquet · Many-Body · S1+S5",
    ha='center',fontsize=9,color=WHITE,alpha=0.7)

def styled(ax,title,fs=9):
    ax.set_facecolor(PANEL); ax.tick_params(colors=WHITE,labelsize=7)
    for sp in ax.spines.values(): sp.set_color(GRAY)
    ax.set_title(title,color=WHITE,fontsize=fs,fontweight='bold',pad=5)
    ax.xaxis.label.set_color(WHITE); ax.yaxis.label.set_color(WHITE)
    ax.grid(True,alpha=0.15,color=GRAY); return ax

# 1. Bar chart
ax=styled(fig.add_subplot(gs[0,:2]),"Negentropic Fraction per Strategy\nFinal 100 steps")
names_s=[n for n,_,_ in strats]
nv=[results[n]['mean_neg'] for n in names_s]; pv=[results[n]['peak_neg'] for n in names_s]
cb=[COLS[n] for n in names_s]
bars=ax.bar(range(8),nv,color=cb,alpha=0.85,edgecolor=WHITE,lw=0.4)
ax.scatter(range(8),pv,color=WHITE,s=45,zorder=6,marker='^',label='Peak')
for i,(b,v) in enumerate(zip(bars,nv)):
    ax.text(b.get_x()+b.get_width()/2,v+0.008,f'{v:.3f}',ha='center',fontsize=8.5,color=WHITE,fontweight='bold')
ax.set_xticks(range(8)); ax.set_xticklabels([n.split()[0] for n in names_s],fontsize=8.5,color=WHITE)
ax.set_ylabel("Mean neg. fraction"); ax.set_ylim(0,1.05)
ax.axhline(0.500,color=ORANGE,ls='--',lw=1.5,alpha=0.6,label='Torus baseline (0.500)')
ax.axhline(0.99,color=GREEN,ls=':',lw=1.5,alpha=0.6,label='Target (0.990)')
ax.legend(fontsize=8,facecolor=PANEL,labelcolor=WHITE)
ax.text(7,nv[-1]+0.02,'★',ha='center',fontsize=16,color=GOLD)

# 2. Trajectories
ax=styled(fig.add_subplot(gs[0,2:]),"Negentropic Trajectories — All Strategies\nSmoothed over 25 steps")
for name in names_s:
    nh=results[name]['neg_hist']; sm=np.convolve(nh,np.ones(25)/25,'same')
    lw=3 if name==best else 1.5; a=0.95 if name==best else 0.55
    ax.plot(range(len(sm)),sm,color=COLS[name],lw=lw,alpha=a,label=name.split()[0])
ax.set_xlabel("Step"); ax.set_ylabel("Neg. fraction")
ax.set_ylim(0,1.05); ax.legend(fontsize=8,facecolor=PANEL,labelcolor=WHITE,ncol=2)

# 3-6: Four key strategies
for idx,(sname,title) in enumerate([
    ('S1 Adversarial','S1: Adversarial Injection'),
    ('S5 Floquet',     'S5: Floquet Modulation'),
    ('S7 Combined',    'S7: S1+S5 Combined ★'),
    ('S6 ManyBody',    'S6: Many-Body All-to-All'),
]):
    ax=styled(fig.add_subplot(gs[1,idx]),title)
    bh=np.convolve(results['Baseline']['neg_hist'],np.ones(20)/20,'same')
    sh=np.convolve(results[sname]['neg_hist'],np.ones(20)/20,'same')
    ax.plot(range(len(bh)),bh,color=GRAY,lw=1.5,alpha=0.6,label='Baseline')
    ax.plot(range(len(sh)),sh,color=COLS[sname],lw=2.5,label=sname.split()[0])
    ax.set_xlabel("Step"); ax.set_ylabel("Neg. fraction"); ax.set_ylim(0,1.05)
    ax.legend(fontsize=8,facecolor=PANEL,labelcolor=WHITE)
    d=results[sname]['mean_neg']-base
    ax.text(0.03,0.87,f"Δ={d:+.4f}\n{results[sname]['mean_neg']:.4f}",
        transform=ax.transAxes,color=COLS[sname],fontsize=10,fontweight='bold',
        bbox=dict(boxstyle='round',facecolor=PANEL,alpha=0.8))

# 7. W_min
ax=styled(fig.add_subplot(gs[2,:2]),"W_min per Strategy — Preservation Maintained")
wv=[results[n]['mean_W'] for n in names_s]
ax.barh(range(8),wv,color=[COLS[n] for n in names_s],alpha=0.85,edgecolor=WHITE,lw=0.3)
ax.axvline(ALPHA_FLOOR,color=WHITE,ls='--',lw=1.5,alpha=0.5,label='Target')
ax.set_yticks(range(8)); ax.set_yticklabels(names_s,fontsize=8,color=WHITE)
ax.set_xlabel("Mean W_min"); ax.legend(fontsize=8,facecolor=PANEL,labelcolor=WHITE)

# 8. Summary
ax=styled(fig.add_subplot(gs[2,2:]),"Performance Summary")
ax.axis('off')
rows=[['Strategy','Neg frac','×Baseline','Verdict']]
for n in names_s:
    r=results[n]; m=r['mean_neg']/base
    v='BEST ★' if n==best else ('Strong' if r['mean_neg']>0.70 else ('Good' if r['mean_neg']>0.55 else 'Mild'))
    rows.append([n,f"{r['mean_neg']:.4f}",f"{m:.2f}×",v])
cw=[0.30,0.18,0.18,0.22]
y=0.96
for ci,(lbl,w) in enumerate(zip(rows[0],cw)):
    ax.text(sum(cw[:ci])+w/2,y,lbl,transform=ax.transAxes,ha='center',fontsize=8.5,fontweight='bold',color=GOLD,va='top')
y=0.86
for ri,row in enumerate(rows[1:]):
    col=COLS[names_s[ri]]
    for ci,(cell,w) in enumerate(zip(row,cw)):
        ax.text(sum(cw[:ci])+w/2,y,cell,transform=ax.transAxes,ha='center',fontsize=8,color=col,va='top')
    y-=0.10

plt.savefig('outputs/negentropic_magnification.png',dpi=150,bbox_inches='tight',facecolor=DARK)
print("Saved")

class E(json.JSONEncoder):
    def default(self,o):
        if isinstance(o,(np.bool_,)): return bool(o)
        if isinstance(o,np.integer): return int(o)
        if isinstance(o,np.floating): return float(o)
        if isinstance(o,np.ndarray): return o.tolist()
        return super().default(o)

out={n:{'mean_neg':r['mean_neg'],'peak_neg':r['peak_neg'],'mean_W':r['mean_W']} for n,r in results.items()}
out['best']=best; out['best_neg']=results[best]['mean_neg']; out['baseline']=base; out['mult']=results[best]['mean_neg']/base
with open('outputs/negentropic_magnification.json','w') as f: json.dump(out,f,indent=2,cls=E)
print("JSON saved")
