import numpy as np, sympy as sp
def truss(nodes, mem, sup, loads, EA, springs=None, active=None):
    nm=list(nodes); ix={n:i for i,n in enumerate(nm)}; nd=2*len(nm)
    K=np.zeros((nd,nd)); F=np.zeros(nd)
    info=[]
    for k,(a,b) in enumerate(mem):
        (x1,y1),(x2,y2)=nodes[a],nodes[b]; L=np.hypot(x2-x1,y2-y1); c,s=(x2-x1)/L,(y2-y1)/L
        ea=EA[k] if hasattr(EA,'__len__') else EA
        if active is not None and not active[k]: ea=0
        v=np.array([-c,-s,c,s]); d=[2*ix[a],2*ix[a]+1,2*ix[b],2*ix[b]+1]
        K[np.ix_(d,d)]+=ea/L*np.outer(v,v); info.append((v,d,L,ea))
    for n,(fx,fy) in loads.items(): F[2*ix[n]]+=fx; F[2*ix[n]+1]+=fy
    for n,(kx,ky) in (springs or {}).items(): K[2*ix[n],2*ix[n]]+=kx; K[2*ix[n]+1,2*ix[n]+1]+=ky
    fixed=[2*ix[n]+d for n,r in sup.items() for d in range(2) if r[d]]
    free=[i for i in range(nd) if i not in fixed]
    U=np.zeros(nd); U[free]=np.linalg.solve(K[np.ix_(free,free)],F[free])
    N=[ea/L*v@U[d] for v,d,L,ea in info]
    return U,N,K,free,info,ix

print('== SA-2005-4')
nodes={'A':(0,0),'B':(6,0),'C':(0,8),'D':(6,8)}
mem=[('A','C'),('B','D'),('C','D'),('A','D'),('B','C')]
U,N,*_=truss(nodes,mem,{'A':(1,1),'B':(1,1)},{'D':(24,0)},1e7)
for (a,b),f in zip(mem,N): print(f'  {a}{b}: N={f:+.4f} N  stress={f/10:+.4f} N/cm²')
print('  ->以 sympy 求精確')
X=sp.symbols('X')  # 取 CD 為贅餘
# 釋放 CD 後：D 節點 24 右，由 BD、AD 承擔；C 節點只有 AC、BC（CD=X）
def fs(X):
    # 節點 C：CD 拉力 X（指向 D, +x），AC（指向A,-y），BC（指向B: (6,-8)/10）
    a,b=sp.symbols('a b')  # AC, BC 拉力
    s1=sp.solve([X+b*sp.Rational(6,10), -a-b*sp.Rational(8,10)],[a,b])
    # 節點 D：外力 24 +x；CD 拉力指向 C (-x)：-X；BD 指向 B (-y)；AD 指向 A (-6,-8)/10
    c,d=sp.symbols('c d')
    s2=sp.solve([24-X-d*sp.Rational(6,10), -c-d*sp.Rational(8,10)],[c,d])
    return {'AC':s1[a],'BC':s1[b],'CD':X,'BD':s2[c],'AD':s2[d]}
f=fs(X); L={'AC':8,'BD':8,'CD':6,'AD':10,'BC':10}
Xs=sp.solve(sp.diff(sum(f[k]**2*L[k] for k in f),X),X)[0]; print('  ',{k:sp.nsimplify(v.subs(X,Xs)) for k,v in f.items()})
print('  stress N/cm²:',{k:float(v.subs(X,Xs))/10 for k,v in f.items()})

print('== SA-2012-2')
nodes={'a':(0,0),'b':(4,0),'c':(8,0),'d':(4,4)}
mem=[('a','d'),('d','c'),('d','b'),('a','b'),('b','c')]
U,N,*_=truss(nodes,mem,{'a':(1,1),'c':(0,1)},{'d':(20,-40)},1e4,springs={'b':(0,2500)})
for (a,b),f in zip(mem,N): print(f'  {a}{b}: N={f:+.4f}')
print('  spring force (up) =',-2500*U[3], ' v_b=',U[3])
# 精確：贅餘彈簧力 S（向上）
S=sp.symbols('S'); r2=sp.sqrt(2)
# 反力：c_y, a_y, a_x. a_x=-20. 對 a 取矩: c_y*8 + S*4 - 40*4 - 20*4 = 0
cy=(240-4*S)/8; ay=40-S-cy
# 節點 c：dc 拉力 t_dc 指向 d (-1,1)/√2，bc 指向 b (-x)；cy 向上
t_dc=-cy*r2; t_bc=-t_dc/r2
# 節點 a：ad 指向 d (1,1)/√2，ab 指向 b (+x)，ax=-20, ay
t_ad=-ay*r2; t_ab=-(-20)-t_ad/r2
# 節點 b：db 指向 d (+y)，S 向上，ab 指向 a, bc 指向 c
t_db=-S
ff={'ad':t_ad,'dc':t_dc,'db':t_db,'ab':t_ab,'bc':t_bc}
LL={'ad':4*r2,'dc':4*r2,'db':4,'ab':4,'bc':4}
Uc=sum(ff[k]**2*LL[k] for k in ff)/(2*10000)+S**2/(2*2500)
Ss=sp.solve(sp.diff(Uc,S),S)[0]; print('  S=',sp.nsimplify(Ss),float(Ss))
print('  ',{k:(sp.nsimplify(sp.simplify(v.subs(S,Ss))),round(float(v.subs(S,Ss)),4)) for k,v in ff.items()})
