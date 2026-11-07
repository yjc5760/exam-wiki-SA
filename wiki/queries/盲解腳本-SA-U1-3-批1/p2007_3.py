import numpy as np
from fem import Model
from truck import maxeff
m=Model()
P={'A':(0,0),'B':(48,0),'E':(0,17),'F':(12,17),'G':(24,17),'H':(36,17),'I':(48,17),'C':(12,12),'D':(36,12)}
for k,(x,y) in P.items(): m.node(k,x,y)
mem=[('E','F'),('F','G'),('G','H'),('H','I'),('A','E'),('I','B'),('F','C'),('H','D'),('A','C'),('E','C'),('C','G'),('G','D'),('D','I'),('D','B')]
for a,b in mem: m.truss(a,b)
m.support('A',1,1); m.support('B',1,1)
top=['E','F','G','H','I']; xs=np.array([P[n][0] for n in top])
iFG=mem.index(('F','G'))
Ay=[];Ax=[];FG=[]
for n in top:
    U,R,f=m.solve([(n,0,-1,0)]); Ay.append(R[m.dof('A',1)]); Ax.append(R[m.dof('A',0)]); FG.append(f[iFG])
Ay,Ax,FG=map(np.array,(Ay,Ax,FG))
print("x:",xs); print("A_y:",Ay.round(5)); print("A_x(向右+):",Ax.round(5)); print("F_FG(拉+):",FG.round(5))
# 靜定檢查：EA 改變不影響
f=lambda arr:(lambda x: np.interp(x,xs,arr) if 0<=x<=48 else 0.0)
print("A_y:",maxeff(f(Ay),0,48))
print("A_x:",maxeff(f(Ax),0,48))
print("F_FG:",maxeff(f(FG),0,48))
# 合力：在同一車位求 sqrt(Ax^2+Ay^2) 最大
from truck import W,OFF
best=(0,0)
for xh in np.arange(-6,48.001,0.005):
    ay=sum(w*f(Ay)(xh+o) for w,o in zip(W,OFF)); ax=sum(w*f(Ax)(xh+o) for w,o in zip(W,OFF))
    r=np.hypot(ax,ay)
    if r>best[0]: best=(r,xh,ax,ay)
print("合力最大:",best)
