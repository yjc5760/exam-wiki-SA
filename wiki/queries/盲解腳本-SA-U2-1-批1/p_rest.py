import sympy as sp, numpy as np
print('== SA-2008-3 最小功閉式')
R,x,u=sp.symbols('R x u')
MAB=R*x-x**2; MBC=R*(6+u)-12*(3+u)
U=sp.integrate(MAB**2,(x,0,6))+sp.Rational(75,45)*sp.integrate(MBC**2,(u,0,sp.Rational(9,2)))
Rs=sp.solve(sp.diff(U,R),R)[0]; print('R_A=',Rs,float(Rs))
MB=MAB.subs({R:Rs,x:6}); MC=MBC.subs({R:Rs,u:sp.Rational(9,2)}); print('M_B=',MB,float(MB),' M_C=',MC,float(MC))
xm=Rs/2; print('AB 最大正彎矩 x=',float(xm),'M=',float(MAB.subs({R:Rs,x:xm})))
u0=sp.solve(MBC.subs(R,Rs),u)[0]; print('BC 反曲點 u(水平,自B)=',float(u0),' 沿桿=',float(u0*sp.Rational(75,45)))

print('== SA-2013-2 閉式（卡氏）')
H,V,s=sp.symbols('H V s')   # C 反力：H 向左為正, V 向上
# BC: s 自 C 量起 0..10； M=V*s - 20*<s-5>  ；AB: y 自 B 向下 0..10：M = V*10 - 20*5 + H*y（H 向左作用於 C(高 10)，對 A 柱斷面力臂 y）
Mbc1=V*s; Mbc2=V*s-20*(s-5); y=sp.symbols('y')
Mab=V*10-100+H*y
Uc=sp.integrate(Mbc1**2,(s,0,5))+sp.integrate(Mbc2**2,(s,5,10))+sp.integrate(Mab**2,(y,0,10))
sol=sp.solve([sp.diff(Uc,H),sp.diff(Uc,V)],[H,V]); print(sol,{k:float(v) for k,v in sol.items()})
# θ_C：加虛擬力矩 Mc（逆時針）於 C
Mc=sp.symbols('Mc')
Uc2=sp.integrate((Mbc1+Mc)**2,(s,0,5))+sp.integrate((Mbc2+Mc)**2,(s,5,10))+sp.integrate((Mab+Mc)**2,(y,0,10))
th=sp.diff(Uc2,Mc).subs(Mc,0).subs(sol)/2; print('θ_C·EI =',sp.nsimplify(th),float(th),'（正＝與 Mc 同向；Mc 取使 BC 在 C 端 M=+Mc 的方向）')

print('== SA-2017-2')
w,m,n,EI=sp.symbols('w m n EI',positive=True)
Vh=3*w*(m**4-n**4)/(8*(m**3+n**3))
Ma=sp.factor(sp.simplify(-w*m**2/2+Vh*m)); Mb=sp.factor(sp.simplify(-w*n**2/2-Vh*n))
print('V_c(右段施於左段, 向上)=',sp.factor(Vh))
print('M_a=',Ma); print('M_b=',Mb)
# 用最小功驗算
X=sp.symbols('X'); xx=sp.symbols('xx')
Uw=sp.integrate((-w*xx**2/2+X*xx)**2,(xx,0,m))+sp.integrate((-w*xx**2/2-X*xx)**2,(xx,0,n))
print('最小功 X =',sp.factor(sp.solve(sp.diff(Uw,X),X)[0]))
print(' m=n:',sp.simplify(Ma.subs(n,m)), '  數例 m=0.43L:', [sp.N(e.subs({m:0.43,n:0.57,w:1})) for e in (Ma,Mb)])
