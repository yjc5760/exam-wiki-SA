import numpy as np
from beamil import beam, il
m,g,nm=beam({'A':0,'B':10,'D':15,'C':20},[(0,20,1.0)],{'A':(0,1,0),'B':(1,1,0),'C':(0,1,0)})
RA=il(m,nm,g,lambda U,R,n:R[m.dof('A',1)]); RB=il(m,nm,g,lambda U,R,n:R[m.dof('B',1)])
RC=il(m,nm,g,lambda U,R,n:R[m.dof('C',1)])
MD=RC*5-np.where(g>15,g-15,0)   # 右自由體，正彎矩為正
for xi in np.arange(0,20.01,2.5):
    i=np.argmin(abs(g-xi)); print(f"x={xi:5.1f}  M_D={MD[i]:8.4f}  R_C={RC[i]:.5f}")
# 閉式：載重在 AB 跨（x<10）時 R_C = -x(100-x^2)/(4000)? 驗證
x=np.arange(0,10.01,2.5); print("AB 跨 閉式 R_C:",(-x*(100-x**2)/4000).round(5))
print("max",MD.max(),g[MD.argmax()],"min",MD.min(),g[MD.argmin()])
