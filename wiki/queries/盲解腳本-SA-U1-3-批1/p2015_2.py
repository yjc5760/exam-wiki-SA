import numpy as np
from beamil import beam, il
m,g,nm=beam({'A':0,'F':15,'B':30,'C':40,'D':50,'E':80},[(0,80,1.0)],
            {'A':(1,1,0),'B':(0,1,0),'D':(0,1,0),'E':(0,1,0)},hinges=('C',),dx=0.25)
RA=il(m,nm,g,lambda U,R,n:R[m.dof('A',1)])
VF=RA-np.where(g<15,1,0)   # 左側上推為正
for xi in [0,7.5,15,22.5,30,35,40,45,50,60,65,70,80]:
    i=np.argmin(abs(g-xi)); print(f"x={xi:5.1f} R_A={RA[i]:8.5f} V_F={VF[i]:8.5f}")
i=np.argmin(abs(g-15)); print("V_F 在 F：F 左側",RA[i]-1,"  F 右側",RA[i])
i=np.argmin(abs(g-40)); print("V_F 在 C:",VF[i])
print("V_F min",VF.min(),g[VF.argmin()],"  in CDE region min",VF[g>40].min(),g[g>40][VF[g>40].argmin()],"max",VF[g>50].max(),g[g>50][VF[g>50].argmax()])
