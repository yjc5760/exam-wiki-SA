"""SA-2024-1 盲解：A 滾支(x=0, 受 200 kN-m 逆時針)、B 100 kN 向下(x=4)、C 內鉸(x=8)、D 固定(x=12)
求 |位移|max ≤ 40 mm 之最小 EI。
路徑1：分段積分（sympy，EI v''=M，正彎矩下緣受拉，v 向上為正）
路徑2：直接勁度法（numpy，C 內鉸以兩個獨立轉角自由度處理，細分元素取位移包絡）"""
import sympy as sp, numpy as np
x=sp.symbols('x',real=True)
# 靜力：AC 對 C 取矩 → R_A=75 kN(上)，C 鉸傳力 25 kN（作用於 CD 為向下）
RA=75; VC=25
M1=RA*x-200            # 0<x<4
M2=RA*x-200-100*(x-4)  # 4<x<8  (= 200-25x)
M3=-VC*(x-8)          # 8<x<12 (CD 懸臂，C 端受 25 kN 向下；D 端 -100)
c=sp.symbols('c1:7')
v1=sp.integrate(sp.integrate(M1,x),x)+c[0]*x+c[1]
v2=sp.integrate(sp.integrate(M2,x),x)+c[2]*x+c[3]
v3=sp.integrate(sp.integrate(M3,x),x)+c[4]*x+c[5]
eqs=[v1.subs(x,0),                       # A 位移 0
     v1.subs(x,4)-v2.subs(x,4), sp.diff(v1-v2,x).subs(x,4),  # B 連續
     v2.subs(x,8)-v3.subs(x,8),          # C 位移連續（轉角不連續）
     v3.subs(x,12), sp.diff(v3,x).subs(x,12)]   # D 固定
s=sp.solve(eqs,c); V=[sp.expand(v.subs(s)) for v in (v1,v2,v3)]   # 這是 EI*v
for i,v in enumerate(V): print("EI·v%d ="%(i+1),v)
segs=[(0,4),(4,8),(8,12)]; ext=[]
for v,(a,b) in zip(V,segs):
    cand=[a,b]+[r for r in sp.solve(sp.diff(v,x),x) if r.is_real and a<=r<=b]
    for r in cand: ext.append((float(r),float(v.subs(x,r))))
up=max(ext,key=lambda t:t[1]); dn=min(ext,key=lambda t:t[1])
print("路徑1: 最大向上 EI·v = %.4f @ x=%.4f m"%(up[1],up[0]))
print("路徑1: 最大向下 EI·v = %.4f @ x=%.4f m"%(dn[1],dn[0]))
thA=float(sp.diff(V[0],x).subs(x,0)); thCL=float(sp.diff(V[1],x).subs(x,8)); thCR=float(sp.diff(V[2],x).subs(x,8))
print("EI·θ(dv/dx): A=%.3f, C左=%.3f, C右=%.3f"%(thA,thCL,thCR))
gov=max(abs(up[1]),abs(dn[1])); print("路徑1: EI_min = %.2f kN-m²"%(gov/0.04))
# --- 路徑2 ---
EI=1.0; ne=48; L=12/ne; xs=np.linspace(0,12,ne+1)
# DOF: 每節點 v, θ；C 節點(x=8)額外一個右側轉角
iC=int(round(8/L)); ndof=2*(ne+1)+1; extra=ndof-1
def dofs(e):
    a,b=e,e+1; d=[2*a,2*a+1,2*b,2*b+1]
    if a==iC: d[1]=extra    # C 右側元素用獨立轉角
    return d
k=EI/L**3*np.array([[12,6*L,-12,6*L],[6*L,4*L*L,-6*L,2*L*L],[-12,-6*L,12,-6*L],[6*L,2*L*L,-6*L,4*L*L]])
K=np.zeros((ndof,ndof))
for e in range(ne): d=dofs(e); K[np.ix_(d,d)]+=k
F=np.zeros(ndof); F[2*int(round(4/L))]=-100; F[1]=200   # 逆時針力偶 = +θ 方向(逆時針為正, v 向上)
fix=[0,2*ne,2*ne+1]; fr=[i for i in range(ndof) if i not in fix]
u=np.zeros(ndof); u[fr]=np.linalg.solve(K[np.ix_(fr,fr)],F[fr])
# 元素內插求包絡
xx=[];vv=[]
for e in range(ne):
    d=dofs(e); q=u[d]
    for t in np.linspace(0,1,41):
        N=[1-3*t*t+2*t**3,L*(t-2*t*t+t**3),3*t*t-2*t**3,L*(-t*t+t**3)]
        xx.append(xs[e]+t*L); vv.append(np.dot(N,q))
vv=np.array(vv);xx=np.array(xx)
print("路徑2: 最大向上 EI·v = %.4f @ x=%.3f; 最大向下 EI·v = %.4f @ x=%.3f"%(vv.max(),xx[vv.argmax()],vv.min(),xx[vv.argmin()]))
print("路徑2: EI_min = %.2f kN-m²"%(max(abs(vv.max()),abs(vv.min()))/0.04))
print("路徑2: v_B=%.4f, v_C=%.4f (×1/EI)"%(u[2*int(round(4/L))],u[2*iC]))
# 精確值
xd=8-4/sp.sqrt(3); vd=sp.nsimplify(V[1].subs(x,xd)); xu=(200-sp.sqrt(30000))/75; vu=sp.simplify(V[0].subs(x,xu))
print("精確: 向下極值 x=8-4/√3, EI·v =",sp.simplify(vd),"=",float(vd),"; 向上極值 x=",sp.simplify(xu),"EI·v=",vu,"=",float(vu))
print("EI_min 精確 =",sp.simplify(-vd/sp.Rational(4,100)),"=",float(-vd/0.04))
print("v_B=",V[0].subs(x,4),"v_C=",V[1].subs(x,8))
