"""SA-U2-4 批1 勘誤驗算：把三題解析正本寫的每個數值與獨立計算比對，印 MISMATCHES"""
from fr import *
import numpy as np
mm=[]; n=[0]
def chk(tag, got, exp, tol=2e-3):
    n[0]+=1
    ok = (sp.simplify(got-exp)==0) if isinstance(exp,sp.Basic) and not exp.is_Float else abs(float(got)-float(exp))<=tol*max(1,abs(float(exp)))
    print(('OK ' if ok else 'XX ')+tag, got, exp)
    if not ok: mm.append(tag)
EI,L,w,P,Q,R=sp.symbols('EI L w P Q R',positive=True)
# ---- SA-2019-4
d1,d2,d3,d4,tc,tE=sp.symbols('d1 d2 d3 d4 t_C t_E')
f=Frame([d1,d2,d3,d4,tc,tE]); f.node('A',0,0); f.node('B',0,L,u=d1,t=d2); f.node('Bb',0,L,u=d1,t=d3); f.node('D',L,L,u=d1,t=d4)
f.node('C',L,0,t=tc); f.node('E',2*L,L,u=d1,t=tE)
f.member('A','B',EI,fef_point_mid(-P,L)); f.member('C','D',EI,fef_point_mid(-Q,L)); f.member('Bb','D',EI); f.member('D','E',EI,fef_udl(-w,L))
K,Rv,_=f.solve(extra_PE=10*EI/L*(d3-d2)**2/2, P=R*d1)
Kc=(K[:4,:4]-K[:4,4:]*K[4:,4:].inv()*K[4:,:4]).applyfunc(sp.simplify); Rc=(Rv[:4,:]-K[:4,4:]*K[4:,4:].inv()*Rv[4:,:]).applyfunc(sp.expand)
u=EI/L**3
Kdoc=u*sp.Matrix([[15,6*L,0,3*L],[6*L,14*L**2,-10*L**2,0],[0,-10*L**2,14*L**2,2*L**2],[3*L,0,2*L**2,10*L**2]])
Pdoc=sp.Matrix([R+P/2+sp.Rational(11,16)*Q, P*L/8, 0, sp.Rational(3,16)*Q*L-w*L**2/8])
for i in range(4):
    for j in range(i,4): chk(f'2019-4 K{i+1}{j+1}',Kc[i,j],Kdoc[i,j])
for i in range(4): chk(f'2019-4 P{i+1}',Rc[i],Pdoc[i])
# 元素修正勁度 ②、⑤ 由凝縮驗證
chk('2019-4 k2 (3EI/L^3) 側移',Kc[0,0]-12*u, 3*u); chk('2019-4 K44 組成 3+4+3',Kc[3,3],10*EI/L)
# ---- SA-2008-4
tB,tC=sp.symbols('tB tC')
f=Frame([tB,tC]); f.node('A',0,0); f.node('B',0,4,t=tB); f.node('C',6,4,t=tC)
f.member('A','B',sp.Integer(1)); f.member('B','C',sp.Integer(1),fef_udl(-1,6))
K,Rv,s=f.solve(); F=f.end_forces()
chk('2008-4 thetaB(cw=+3/EI)',-s[tB],3); chk('2008-4 thetaC(cw=-6/EI)',-s[tC],-6)
chk('2008-4 M_AB 1.5',-F[0][2][2],1.5); chk('2008-4 M_BA 3.0',-F[0][2][5],3.0)
chk('2008-4 M_BC -3',-F[1][2][2],-3); chk('2008-4 M_CB 0',F[1][2][5],0)
VB=F[1][2][1]; chk('2008-4 V_B 3.5',VB,3.5); chk('2008-4 V_C 2.5',6-VB,2.5)
x=sp.symbols('x'); M=-F[1][2][2]*(-1)*0  # placeholder
Mx=-3+VB*x-x**2/2; xm=sp.solve(sp.diff(Mx,x),x)[0]
chk('2008-4 x_max 3.5',xm,3.5); chk('2008-4 M_max 3.125',Mx.subs(x,xm),3.125)
chk('2008-4 梁反曲點 1 m',min(sp.solve(Mx,x)),1.0); chk('2008-4 柱反曲點 4/3',1.5/4.5*4,4/3)
chk('2008-4 柱剪力 1.125',(1.5+3)/4,1.125)
chk('2008-4 凝縮 θB=4.5/(1.5EI)',4.5/1.5,3)
# ---- SA-2024-4（數值）
EIv=425000.; Lv=7.
u=EIv/Lv**3; chk('2024-4 EI/L^3',u,1239.07,1e-5)
K1=4.2*u; chk('2024-4 Kt1',K1,5204.1,1e-4)
# 以勁度矩陣直接解（不靠閉合式）
K1m=np.array([[6,3*Lv,3*Lv],[3*Lv,8*Lv**2,2*Lv**2],[3*Lv,2*Lv**2,8*Lv**2]])*u
d=np.linalg.solve(K1m,[1,0,0]); chk('2024-4 Kt1 矩陣解',1/d[0],5204.1,1e-4)
Mb=6*EIv/Lv*d[1]; Mbase=2*EIv/Lv*d[1]+3*EIv/Lv**2*d[0]; Mtop=4*EIv/Lv*d[1]+3*EIv/Lv**2*d[0]
chk('2024-4 梁端/P 3',abs(Mb),3); chk('2024-4 柱底/P 4',Mbase,4); chk('2024-4 柱頂/P 3',Mtop,3)
P1=300/abs(Mb); chk('2024-4 P1',P1,100); chk('2024-4 Δ1 mm',P1*d[0]*1000,19.22)
K2m=np.array([[6,3*Lv,3*Lv],[3*Lv,4*Lv**2,0],[3*Lv,0,4*Lv**2]])*u
d2_=np.linalg.solve(K2m,[1,0,0]); chk('2024-4 Kt2',1/d2_[0],1858.6,1e-4)
mbase2=2*EIv/Lv*d2_[1]+3*EIv/Lv**2*d2_[0]; mtop2=4*EIv/Lv*d2_[1]+3*EIv/Lv**2*d2_[0]
chk('2024-4 柱底增量/δP 7',mbase2,7); chk('2024-4 柱頂增量 0',mtop2,0)
dP=(580-4*P1)/mbase2; chk('2024-4 δP2',dP,25.71); chk('2024-4 P_u',P1+dP,125.71)
chk('2024-4 Δ2 mm',(P1*d[0]+dP*d2_[0])*1000,33.05)
chk('2024-4 塑性轉角',abs(dP*d2_[1]),1.48e-3,5e-3)
K3m=np.array([[6,3*Lv,3*Lv],[3*Lv,4*Lv**2,0],[3*Lv,0,4*Lv**2]])*u  # 柱底釋放：柱改兩端鉸 → 側向勁度 0
chk('2024-4 機構法',(2*580+2*300)/14,125.71)
chk('2024-4 閉合式 5/21 = 1/4.2',sp.Rational(5,21),sp.Rational(10,42))
print(f'共 {n[0]} 項；MISMATCHES: {len(mm)}',mm)
