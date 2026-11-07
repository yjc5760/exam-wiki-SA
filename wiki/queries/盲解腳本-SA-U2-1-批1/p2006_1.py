import sympy as sp
X,Hg=sp.symbols('X H'); EI,EA=sp.symbols('EI EA',positive=True)
x=sp.symbols('x')
RB=10-sp.Rational(3,2)*X; RD=10+X/2
segs=[(0,10,X*x),(10,15,X*x+RB*(x-10)),(15,25,X*x+RB*(x-10)-10*(x-15)),(25,30,X*x+RB*(x-10)-10*(x-15)-10*(x-25))]
Ub=sum(sp.integrate(M**2,(x,a,b)) for a,b,M in segs)/(2*EI)
# 檢查 D 處 M=0（E 懸臂無載）
print('M(30)=',sp.simplify(segs[-1][2].subs(x,30)))
nodes={'F':(0,0),'T1':(10,0),'T2':(20,0),'T3':(30,0),'G':(40,0),'H':(10,-10),'J':(20,-10),'K':(30,-10)}
mem=[('F','T1'),('T1','T2'),('T2','T3'),('T3','G'),('H','J'),('J','K'),('T1','H'),('T2','J'),('T3','K'),('F','H'),('H','T2'),('T2','K'),('K','G')]
def solve_truss(loads):
    # 未知：13 桿拉力 + Fx,Fy,Gy（G 水平以外力 loads 給）
    N=sp.symbols('n0:13'); Fx,Fy,Gy=sp.symbols('Fx Fy Gy')
    eqs=[]
    for nd,(px,py) in nodes.items():
        ex=0;ey=0
        for k,(a,b) in enumerate(mem):
            if nd in (a,b):
                o=b if nd==a else a
                dx=nodes[o][0]-px; dy=nodes[o][1]-py; L=sp.sqrt(dx**2+dy**2)
                ex+=N[k]*dx/L; ey+=N[k]*dy/L
        fx,fy=loads.get(nd,(0,0))
        if nd=='F': ex+=Fx; ey+=Fy
        if nd=='G': ey+=Gy
        eqs+= [ex+fx, ey+fy]
    s=sp.solve(eqs,list(N)+[Fx,Fy,Gy],dict=True)[0]
    return [sp.simplify(s[n]) for n in N]
Ls=[sp.sqrt((nodes[b][0]-nodes[a][0])**2+(nodes[b][1]-nodes[a][1])**2) for a,b in mem]
Nr=solve_truss({'T1':(0,-RB),'T3':(0,-RD),'G':(-Hg,0)})   # H 為 G 對桁架的水平反力（向左為正）
Ut=sum(n**2*L for n,L in zip(Nr,Ls))/(2*EA)
U=Ub+Ut
sol=sp.solve([sp.diff(U,X),sp.diff(U,Hg)],[X,Hg],dict=True)[0]
sol={k:sp.simplify(v) for k,v in sol.items()}
print('R_A=',sol[X]); print('H_G=',sol[Hg])
n1=solve_truss({'J':(0,-1)})
dJ=sp.simplify(sum(n.subs(sol)*m*L for n,m,L in zip(Nr,n1,Ls))/EA)
print('Δ_J（向下）=',dJ)
r=sp.symbols('r',positive=True)  # r = EA/EI (1/m²)
print('以 r=EA/EI：',sp.simplify(dJ.subs(EA,r*EI)*EI))
for rv in [1e-6,0.01,0.1,1,10,100,1e6]:
    print('  EA/EI=',rv,' Δ_J·EA=',float(sp.simplify(dJ*EA).subs(EA,rv*EI).subs(EI,1)), ' R_A=',float(sol[X].subs(EA,rv*EI).subs(EI,1)))
print('桿力（EA/EI→∞ 剛性桁架極限 與 一般式）')
for (a,b),n in zip(mem,Nr): print(' ',a+b, sp.simplify(n.subs(sol)))
