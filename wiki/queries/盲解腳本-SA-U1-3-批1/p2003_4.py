import numpy as np
from beamil import beam, il
m,g,nm=beam({'A':0,'B':5,'C':10},[(0,10,1.0)],{'A':(1,1,1),'C':(0,1,0)})
RC=il(m,nm,g,lambda U,R,n:R[m.dof('C',1)])
RA=il(m,nm,g,lambda U,R,n:R[m.dof('A',1)])
MA=il(m,nm,g,lambda U,R,n:R[m.dof('A',2)])   # ccw +
# 閉式解
x=g; L=10; RCc=x**2*(3*L-x)/(2*L**3)
print("R_C 閉式 vs FEM 最大差", abs(RCc-RC).max())
MB=RC*5-np.where(x>5,x-5,0)          # 取右自由體，正彎矩（下緣受拉）為正
VBl=-RC+np.where(x>5,1,0)            # 左側上推為正
for xi in [0,1,2,2.5,3,4,5,6,7,7.5,8,9,10]:
    i=np.argmin(abs(g-xi)); print(f"x={xi:5.2f}  M_B={MB[i]:8.4f}  V_B={VBl[i]:8.4f}  R_C={RC[i]:.4f}")
# B 點兩側剪力
rc5=5**2*(25)/(2000); print("V_B 在 x=5 左側載重(載重在B左):",-rc5," 右側:",1-rc5)
i=np.argmax(MB); print("M_B 最大",MB.max(),"at",g[i]); print("M_B 最小",MB.min(),"at",g[np.argmin(MB)])
# 精細找 M_B 極值與 V_B 極值
xx=np.linspace(0,10,100001); rc=xx**2*(30-xx)/2000
mb=rc*5-np.where(xx>5,xx-5,0); vb=-rc+(xx>5)
print("精細 M_B max",mb.max(),xx[mb.argmax()]," min",mb.min(),xx[mb.argmin()])
print("V_B max",vb.max(),xx[vb.argmax()]," min",vb.min(),xx[vb.argmin()])
# A–B 段 M_B IL 零點? 
