import numpy as np
from beamil import beam, il
m,g,nm=beam({'A':0,'B':4,'F':6,'C':8,'D':12,'E':16},[(0,16,1.0)],
            {'A':(1,1,1),'C':(0,1,0),'E':(0,1,0)},hinges=('B','D'),dx=0.5)
RA=il(m,nm,g,lambda U,R,n:R[m.dof('A',1)]); RC=il(m,nm,g,lambda U,R,n:R[m.dof('C',1)])
RE=il(m,nm,g,lambda U,R,n:R[m.dof('E',1)]); MAr=il(m,nm,g,lambda U,R,n:R[m.dof('A',2)])  # 反力矩 逆時針+
VF=RA-np.where(g<6,1,0)
print("  x    R_A     R_C     R_E   MA_react(ccw+)  M_A(正彎矩慣例)  V_F")
for xi in [0,2,4,6,8,10,12,14,16]:
    i=np.argmin(abs(g-xi)); print("%4.0f %7.3f %7.3f %7.3f %9.3f %12.3f %9.3f"%(xi,RA[i],RC[i],RE[i],MAr[i],-MAr[i],VF[i]))
i=np.argmin(abs(g-6)); print("V_F 在 F：左側",RA[i]-1,"右側",RA[i])
