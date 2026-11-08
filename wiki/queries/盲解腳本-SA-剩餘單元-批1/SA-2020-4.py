"""SA-2020-4 構架＋剪力牆＋連桿
路徑1：樓層側向勁度（剛性梁→柱 12EI/h^3）＋牆勁度相加，sympy 解
路徑2：2D 構架有限元素（柱梁元素，梁 I 取極大，連桿取極大 EA 桁架），牆以給定 2x2 勁度接在 c、f"""
import numpy as np, sympy as sp
EI=81920.; h=3.2; L=3.2
# 路徑1
k=12*EI/h**3; print('單柱 12EI/h^3 =',k)
Kf=sp.Matrix([[2*k,-2*k],[-2*k,4*k]]); Kw=30000*sp.Matrix([[1,-2],[-2,6]])
D=(Kf+Kw).LUsolve(sp.Matrix([60,60])); print('Δ1,Δ2 (m)=',list(D))
Fw=Kw*D; print('牆受力 F1,F2 =',list(Fw),'基底剪力=',sum(Fw))
V_eh=k*D[1]; M=6*EI*D[1]/h**2
print('eh 剪力',V_eh,' 端彎矩(順時針正) M_eh=M_he=',-M)
# 路徑2 FE
nodes={'a':(0,6.4),'b':(3.2,6.4),'d':(0,3.2),'e':(3.2,3.2),'g':(0,0),'h':(3.2,0),'c':(4.2,6.4),'f':(4.2,3.2)}
idx={n:i for i,n in enumerate(nodes)}; N=3*len(nodes)
K=np.zeros((N,N))
def frame(n1,n2,EI_,EA):
    x1,y1=nodes[n1];x2,y2=nodes[n2];l=np.hypot(x2-x1,y2-y1);c=(x2-x1)/l;s=(y2-y1)/l
    kl=np.array([[EA/l,0,0,-EA/l,0,0],[0,12*EI_/l**3,6*EI_/l**2,0,-12*EI_/l**3,6*EI_/l**2],
      [0,6*EI_/l**2,4*EI_/l,0,-6*EI_/l**2,2*EI_/l],[-EA/l,0,0,EA/l,0,0],
      [0,-12*EI_/l**3,-6*EI_/l**2,0,12*EI_/l**3,-6*EI_/l**2],[0,6*EI_/l**2,2*EI_/l,0,-6*EI_/l**2,4*EI_/l]])
    T=np.zeros((6,6));R=np.array([[c,s,0],[-s,c,0],[0,0,1]]);T[:3,:3]=R;T[3:,3:]=R
    dof=[3*idx[n1],3*idx[n1]+1,3*idx[n1]+2,3*idx[n2],3*idx[n2]+1,3*idx[n2]+2]
    K[np.ix_(dof,dof)]+=T.T@kl@T; return dof,T,kl
BIG=1e9
els={}
for e in [('g','d'),('d','a'),('h','e'),('e','b')]: els[e]=frame(*e,EI,BIG)
for e in [('a','b'),('d','e')]: els[e]=frame(*e,BIG,BIG)
for e in [('b','c'),('e','f')]: els[e]=frame(*e,0.0,BIG)   # 連桿：只有軸向
kw=30000*np.array([[1,-2],[-2,6]]); wd=[3*idx['c'],3*idx['f']]
K[np.ix_(wd,wd)]+=kw
F=np.zeros(N);F[3*idx['a']]=60;F[3*idx['d']]=60
fixed=[3*idx[n]+i for n in 'gh' for i in range(3)]
# c、f：牆端只有水平自由度，垂直與轉角固定（牆不計軸向；連桿 EI=0 不傳彎矩）
fixed+= [3*idx[n]+i for n in 'cf' for i in (1,2)]
free=[i for i in range(N) if i not in fixed]
u=np.zeros(N);u[free]=np.linalg.solve(K[np.ix_(free,free)],F[free])
print('FE Δ1=',u[3*idx['c']],' Δ2=',u[3*idx['f']])
for e in [('b','c'),('e','f')]:
    dof,T,kl=els[e];f=kl@T@u[dof];print('連桿',e,'軸力(拉為正)=',round(-f[0],4))
Fw2=kw@u[wd];print('牆 F=',Fw2,'基底剪力',Fw2.sum())
dof,T,kl=els[('h','e')];f=kl@T@u[dof]
print('柱 he 局部端力 [N,V,M]_h=',np.round(f[:3],4),' _e=',np.round(f[3:],4),'(M 逆時針正)')
