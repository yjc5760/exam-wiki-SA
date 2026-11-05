from fr import *
import numpy as np
EI,L,w,P,Q,R=sp.symbols('EI L w P Q R',positive=True)
print("== SA-2019-4")
d1,d2,d3,d4,tc,tE=sp.symbols('d1 d2 d3 d4 t_C t_E')
f=Frame([d1,d2,d3,d4,tc,tE])
f.node('A',0,0); f.node('B',0,L,u=d1,t=d2); f.node('Bb',0,L,u=d1,t=d3); f.node('D',L,L,u=d1,t=d4)
f.node('C',L,0,t=tc); f.node('E',2*L,L,u=d1,t=tE)
f.member('A','B',EI,fef_point_mid(-P,L))      # 柱局部 y 指向左；向右載重 = 局部 -y
f.member('C','D',EI,fef_point_mid(-Q,L))
f.member('Bb','D',EI); f.member('D','E',EI,fef_udl(-w,L))
K,Rv,s=f.solve(extra_PE=10*EI/L*(d3-d2)**2/2, P=R*d1)
# 凝縮 t_C, t_E
Kaa,Kab,Kbb=K[:4,:4],K[:4,4:],K[4:,4:]
Kc=sp.simplify(Kaa-Kab*Kbb.inv()*Kab.T); Rc=sp.simplify(Rv[:4,:]-Kab*Kbb.inv()*Rv[4:,:])
print(' [K] (d1 右, d2 d3 d4 逆時針) ='); sp.pprint(sp.simplify(Kc/(EI/L**3)).applyfunc(lambda e: sp.factor(e)))
print('  ×EI/L^3 ; {P}='); sp.pprint(sp.expand(Rc))
print("== SA-2022-4")
EIv=97200.; h=3.6; k1=12*EIv/h**3; k2=12*EIv/(2*h)**3
Kn=np.array([[2*k1+2*k1,-2*k1,0],[-2*k1,2*k1+2*k2+4*k1,-4*k1],[0,-4*k1,4*k1]])
Fn=np.array([100,200,300.]); u=np.linalg.solve(Kn,Fn)
print(' k1=',k1,' k2=',k2,' u_b,u_c,u_d (m)=',u, ' mm=',u*1000)
Va=k1*u[0]; Ma=6*EIv/h**2*u[0]; Vm=k2*u[1]; Mm=6*EIv/(2*h)**2*u[1]
print(' a: V=',Va,' M=',Ma,'  m: V=',Vm,' M=',Mm, ' 檢核 ΣV=2Va+2Vm=',2*Va+2*Vm)
