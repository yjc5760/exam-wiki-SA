"""SA-2019-2 范倫迪爾桁架近似分析（各構件中點反曲點＝鉸）
路徑1：以「節點塊＋中點鉸」建立全部平衡方程，numpy 最小平方求解並檢查一致性/秩
路徑2：逐格切面手算（sympy），上下弦剪力由節點塊平衡決定"""
import numpy as np, sympy as sp
P={'A':(0,0),'B':(4,0),'C':(8,0),'D':(12,0),'E':(16,0),
   'F':(0,6),'G':(4,6),'H':(8,6),'I':(12,6),'J':(16,6)}
mem=[('A','B'),('B','C'),('C','D'),('D','E'),('F','G'),('G','H'),('H','I'),('I','J'),
     ('A','F'),('B','G'),('C','H'),('D','I'),('E','J')]
nodes=list(P); idx={n:k for k,n in enumerate(nodes)}
nu=2*len(mem)+3; A=np.zeros((30,nu)); b=np.zeros(30)
def add(n,col,f,arm):  # force vector f (per unit unknown) at point arm rel. to node n
    r=3*idx[n]; A[r,col]+=f[0]; A[r+1,col]+=f[1]; A[r+2,col]+=arm[0]*f[1]-arm[1]*f[0]
for k,(i,j) in enumerate(mem):
    m=np.add(P[i],P[j])/2
    for c,f in ((2*k,(1,0)),(2*k+1,(0,1))):
        add(i,c,f,m-np.array(P[i])); add(j,c,(-f[0],-f[1]),m-np.array(P[j]))
add('A',nu-3,(1,0),(0,0)); add('A',nu-2,(0,1),(0,0)); add('E',nu-1,(0,1),(0,0))
for n in 'BCD': b[3*idx[n]+1]=+100   # A x + load = 0 -> A x = -load ; load (0,-100)
x,res,rank,_=np.linalg.lstsq(A,b,rcond=None)
print('rank',rank,'unknowns',nu,'residual',np.linalg.norm(A@x-b))
# null space (indeterminate part)?
U,S,Vt=np.linalg.svd(A); print('smallest sing',S[-3:])
for k,(i,j) in enumerate(mem):
    Hx,Hy=x[2*k],x[2*k+1]   # force on piece i (from j side) at midpoint
    L=np.hypot(*np.subtract(P[j],P[i])); e=np.subtract(P[j],P[i])/L
    # internal forces at hinge, member i->j: force on i-side part from j-side part = (Hx,Hy)
    N=Hx*e[0]+Hy*e[1]            # tension +
    V=-Hx*e[1]+Hy*e[0]           # shear (on i-part, perpendicular left)
    Mi= (L/2)*V                  # moment at end i from hinge force (ccw on piece about i)
    print(f'{i}{j}: N={N:8.2f} (+拉)  V={V:8.2f}  |M_end|={abs(Mi):7.2f}  M_i(ccw on joint piece)={Mi:8.2f}')
print('reactions Ax,Ay,Ey',x[-3:])

# ---- 路徑2：逐格切面＋上弦節點塊（手算鏈）----
print('\n== 路徑2 ==')
Ay=Ey=sp.Rational(150); xs=[2,6,10,14]
Vp=[Ay-100*sum(1 for xl in (4,8,12) if xl<xc) for xc in xs]          # 各格總剪力
Mp=[Ay*xc-sum(100*(xc-xl) for xl in (4,8,12) if xl<xc) for xc in xs] # 格中點彎矩
Nt=[-m/6 for m in Mp]; Nb=[m/6 for m in Mp]                          # 上弦壓、下弦拉
# 上弦節點塊 F,G,H,I,J：腹桿中點剪力 = 相鄰上弦軸力差；彎矩平衡：腹桿上端彎矩 3*Hv = 2*(Vt_左+Vt_右)
Vt=sp.symbols('vt1:5'); Ntx=[0]+Nt+[0]
Hv=[Ntx[k+1]-Ntx[k] for k in range(5)]          # F..J 腹桿水平剪力（取絕對大小用）
eqs=[sp.Eq(3*abs(Hv[0]),2*Vt[0])]+[sp.Eq(3*abs(Hv[k]),2*(Vt[k-1]+Vt[k])) if k in (1,) else None for k in range(1,2)]
eqs=[e for e in eqs if e is not None]
# 對稱：vt4=vt1, vt3=vt2
sol=sp.solve(eqs+[sp.Eq(Vt[3],Vt[0]),sp.Eq(Vt[2],Vt[1])],Vt)
print('Vpanel',Vp,'Mmid',Mp); print('N_top',Nt,'N_bot',Nb); print('vertical shear',Hv); print('Vt',sol)
print('Vb = Vpanel - Vt:',[Vp[k]-sol[Vt[k]]*sp.sign(Vp[k]) for k in range(4)])
