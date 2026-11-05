import numpy as np
def truss(nodes, mems, free, load, EA, e0=None):
    """nodes{n:(x,y)}, mems[(i,j)], free [(n,'x'|'y')], load{(n,dir):val}, e0{mem:初始伸長量(短了->需拉長 +)}"""
    idx={k:i for i,k in enumerate(free)}; n=len(free); K=np.zeros((n,n)); F=np.zeros(n)
    for k,v in load.items(): F[idx[k]]+=v
    info=[]
    for m in mems:
        i,j=m; (x1,y1),(x2,y2)=nodes[i],nodes[j]; L=np.hypot(x2-x1,y2-y1); c,s=(x2-x1)/L,(y2-y1)/L
        dofs=[(i,'x'),(i,'y'),(j,'x'),(j,'y')]; g=np.array([-c,-s,c,s]); k=EA/L*np.outer(g,g)
        N0=EA/L*(e0 or {}).get(m,0)    # 固定狀態下的桿力（拉為正）
        for a in range(4):
            if dofs[a] in idx:
                F[idx[dofs[a]]]-= N0*g[a]   # 等效節點力 = -FEF
                for b in range(4):
                    if dofs[b] in idx: K[idx[dofs[a]],idx[dofs[b]]]+=k[a,b]
        info.append((m,L,g,dofs,N0))
    d=np.linalg.solve(K,F); D={k:d[idx[k]] for k in free}
    N={}
    for m,L,g,dofs,N0 in info:
        u=np.array([D.get(x,0) for x in dofs]); N[m]=EA/L*(g@u)+N0
    return K,F,D,N
np.set_printoptions(precision=6,suppress=True)
print("== SA-2009-4  (a 原點; AE=1000 kN)")
K,F,D,N=truss({'a':(0,0),'d':(-4,0),'b':(4,3),'c':(0,3)},[('a','d'),('a','b'),('a','c')],[('a','x'),('a','y')],{('a','y'):-100},1000)
print(K,F,D,{k:round(v,4) for k,v in N.items()})
print("== SA-2010-4  (A 原點; EA=10000 kN)")
K,F,D,N=truss({'A':(0,0),'B':(-3,-4),'C':(0,-4),'D':(4,-3)},[('B','A'),('C','A'),('D','A')],[('A','x'),('A','y')],{('A','x'):100,('A','y'):-225},10000)
print(K,F,D,{k:round(v,4) for k,v in N.items()})
print("== SA-2011-4  (C 原點; EA=1e4; AC 短 0.02 m)")
K,F,D,N=truss({'A':(3,4),'B':(0,4),'C':(0,0),'D':(6,0)},[('B','A'),('C','A'),('D','A')],[('A','x'),('A','y')],{},1e4,{('C','A'):0.02})
print(K,F,{k:v for k,v in D.items()},{k:round(v,4) for k,v in N.items()})
print("== SA-2013-4  (A 原點; EA=200e6*0.01=2e6 kN)")
EA=2e6; nodes={'A':(0,0),'B':(14,0),'D':(6,6),'C':(0,6)}; mems=[('C','D'),('A','D'),('D','B'),('A','B')]
free=[('B','x'),('D','x'),('D','y')]
K,_,_,_=truss(nodes,mems,free,{('B','x'):1},EA)
d=np.array([0.1277,0.1743,0.7055])*1e-3; P=K@d
print('K (kN/m)=\n',K,'\nK/1000 (kN/mm)=\n',K/1000,'\nP=',P)
# 桿力
idx={k:i for i,k in enumerate(free)}
for m in mems:
    i,j=m;(x1,y1),(x2,y2)=nodes[i],nodes[j];L=np.hypot(x2-x1,y2-y1);c,s=(x2-x1)/L,(y2-y1)/L
    u=[d[idx[x]] if x in idx else 0 for x in [(i,'x'),(i,'y'),(j,'x'),(j,'y')]]
    print(' ',m,'L=',round(L,4),'N=',round(EA/L*np.dot([-c,-s,c,s],u),3))
