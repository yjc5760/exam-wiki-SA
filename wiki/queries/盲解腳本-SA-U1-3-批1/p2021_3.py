import numpy as np
from fem import Model
m=Model()
P={'a':(0,0),'b':(3,0),'c':(6,0),'d':(9,0),'e':(12,0),'f':(3,4),'g':(6,4),'h':(9,4)}
for k,(x,y) in P.items(): m.node(k,x,y)
mem=[('a','b'),('b','c'),('c','d'),('d','e'),('f','g'),('g','h'),('a','f'),('h','e'),('f','b'),('g','c'),('h','d'),('b','g'),('g','d')]
for a,b in mem: m.truss(a,b,1.0)
m.support('a',1,1); m.support('e',1,1)
out=[]
for n in 'abcde':
    U,R,f=m.solve([(n,0,-1,0)])
    out.append((P[n][0],R[m.dof('a',0)],f[mem.index(('a','b'))],f[mem.index(('b','g'))],R[m.dof('a',1)]))
print(" x    H_a(向右+)   N_ab(拉+)   N_bg(拉+)   V_a")
for r in out: print("%4.0f  %10.5f  %10.5f  %10.5f  %8.4f"%r)
# 分數形式
from fractions import Fraction
for r in out: print([str(Fraction(v).limit_denominator(2000)) for v in r[1:4]])
