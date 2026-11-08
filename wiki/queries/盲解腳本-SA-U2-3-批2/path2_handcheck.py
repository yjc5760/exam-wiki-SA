"""SA-U2-3 批 2 盲解路徑 2：手列傾角變位式／力法／柔度法（sympy），與路徑 1 對照。python path2_handcheck.py"""
import sympy as sp, numpy as np
sd = lambda ti, tj, L, psi=0, F=0, k=1: 2*k/sp.nsimplify(L)*(2*ti+tj-3*psi)+F
print('== 2015-3'); tB,dC=sp.symbols('tB dC'); w=4
MBA=sd(tB,0,4); MBC=3*(tB-dC)-sp.Rational(w,8); MDC=(0+dC/3)+sp.Rational(w*9,8)
s=sp.solve([MBA+MBC, w/sp.Integer(2)+MBC+ (6-MDC/3)],[tB,dC]); print(s,[e.subs(s) for e in (sd(0,tB,4),MBA,MBC,MDC)],'Gy',2*(6+MDC/3).subs(s))
print('== 2017-3'); tA,tB,tC,tD,D=sp.symbols('tA tB tC tD D'); p=D/4
MAB,MBA=sd(tA,tB,4,p),sd(tB,tA,4,p); MDC,MCD=sd(tD,tC,4,p,30),sd(tC,tD,4,p,-30); MBC,MCB=sd(tB,tC,6,0,-135),sd(tC,tB,6,0,135)
s=sp.solve([MAB,MDC,MBA+MBC,MCB+MCD,(MAB+MBA)/4+(MDC+MCD+120)/4-120],[tA,tB,tC,tD,D]); print(s,[e.subs(s) for e in (MBA,MCB)])
print('== 2019-3'); w,L,EI,Dl,tA,tB=sp.symbols('w L EI Delta tA tB'); k=2*EI/L; psi=Dl/L
MAB=k*(2*tA+tB-3*psi)-w*L**2/12; MBA=k*(2*tB+tA-3*psi)+w*L**2/12; MBC=k*(2*tB-tB)-w*L**2/12
s=sp.solve([MAB,MBA+MBC],[tA,tB],dict=True)[0]; RA=sp.simplify(w*L/2-(MAB+MBA).subs(s)/L); print('RA=',RA, 'Delta=',sp.solve(RA-sp.Rational(1,2)*w*L,Dl))
print('== 2020-1'); tb,tc,D=sp.symbols('tb tc D')
Mab,Mba=sd(0,tb,4,D/4),sd(tb,0,4,D/4); Pp=sp.Rational(272,5); Mbc,Mcb=sd(tb,tc,5,0,-Pp*5/8),sd(tc,tb,5,0,Pp*5/8)
s=sp.solve([Mcb,Mba+Mbc,(Mab+Mba)/4+68],[tb,tc,D]); H=sp.Symbol('H'); print(s,[Mab.subs(s),Mba.subs(s)],'Hc',sp.solve(3*H-136-Mbc.subs(s),H))
print('== 2020-2'); tb,tf,D=sp.symbols('tb tf D'); E=20000
Mab,Mba=sd(0,tb,4,D/4),sd(tb,0,4,D/4); Mbc=sd(tb,-tb,4,0,-6); Mbf,Mfb=sd(tb,tf,4),sd(tf,tb,4); Mef,Mfe=sd(0,tf,4,D/4),sd(tf,0,4,D/4); Mfg=sd(tf,-tf,4,0,-6)
s=sp.solve([Mba+Mbc+Mbf,Mfe+Mfg+Mfb,(Mab+Mba)/2+(Mef+Mfe)/2+24],[tb,tf,D]); print({k:v/E for k,v in s.items()},[Mab.subs(s),Mba.subs(s)])
print('== 2021-1'); ta,tb,Db,Dc=sp.symbols('ta tb Db Dc'); E=10000
Mab=E*sd(ta,tb,4,Db/4)-18; Mba=E*sd(tb,ta,4,Db/4)+18; Mbc=E*sp.Rational(3,4)*(tb-(Dc-Db)/4); Mdc=E*sp.Rational(3,2)*(Dc/2)
s=sp.solve([Mab,Mba+Mbc,-(18+(Mab+Mba)/4)+Mbc/4+15000*Db-36,Mbc/4-Mdc/2],[ta,tb,Db,Dc]); print(s,[Mba.subs(s),Mdc.subs(s)])
print('== 2021-2'); ta,tb,te,tf,tc,td,D=sp.symbols('ta tb te tf tc td D'); E=20000; p=D/3; S=lambda *a: E*sd(*a)
Mab,Mba=S(ta,tb,3),S(tb,ta,3); Mbe,Meb=S(tb,te,6),S(te,tb,6); Mef,Mfe=S(te,tf,3),S(tf,te,3)
Mcb,Mbc=S(tc,tb,3,p),S(tb,tc,3,p); Mde,Med=S(td,te,3,p),S(te,td,3,p); Mcd,Mdc=S(tc,td,6),S(td,tc,6)
s=sp.solve([Mab,Mba+Mbe+Mbc,Meb+Mef+Med,Mfe,Mcb+Mcd,Mdc+Mde,24+(Mcb+Mbc)/3+(Mde+Med)/3],[ta,tb,te,tf,tc,td,D]); print(s,[Mba.subs(s),Mbe.subs(s),Mbc.subs(s)])
print('== 2022-2 力法'); X,y,x=sp.symbols('X y x'); He=X/2-30; Ha=-30-X/2; Va=-X
segs=[(y*Ha,y,0,2),(y*Ha+(y-2)*30,y,2,4),(4*Ha-x*Va+60,x,0,4),((8-y)*He+(6-y)*30,y,4,6),((8-y)*He,y,6,8)]
Xs=sp.solve(sp.diff(sum(sp.integrate(M**2,(v,a,b)) for M,v,a,b in segs),X),X)[0]
def um(py):
    he=-sp.Rational(py,8); ha=-1-he; return [y*ha, y*ha+((y-2) if py==2 else 0), 4*ha+(4-py), (8-y)*he, (8-y)*he]
