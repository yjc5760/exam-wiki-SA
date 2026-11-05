import sympy as sp
x=sp.Symbol('x'); EI=sp.Symbol('EI',positive=True)
def integ(Mexpr_pieces, EIs, x0, v0, th0):
    # pieces: list of (a,b,M(x)) ; returns list of (a,b,theta(x),v(x)) with v up, v''=M/EI (sagging +)
    out=[]; th,v=th0,v0
    for (a,b,M),E in zip(Mexpr_pieces,EIs):
        thx=th+sp.integrate(M/E,(x,a,x)); vx=v+sp.integrate(thx,(x,a,x))
        out.append((a,b,sp.simplify(thx),sp.simplify(vx))); th=thx.subs(x,b); v=vx.subs(x,b)
    return out
print('==== 2012-1')
# ac: a fixed at 0, M sagging: [0,4]:160, [4,8]: 40(8-x)
ac=integ([(0,4,sp.Integer(160)),(4,8,40*(8-x))],[2*EI,2*EI],0,0,0)
vc=ac[-1][3].subs(x,8); print('v_c =',vc, ' (up +)')
# cde: M on cd: -40(x-8) for x in [8,12]; de: -40(16-x)
th_c=sp.Symbol('thc')
cde=integ([(8,12,-40*(x-8)),(12,16,-40*(16-x))],[EI,EI],8,vc,th_c)
thc=sp.solve(cde[0][3].subs(x,12),th_c)[0]
cde=[(a,b,t.subs(th_c,thc),v.subs(th_c,thc)) for a,b,t,v in cde]
print('theta_c+ (cde side)=',thc, ' theta_c- (ac side)=',ac[-1][2].subs(x,8))
print('theta_d=',cde[0][2].subs(x,12))
print('v_e=',cde[1][3].subs(x,16),' theta_e=',cde[1][2].subs(x,16))
for a,b,t,v in ac+cde: print(a,b,'v=',sp.expand(v))
# zero of v in cd?
print('v zeros cd:',sp.solve(cde[0][3],x))
print('==== 2004-3')
E=10**6; k=10**4
# AB cantilever, tip net 12 t down: M(x) = -12(30-x), EI=2E
ab=integ([(0,30,-12*(30-x))],[2*E],0,0,0)
vB=ab[0][3].subs(x,30); thB_ab=ab[0][2].subs(x,30); print('vB=',vB,float(vB),'theta_B(AB)=',thB_ab)
vC=sp.Rational(-60,k); print('vC=',vC,float(vC))
# BCD: x from 30 to 60. M on BC: R_B part: shear from left: force on BCD at B = -24 (down) -> M = -24(x-30); CD: M=-36(60-x)
t=sp.Symbol('t')
bcd=integ([(30,48,-24*(x-30)),(48,60,-36*(60-x))],[E,E],30,vB,t)
tB=sp.solve(bcd[0][3].subs(x,48)-vC,t)[0]
bcd=[(a,b,th.subs(t,tB),v.subs(t,tB)) for a,b,th,v in bcd]
print('theta_B+ (BC side)=',tB,float(tB))
print('theta_C=',bcd[0][2].subs(x,48),float(bcd[0][2].subs(x,48)))
print('theta_D=',bcd[1][2].subs(x,60),float(bcd[1][2].subs(x,60)))
print('v_D=',bcd[1][3].subs(x,60),float(bcd[1][3].subs(x,60)))
