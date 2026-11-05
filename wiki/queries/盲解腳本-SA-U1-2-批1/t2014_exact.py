import sympy as sp, numpy as np
# 2014-1 ID exact
P=sp.Symbol('P')
nd={'A':(0,0),'B':(12,0),'C':(24,0),'D':(36,0),'E':(48,0),'F':(60,0),'G':(72,0),'H':(12,12),'I':(24,17),'J':(36,22),'K':(48,17),'L':(60,12)}
mem=[tuple(s) for s in 'AH HI IJ JK KL LG AB BC CD DE EF FG BH CI DJ EK FL HC ID KD LE'.split()]
names=list(nd); idx={n:i for i,n in enumerate(names)}
F=sp.symbols('f0:21'); R=sp.symbols('Ax Ay Gy')
eqs=[sp.Integer(0)]*24
for k,(i,j) in enumerate(mem):
    xi,yi=nd[i]; xj,yj=nd[j]; L=sp.sqrt((xj-xi)**2+(yj-yi)**2)
    ux,uy=sp.Rational(xj-xi)/L,sp.Rational(yj-yi)/L
    eqs[2*idx[i]]+=F[k]*ux; eqs[2*idx[i]+1]+=F[k]*uy; eqs[2*idx[j]]-=F[k]*ux; eqs[2*idx[j]+1]-=F[k]*uy
eqs[0]+=R[0]; eqs[1]+=R[1]; eqs[2*idx['G']+1]+=R[2]; eqs[2*idx['C']+1]-=P
s=sp.solve(eqs,list(F)+list(R))
for n in ['CD','ID','IJ']:
    k=mem.index(tuple(n)); print(n, sp.nsimplify(sp.simplify(s[F[k]])), sp.N(s[F[k]]))