for py,n in [(2,'b'),(4,'c')]: print(n, sum(sp.integrate(M.subs(X,Xs)*u,(v,a,b)) for (M,v,a,b),u in zip(segs,um(py)))/40000)
print('Ve',Xs,'Mcd',sp.simplify(segs[2][0].subs(X,Xs)))
print('== 2023-3'); tA,tB,tC=sp.symbols('tA tB tC')
MAB,MBA=sd(tA,tB,6,0,60),sd(tB,tA,6,0,-60); MBC,MCB=sd(tB,tC,4,0,25),sd(tC,tB,4,0,-25); MCD,MDC=sd(tC,0,4),sd(0,tC,4)
s=sp.solve([MAB,MBA+MBC,MCB+MCD],[tA,tB,tC]); print(s,[e.subs(s) for e in (MBA,MCB,MDC)])
print('== 2024-3'); r,t,D,P,L=sp.symbols('r t D P L'); psi=D/L
MAB=2/L*(t-3*psi); MBA=2/L*(2*t-3*psi); MBC=3/(r*L)*t; MDC=-3*D/L**2
s=sp.solve([MBA+MBC,(MAB+MBA)/L+MDC/L+P],[t,D]); E={k:sp.simplify(v.subs(s)/(P*L)) for k,v in dict(MAB=MAB,MBA=MBA,MBC=MBC,MDC=MDC).items()}
print(E,'r=',sp.solve(sp.Eq(-E['MAB'],2*E['MBC']),r))
print('== 2025-3 柔度法'); x,L,EI,P=sp.symbols('x L EI P',positive=True)
seg=[(0,L/3,EI),(L/3,2*L/3,2*EI),(2*L/3,L,EI)]; I=lambda f: sum(sp.integrate(f/e,(x,a,b)) for a,b,e in seg)
m1,m2=(1-x/L),-(x/L); F=sp.Matrix([[I(m1*m1),I(m1*m2)],[I(m2*m1),I(m2*m2)]]); K=sp.simplify(F.inv())
M0=sp.Piecewise((P*x/2,x<=L/2),(P*(L-x)/2,True)); th0=sp.Matrix([I(M0*m1),I(M0*m2)]); print('K=',K,'FEM=',sp.simplify(-K*th0))
print('== 2025-3 有限元凝聚')
def ke(EI,l): return EI/l**3*np.array([[12,6*l,-12,6*l],[6*l,4*l*l,-6*l,2*l*l],[-12,-6*l,12,-6*l],[6*l,2*l*l,-6*l,4*l*l]])
Kg=np.zeros((8,8)); l=1/3
for e,EIv in enumerate([1,2,1]): d=list(range(2*e,2*e+4)); Kg[np.ix_(d,d)]+=ke(EIv,l)
Fv=np.zeros(8); Fv[2:6]+=[-0.5,-l/8,-0.5,l/8]; fr=[2,3,4,5]; u=np.zeros(8); u[fr]=np.linalg.solve(Kg[np.ix_(fr,fr)],Fv[fr]); print('FEM_cw',-(Kg@u-Fv)[1])
u=np.zeros(8); u[1]=1; u[fr]=np.linalg.solve(Kg[np.ix_(fr,fr)],-Kg[np.ix_(fr,[1])].ravel()); R=Kg@u; print('kAA',R[1],'kAB',R[7])
