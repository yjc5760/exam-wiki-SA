import numpy as np
from fem import Model
from truck import maxeff
m=Model()
P={'a':(0,0),'b':(10,0),'c':(20,0),'d':(30,0),'e':(40,0),'B':(10,10),'C':(20,10),'D':(30,10)}
for k,(x,y) in P.items(): m.node(k,x,y)
mem=[('a','b'),('b','c'),('c','d'),('d','e'),('B','C'),('C','D'),('a','B'),('D','e'),('B','b'),('C','c'),('D','d'),('B','c'),('c','D')]
for a,b in mem: m.truss(a,b)
m.support('a',1,1); m.support('e',0,1)
ib=mem.index(('b','c'))
def nodal(chord):
    xs=[];Ra=[];Fbc=[]
    for n in chord:
        U,R,f=m.solve([(n,0,-1,0)]); xs.append(P[n][0]); Ra.append(R[m.dof('a',1)]); Fbc.append(f[ib])
    return np.array(xs),np.array(Ra),np.array(Fbc)
xb,Rab,Fb=nodal(['a','b','c','d','e'])
print("下弦受載 節點 x:",xb,"\n R_a:",Rab.round(4),"\n F_bc:",Fb.round(4))
xt,Rat,Ft=nodal(['B','C','D'])
print("上弦受載 節點 B C D:",Rat.round(4),Ft.round(4))
fR=lambda x: np.interp(x,xb,Rab) if 0<=x<=40 else 0.0
fF=lambda x: np.interp(x,xb,Fb) if 0<=x<=40 else 0.0
print("R_a max/min:",maxeff(fR,0,40))
print("F_bc max/min:",maxeff(fF,0,40))
# 也算其他桿件 IL 供參考
