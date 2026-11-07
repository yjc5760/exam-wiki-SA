import numpy as np
from fem import Model
L=1.0; n=20
m=Model(); m.node('A',0,0); m.node('B',0,L)
names=['B']
for i in range(1,n+1):
    nm='C' if i==n else f"b{i}"; m.node(nm,L*i/n,L); names.append(nm)
m.frame('A','B',1.0,1e9)
for a,b in zip(names[:-1],names[1:]): m.frame(a,b,1.0,1e9)
m.support('A',1,1,1); m.support('C',0,1,0)
xs=[];RC=[]
for i,nm in enumerate(names):
    U,R,f=m.solve([(nm,0,-1,0)]); xs.append(i/n); RC.append(R[m.dof('C',1)])
xs=np.array(xs); RC=np.array(RC); cf=(6*xs+3*xs**2-xs**3)/8
print("FEM vs 閉式 最大差:",abs(RC-cf).max())
for x,r in zip(xs[::5],RC[::5]): print(f"ξ={x:.2f}  R_C={r:.5f}")
