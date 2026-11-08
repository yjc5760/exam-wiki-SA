"""SA-2021-4 剛性樓板單層，路徑1：剛心法；路徑2：樓板原點 3x3 直接勁度（numpy）"""
import numpy as np
h=3.6; EId,EIe=9720.,48600.
kd,ke=12*EId/h**3,12*EIe/h**3
cols={'C1':(-3,-2,kd),'C2':(3,-2,ke),'C3':(-3,2,kd),'C4':(3,2,ke)}
P={'C1':27,'C2':27,'C3':27,'C4':27}
print('k_d,k_e =',kd,ke)
# 路徑1 剛心法
K=sum(c[2] for c in cols.values())
xr=sum(c[0]*c[2] for c in cols.values())/K; yr=sum(c[1]*c[2] for c in cols.values())/K
Fy=sum(P.values()); xF=sum(cols[k][0]*P[k] for k in P)/Fy
Mt=Fy*(xF-xr)
Kt=sum(c[2]*((c[0]-xr)**2+(c[1]-yr)**2) for c in cols.values())
th=Mt/Kt; v=Fy/K; u=0
print(f'xr={xr} yr={yr} Mt={Mt} Kt={Kt} theta={th}')
r1={}
for n,(x,y,k) in cols.items():
    ux=u-th*(y-yr); uy=v+th*(x-xr); r1[n]=(ux,uy,k*ux,k*uy)
    print(n,f'ux={ux*1e3:.3f} mm uy={uy*1e3:.3f} mm Vx={k*ux:.3f} Vy={k*uy:.3f} kN')
# 路徑2 原點 DOF (u,v,th)，每柱 x、y 兩向彈簧
Km=np.zeros((3,3)); F=np.zeros(3)
for n,(x,y,k) in cols.items():
    ax=np.array([1,0,-y]); ay=np.array([0,1,x])
    Km+=k*np.outer(ax,ax)+k*np.outer(ay,ay)
    F+=P[n]*ay
d=np.linalg.solve(Km,F); print('path2 d=',d)
for n,(x,y,k) in cols.items():
    ux=d[0]-y*d[2]; uy=d[1]+x*d[2]
    assert abs(ux-r1[n][0])<1e-12 and abs(uy-r1[n][1])<1e-12
    print(n,f'ux={ux*1e3:.3f} uy={uy*1e3:.3f} mm  Vx={k*ux:.3f} Vy={k*uy:.3f} kN  M_end(y-shear)={k*uy*h/2:.2f}')
print('兩路徑一致')
