import sympy as sp
T=sp.Symbol('T'); EA=sp.Integer(2*10**5)
nd={'A':(0,0),'B':(4,3),'C':(4,0),'D':(8,0)}
mem=[('A','B'),('B','C'),('B','D'),('A','C'),('C','D')]
e0={('B','D'):sp.Rational(-5,1000)}
uB,vB,uC,uD,vD=sp.symbols('uB vB uC uD vD')
U={'A':(0,0),'B':(uB,vB),'C':(uC,sp.Rational(-4,1000)),'D':(uD,vD)}
load={'B':(-T,0),'D':(0,-50),'C':(0,0),'A':(0,0)}
res={n:[sp.Integer(0),sp.Integer(0)] for n in nd}
N={}
for (i,j) in mem:
    dx=nd[j][0]-nd[i][0]; dy=nd[j][1]-nd[i][1]; L=sp.sqrt(dx*dx+dy*dy); c,s=sp.Rational(dx)/L,sp.Rational(dy)/L
    el=(U[j][0]-U[i][0])*c+(U[j][1]-U[i][1])*s
    N[(i,j)]=EA/L*(el-e0.get((i,j),0))
    res[i][0]+=N[(i,j)]*c; res[i][1]+=N[(i,j)]*s; res[j][0]-=N[(i,j)]*c; res[j][1]-=N[(i,j)]*s
eqs=[res['B'][0]+load['B'][0],res['B'][1],res['C'][0],res['D'][0],res['D'][1]+load['D'][1]]
sol=sp.solve(eqs,[uB,vB,uC,uD,vD])
vd=sp.simplify(sol[vD]); print('vD(T)=',vd)
Ts=sp.solve(sp.Eq(vd,0),T)[0]; print('T=',Ts,float(Ts))
for k,v in N.items(): print(k, float(v.subs(sol).subs(T,Ts)))
# also T=0 case
print('vD at T=0', float(vd.subs(T,0)))
