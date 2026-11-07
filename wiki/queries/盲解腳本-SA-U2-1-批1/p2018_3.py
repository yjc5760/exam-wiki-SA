import sys; sys.path.insert(0,'.')
from fem import solve
EI=1000.;EAc=500.
nodes={'A':(0,0),'B':(5,0),'C':(10,0),'D':(15,0),'F':(5,-5),'G':(10,-5)}
els=[dict(n1='A',n2='B',EI=EI,EA=1e8*EI),dict(n1='B',n2='C',EI=EI,EA=1e8*EI),dict(n1='C',n2='D',EI=EI,EA=1e8*EI),
     dict(n1='G',n2='C',EI=EI,EA=1e8*EI),dict(n1='F',n2='B',EA=EAc,truss=True)]
U,out,R=solve(nodes,els,{'F':(1,1,1),'G':(1,1,1)},{'D':(0,-100,0)})
for nm,f,L in out: print(nm, 'N_i=%+.4f M(i)=%+.4f M(j)=%+.4f V_i=%+.4f'%(f[0],-f[2],f[5],f[1]))
print('A',U['A'],'B',U['B'],'C',U['C'],'D',U['D'])
# 閉式：BF 張力 T；C 視為不動（柱不計軸向）、C 轉角 θ。最小功
import sympy as sp
T=sp.symbols('T',positive=True)
x=sp.symbols('x')
# 梁 B–C–D：取 x 自 B 起；M(x)=T*x (B 段 0..5，正=下緣受拉?) 以自由體：BC 段 M = T·x（向下拉的 B 端…）符號以能量平方不影響
M_BC = -T*x       # B 被纜索向下拉 → B–C 段負彎矩（上緣受拉）
M_CD = -100*x     # 自 D 量起
# 柱 GC：C 處彎矩 = 梁兩側不平衡 = 100*5 - T*5（常數，柱無水平力）
M_col = 100*5 - T*5
Uc = (sp.integrate(M_BC**2,(x,0,5))+sp.integrate(M_CD**2,(x,0,5))+M_col**2*5)/(2*EI) + T**2*5/(2*EAc)
Ts=sp.solve(sp.diff(Uc,T),T); print('T_BF =',Ts,[float(t) for t in Ts])
