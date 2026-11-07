import numpy as np
from fem import Model
BIG=1e10
m=Model(); nA=m.node(0,0); nD=m.node(6,0); nB=m.node(12,0); nC=m.node(0,4.5)
m.frame(nA,nD,BIG,1e4,-8); m.frame(nD,nB,BIG,1e4,-8); m.truss(nC,nD,4e4)
m.solve({(nA,0),(nA,1),(nA,2),(nB,1),(nC,0),(nC,1)})
xs=np.linspace(0,6,60001)
for e,off in ((0,0),(1,6)):
    M=np.array([m.moment_at(e,t) for t in xs]); i=M.argmax(); print('elem',e,'Mmax+',M[i],'at',off+xs[i], 'zeros', [round(off+xs[k],3) for k in range(1,len(M)) if M[k-1]*M[k]<0])
print('MA',m.moment_at(0,0),'MD',m.moment_at(0,6),'vD mm',m.U[m.dof[nD][1]]*1e3, 'Ax',m.R[m.dof[nA][0]],'Ay',m.R[m.dof[nA][1]])
m=Model(); nc=m.node(0,0); nb=m.node(0,6); na=m.node(0,10); nd=m.node(100,10)
m.frame(nc,nb,BIG,1000,1); m.frame(nb,na,BIG,1000,1); m.truss(na,nd,1000)
m.solve({(nc,0),(nc,1),(nc,2),(nd,0),(nd,1)})
print('2009-2 Mc', m.R[m.dof[nc][2]], 'Hc', m.R[m.dof[nc][0]])
