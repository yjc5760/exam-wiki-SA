# SA-2017-1: path1 equilibrium (method of joints, 10x10) + unit-load virtual work; path2 direct stiffness
import numpy as np
X={'A':(0,0),'B':(0,4),'C':(0,8),'D':(3,4),'E':(6,0)}
mem=[('A','B'),('B','C'),('B','D'),('A','D'),('C','D'),('D','E')]
nodes=list(X); idx={n:i for i,n in enumerate(nodes)}
def geo(i,j):
    d=np.subtract(X[j],X[i]); L=np.hypot(*d); return L,d/L
loads={'C':(12,0),'B':(9,0)}
sup={'A':(1,1),'E':(1,1)}
def equil(ld):
    # unknowns: 6 member forces (tension +) + Ax,Ay,Ex,Ey
    A=np.zeros((10,10)); b=np.zeros(10)
    for m,(i,j) in enumerate(mem):
        L,u=geo(i,j)
        A[2*idx[i]:2*idx[i]+2,m]+=u; A[2*idx[j]:2*idx[j]+2,m]-=u
    A[0,6]=1;A[1,7]=1;A[8,8]=1;A[9,9]=1
    for n,(fx,fy) in ld.items(): b[2*idx[n]]-=fx; b[2*idx[n]+1]-=fy
    return np.linalg.solve(A,b)
s=equil(loads); N=s[:6]
print("Path1 forces (T+):",{f"{i}{j}":round(N[m],4) for m,(i,j) in enumerate(mem)},"Ax,Ay,Ex,Ey",np.round(s[6:],4))
n=equil({'C':(1,0)})[:6]
d=sum(N[m]*n[m]*geo(i,j)[0] for m,(i,j) in enumerate(mem))
print("unit-load n:",np.round(n,4)," delta_C*EA =",d)
for m,(i,j) in enumerate(mem): print(f"  {i}{j} L={geo(i,j)[0]} N={N[m]:.3f} n={n[m]:.4f} NnL={N[m]*n[m]*geo(i,j)[0]:.3f}")
# Path 2 direct stiffness, EA=1
K=np.zeros((10,10))
for i,j in mem:
    L,u=geo(i,j); k=np.outer(u,u)/L
    dof=[2*idx[i],2*idx[i]+1,2*idx[j],2*idx[j]+1]
    K[np.ix_(dof,dof)]+=np.block([[k,-k],[-k,k]])
F=np.zeros(10)
for nn,(fx,fy) in loads.items(): F[2*idx[nn]]+=fx; F[2*idx[nn]+1]+=fy
free=[k for k in range(10) if k not in (0,1,8,9)]
U=np.zeros(10); U[free]=np.linalg.solve(K[np.ix_(free,free)],F[free])
N2=[ (lambda L,u: u@ (U[2*idx[j]:2*idx[j]+2]-U[2*idx[i]:2*idx[i]+2])/L)(*geo(i,j)) for i,j in mem]
print("Path2 forces:",np.round(N2,4)); print("Path2 u_Cx*EA=",U[2*idx['C']],"u_Cy*EA=",U[2*idx['C']+1])
