"""SA-2023-1 盲解：D 沉陷 3 mm，求 F 點水平力 P 使 E 垂直位移 = 0
路徑1：單位虛載重法（sympy 手列）；路徑2：直接勁度法框架（numpy, 大 EA 近似不計軸向變形）"""
import sympy as sp, numpy as np
EI=20000.0; dD=-3e-3  # D 向下 (m)
P,x=sp.symbols('P x')
# --- 路徑1 ---
# 真實載重 P(向右, F 在 (6,4))：R_B=-P/2(向下), R_D=+P/2, H_D=-P
# 正彎矩=梁下緣受拉
M_BC=-P/2*(x-2); M_CD=P/2*(10-x)
# 虛擬：E 點單位向下力：R_B=-0.25, R_D=1.25
m_BC=-sp.Rational(1,4)*(x-2); m_CD=-sp.Rational(1,4)*(x-2); m_DE=-(12-x)
I=sp.integrate(M_BC*m_BC,(x,2,6))+sp.integrate(M_CD*m_CD,(x,6,10))
settle=-(sp.Rational(5,4))*dD           # -ΣR̄Δ, R̄_D=1.25 向上, Δ_D=-3mm
vE=settle+I/EI                             # 向下為正
Psol=sp.solve(sp.Eq(vE,0),P)[0]
print("路徑1: ∫Mm =",sp.simplify(I),"  沉陷項 =",settle*1e3,"mm")
print("路徑1: P =",float(Psol),"kN (正=向右)")
# --- 路徑2：直接勁度法 ---
EA=1e10
nodes={'A':(0,0),'B':(2,0),'C':(6,0),'D':(10,0),'E':(12,0),'F':(6,4)}
names=list(nodes); idx={n:i for i,n in enumerate(names)}
elems=[('A','B'),('B','C'),('C','D'),('D','E'),('C','F')]
def kglob(p1,p2):
    (x1,y1),(x2,y2)=p1,p2;L=np.hypot(x2-x1,y2-y1);c=(x2-x1)/L;s=(y2-y1)/L
    k=np.array([[EA/L,0,0,-EA/L,0,0],[0,12*EI/L**3,6*EI/L**2,0,-12*EI/L**3,6*EI/L**2],
       [0,6*EI/L**2,4*EI/L,0,-6*EI/L**2,2*EI/L],[-EA/L,0,0,EA/L,0,0],
       [0,-12*EI/L**3,-6*EI/L**2,0,12*EI/L**3,-6*EI/L**2],[0,6*EI/L**2,2*EI/L,0,-6*EI/L**2,4*EI/L]])
    T=np.zeros((6,6));R=np.array([[c,s,0],[-s,c,0],[0,0,1]]);T[:3,:3]=R;T[3:,3:]=R
    return T.T@k@T
n=3*len(names);K=np.zeros((n,n))
for a,b in elems:
    d=[3*idx[a],3*idx[a]+1,3*idx[a]+2,3*idx[b],3*idx[b]+1,3*idx[b]+2]
    K[np.ix_(d,d)]+=kglob(nodes[a],nodes[b])
fixed={3*idx['B']+1:0.0,3*idx['D']:0.0,3*idx['D']+1:dD}
free=[i for i in range(n) if i not in fixed]
def solve(Pv):
    F=np.zeros(n);F[3*idx['F']]=Pv
    u=np.zeros(n)
    for i,v in fixed.items():u[i]=v
    fi=np.array(free);ci=np.array(list(fixed))
    u[fi]=np.linalg.solve(K[np.ix_(fi,fi)],F[fi]-K[np.ix_(fi,ci)]@u[ci]);return u
u0=solve(0)[3*idx['E']+1]; u1=solve(1)[3*idx['E']+1]-u0
P2=-u0/u1
print("路徑2: vE(只沉陷)=%.4f mm, ∂vE/∂P=%.6f mm/kN, P=%.4f kN"%(u0*1e3,u1*1e3,P2))
u=solve(P2);print("驗算 vE=%.2e m, uF=%.3f mm"%(u[3*idx['E']+1],u[3*idx['F']]*1e3))
