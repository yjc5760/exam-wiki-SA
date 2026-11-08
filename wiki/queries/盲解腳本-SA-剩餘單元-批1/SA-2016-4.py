# SA-2016-4: zero-force members. Path1 = joint inspection + compatibility argument (see md).
# Path2: direct stiffness of whole structure with random EA per member and random k; beam MNO
# modeled as simply supported (M pin, O roller) -> vertical spring k_b at N (horizontal fixed by M pin via axially rigid beam).
import numpy as np
rng=np.random.default_rng(0)
X={'A':(1,2),'B':(2,2),'C':(3,2),'D':(0,1),'E':(1,1),'F':(2,1),'G':(3,1),'H':(4,1),
   'I':(2,0),'J':(3,0),'K':(2,-1),'L':(3,-1),'P':(5,-1),'N':(5,0.37)}
mem=['AB','BC','AD','AE','AF','BF','CF','CG','CH','DE','EF','FG','GH','FI','GJ','IJ','FJ','GI',
     'IK','JL','KL','IL','JK','LP','NP']
nodes=list(X); idx={n:i for i,n in enumerate(nodes)}; nd=2*len(nodes)
fixed={'A':(0,1),'C':(0,1),'D':(0,1),'N':(0,)}   # N: horizontal restrained by beam (axially rigid, pinned at M)
for trial in range(5):
    EA={m:rng.uniform(0.5,3) for m in mem}; k=rng.uniform(0.01,5); kb=rng.uniform(0.01,5)
    K=np.zeros((nd,nd)); F=np.zeros(nd)
    for m in mem:
        i,j=m; d=np.subtract(X[j],X[i]); L=np.hypot(*d); u=d/L; kk=EA[m]/L*np.outer(u,u)
        dof=[2*idx[i],2*idx[i]+1,2*idx[j],2*idx[j]+1]; K[np.ix_(dof,dof)]+=np.block([[kk,-kk],[-kk,kk]])
    K[2*idx['H']+1,2*idx['H']+1]+=k        # spring H-M, M is a pinned (fixed) point
    # beam: load 100 kN down at N; beam flexibility at N -> spring kb; beam alone gives reaction at N = 0 force
    # equivalently: apply 100 down at N on node with vertical spring kb (beam's own stiffness carries it).
    K[2*idx['N']+1,2*idx['N']+1]+=kb
    for n,(fx,fy) in {'A':(100,0),'D':(100,0),'E':(0,-100),'N':(0,-100)}.items():
        F[2*idx[n]]+=fx; F[2*idx[n]+1]+=fy
    fx=[2*idx[n]+c for n,cs in fixed.items() for c in cs]; free=[q for q in range(nd) if q not in fx]
    U=np.zeros(nd); U[free]=np.linalg.solve(K[np.ix_(free,free)],F[free])
    N={}
    for m in mem:
        i,j=m; d=np.subtract(X[j],X[i]); L=np.hypot(*d); u=d/L
        N[m]=EA[m]/L*u@(U[2*idx[j]:2*idx[j]+2]-U[2*idx[i]:2*idx[i]+2])
    nz={m:round(v,6) for m,v in N.items() if abs(v)>1e-8}
    print(f"trial{trial}: nonzero members {nz}; spring force={k*U[2*idx['H']+1]:.2e}; "
          f"zero count={sum(abs(v)<1e-8 for v in N.values())}/{len(mem)}")
