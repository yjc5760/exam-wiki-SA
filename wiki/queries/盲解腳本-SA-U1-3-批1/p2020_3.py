import numpy as np
from beamil import beam, il
m,g,nm=beam({'a':0,'b':2,'c':4,'d':7},[(0,4,1.0),(4,7,1.5)],
            {'a':(1,1,0),'b':(0,1,0),'d':(1,1,1)},hinges=('c',),dx=0.05)
Rb=il(m,nm,g,lambda U,R,n:R[m.dof('b',1)])
for xi in [0,1,2,2.5,3,3.5,4,5,6,7]:
    i=np.argmin(abs(g-xi)); print(f"x={xi:4.1f}  R_b={Rb[i]:.5f}")
print("max",Rb.max(),"@",g[Rb.argmax()]," min",Rb.min(),"@",g[Rb.argmin()])
# 解析：c 端彈簧 k_c = 3(1.5EI)/27 = EI/6 ；細找極值
from scipy.optimize import minimize_scalar
m,g,nm=beam({'a':0,'b':2,'c':4,'d':7},[(0,4,1.0),(4,7,1.5)],{'a':(1,1,0),'b':(0,1,0),'d':(1,1,1)},hinges=('c',),dx=0.01)
sel=[n for n,x in zip(nm,g) if 2.8<=x<=3.2]
v=[(m.nodes[n][0],m.solve([(n,0,-1,0)])[1][m.dof('b',1)]) for n in sel]
x,r=max(v,key=lambda t:t[1]); print("細網格 max",r,"@",x, " 19/17=",19/17," 18/17=",18/17)
