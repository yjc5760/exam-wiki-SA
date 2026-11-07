import numpy as np
from beamil import beam, il
m,g,nm=beam({'A':0,'B':30,'C':45,'D':60},[(0,60,1.0)],{'A':(0,1,0),'B':(0,1,0),'D':(1,1,0)},dx=0.25)
RA=il(m,nm,g,lambda U,R,n:R[m.dof('A',1)]); RB=il(m,nm,g,lambda U,R,n:R[m.dof('B',1)]); RD=il(m,nm,g,lambda U,R,n:R[m.dof('D',1)])
MB=RA*30-np.where(g<30,30-g,0)            # 左自由體，正彎矩為正
MC=RD*15-np.where(g>45,g-45,0)            # 右自由體
VC=-RD+np.where(g>45,1,0)                 # 左側上推為正
for xi in [0,7.5,10,15,20,22.5,30,37.5,45,52.5,60]:
    i=np.argmin(abs(g-xi)); print(f"x={xi:5.1f} RA={RA[i]:8.4f} RB={RB[i]:8.4f} MB={MB[i]:8.4f} MC={MC[i]:8.4f} VC={VC[i]:8.4f}")
i45=np.argmin(abs(g-45)); print("V_C 在 C 左/右:",-RD[i45],1-RD[i45])
for nmx,arr in [('RA',RA),('RB',RB),('MB',MB),('MC',MC)]:
    print(nmx,"max",arr.max().round(4),"@",g[arr.argmax()]," min",arr.min().round(4),"@",g[arr.argmin()])
# 均布 2 kN/m：正區與負區積分
w=2; dx=np.diff(g)
def integ(arr,mask):
    a=np.where(mask,arr,0); return np.trapezoid(a,g)
pos=integ(MC,MC>0); neg=integ(MC,MC<0)
print("M_C 影響線 正面積",pos,"負面積",neg," → M_C,max+ =",w*pos," M_C,max- =",w*neg," 全跨 =",w*np.trapezoid(MC,g))
# 零點
s=np.where(np.diff(np.sign(MC))!=0)[0]; print("M_C 零點附近 x:",g[s])
