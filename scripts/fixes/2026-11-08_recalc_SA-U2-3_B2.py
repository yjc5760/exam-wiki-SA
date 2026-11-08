#!/usr/bin/env python3
"""SA-U2-3 批 2 勘誤重算（2026-11-08）：SA-2017-3、SA-2021-1、SA-2021-2、SA-2025-3
每題兩條獨立路徑：① 剛架勁度法（wiki/queries/盲解腳本-SA-U2-3-批2/frame.py）② 手列傾角變位式／柔度法（sympy）
與勘誤後解析正本的數值逐項比對，最後印 MISMATCHES: n。
用法：python3 scripts/fixes/2026-11-08_recalc_SA-U2-3_B2.py（在 repo 根目錄）"""
import os, sys
import numpy as np, sympy as sp
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "wiki", "queries", "盲解腳本-SA-U2-3-批2"))
from frame import Frame

BAD = []
def chk(tag, stated, *paths, tol=1e-4):   # 勁度法以 EA=1e8·EI 近似不計軸向變形，相對誤差約 1e-5
    for k, v in enumerate(paths, 1):
        ok = abs(float(v) - float(stated)) <= tol * max(1, abs(float(stated)))
        print(f"  {'OK ' if ok else 'BAD'} {tag:28s} 正本 {float(stated):>12.6g}  路徑{k} {float(v):>12.6g}")
        if not ok: BAD.append((tag, stated, k, v))
sd = lambda ti, tj, L, psi=0, F=0: sp.Rational(2) / sp.nsimplify(L) * (2*ti + tj - 3*psi) + F

# ── SA-2017-3（順時針為正；θ 負值 = 逆時針）────────────────────
print("SA-2017-3")
f = Frame()
for n, x, y in [('A',0,0),('B',0,4),('C',6,4),('D',6,0)]: f.node(n, x, y)
f.support('A',1,1,0); f.support('D',1,1,0)
f.member('AB','A','B'); f.member('BC','B','C'); f.member('DC','D','C')
f.mload('BC','udl',wy=-45); f.mload('DC','pt',px=-60,a=2); f.load('C',fx=-60); f.solve()
tA,tB,tC,tD,D = sp.symbols('tA tB tC tD D'); p = D/4
MAB,MBA = sd(tA,tB,4,p),sd(tB,tA,4,p); MDC,MCD = sd(tD,tC,4,p,30),sd(tC,tD,4,p,-30)
MBC,MCB = sd(tB,tC,6,0,-135),sd(tC,tB,6,0,135)
s = sp.solve([MAB,MDC,MBA+MBC,MCB+MCD,(MAB+MBA)/4+(MDC+MCD+120)/4-120],[tA,tB,tC,tD,D])
cw = lambda n: -f.U[n][2]            # 勁度法逆時針為正 → 轉成順時針為正
chk("EIθ_A（負=逆時針）", sp.Rational(-8280,13), cw('A'), s[tA])
chk("EIθ_D（負=逆時針）", sp.Rational(-7320,13), cw('D'), s[tD])
chk("EIθ_B", sp.Rational(-990,13), cw('B'), s[tB]); chk("EIθ_C", sp.Rational(-3690,13), cw('C'), s[tC])
chk("M_BA", sp.Rational(3645,13), f.end['AB']['Mj_cw'], MBA.subs(s)); chk("M_CD", sp.Rational(1035,13), f.end['DC']['Mj_cw'], MCD.subs(s))

# ── SA-2021-1 ───────────────────────────────────────────────
print("SA-2021-1")
EI = 10000
f = Frame()
for n, x in [('a',0),('b',4),('c',8),('d',10)]: f.node(n, x, 0)
f.node('s',4,-1); f.support('s'); f.support('a',0,1,0); f.support('d')
f.member('ab','a','b',EI=EI,EA=1e12); f.member('bc','b','c',EI=EI,EA=1e12,hinge_j=True)
f.member('cd','c','d',EI=EI,EA=1e12,hinge_i=True); f.member('spr','b','s',EI=1e-9,EA=15000,hinge_i=True,hinge_j=True)
f.mload('ab','pt',py=-36,a=2); f.load('b',fy=-36); f.solve()
t,b,c = sp.symbols('t b c')
Mba = 7500*t - 1875*b + 27; Mbc = 7500*t - 1875*c + 1875*b
s = sp.solve([Mba+Mbc, 18 + Mba/4 - Mbc/4 + 36 - 15000*b, Mbc/4 - 3750*c],[t,b,c])
Ra = 18 - Mba.subs(s)/4
chk("Δ_b (m, 下)", 0.0038, -f.U['b'][1], s[b]); chk("θ_b (rad, 負=逆時針)", -0.00185, -f.U['b'][2], s[t])
chk("Δ_c (m, 下)", -0.0004, -f.U['c'][1], s[c])
chk("M_ba", 6, f.end['ab']['Mj_cw'], Mba.subs(s)); chk("M_bc", -6, f.end['bc']['Mi_cw'], Mbc.subs(s))
chk("R_a", 16.5, f.R['a'][1], Ra); chk("ab 跨中彎矩", 33, 2*f.R['a'][1], 2*Ra)
chk("彈簧力", 57, f.end['spr']['Nj']*-1 if f.end['spr']['Nj'] < 0 else f.end['spr']['Nj'], 15000*s[b])
chk("M_d（逆時針作用於梁）", 3, f.R["d"][2], -2*Mbc.subs(s)/4)

# ── SA-2021-2（框角剛接，使用者 2026-11-08 判定）─────────────────
print("SA-2021-2")
EI = 20000
f = Frame()
for n, x, y in [('a',0,3),('b',3,3),('e',9,3),('f',12,3),('c',3,0),('d',9,0)]: f.node(n, x, y)
f.support('a',0,1,0); f.support('f',0,1,0); f.support('d',0,1,0); f.support('c',1,1,0)
for m in ['ab','be','ef','cb','de','cd']: f.member(m, m[0], m[1], EI=EI, EA=1e12)
f.load('f', fx=24); f.solve()
th, ph, ps = sp.symbols('th ph ps')
Mba = th; Mbe = sp.Rational(2,6)*3*th; Mbc = sp.Rational(2,3)*(2*th+ph-3*ps); Mcb = sp.Rational(2,3)*(2*ph+th-3*ps); Mcd = sp.Rational(2,6)*3*ph
s = sp.solve([Mba+Mbe+Mbc, Mcb+Mcd, (Mbc+Mcb)/3+12],[th,ph,ps])
chk("θ_b (rad, 順時針)", 5.0e-4, -f.U['b'][2], s[th]/EI); chk("Δ_b (m, 右)", 0.0033, f.U['b'][0], 3*s[ps]/EI)
chk("θ_c (rad)", 8.0e-4, -f.U['c'][2], s[ph]/EI)
chk("M_ba", 10, f.end['ab']['Mj_cw'], Mba.subs(s)); chk("M_be", 10, f.end['be']['Mi_cw'], Mbe.subs(s))
chk("M_bc", -20, f.end['cb']['Mj_cw'], Mbc.subs(s)); chk("M_cb", -16, f.end['cb']['Mi_cw'], Mcb.subs(s))
chk("M_cd", 16, f.end['cd']['Mi_cw'], Mcd.subs(s))
# 受拉側：ab 在 b 端內彎矩（下緣受拉為正）= −M_ba(cw, 右端)；be 在 b 端 = +M_be(cw, 左端)
chk("梁 b 左內彎矩", -10, -f.end['ab']['Mj_cw'], -Mba.subs(s)); chk("梁 b 右內彎矩", 10, f.end['be']['Mi_cw'], Mbe.subs(s))

# ── SA-2025-3（順時針為正；k 以 EI/L、M_F 以 PL 為單位）──────────
print("SA-2025-3")
x, L, E, P = sp.symbols('x L E P', positive=True)
seg = [(0,L/3,E),(L/3,2*L/3,2*E),(2*L/3,L,E)]; I = lambda g: sum(sp.integrate(g/e,(x,a0,b0)) for a0,b0,e in seg)
m1, m2 = 1 - x/L, -x/L
F = sp.Matrix([[I(m1*m1), I(m1*m2)], [I(m2*m1), I(m2*m2)]]); K = sp.simplify(F.inv())
M0 = sp.Piecewise((P*x/2, x <= L/2), (P*(L-x)/2, True)); th0 = sp.Matrix([I(M0*m1), I(M0*m2)]); FEM = sp.simplify(-K*th0)
def ke(EIv, l): return EIv/l**3*np.array([[12,6*l,-12,6*l],[6*l,4*l*l,-6*l,2*l*l],[-12,-6*l,12,-6*l],[6*l,2*l*l,-6*l,4*l*l]])
Kg = np.zeros((8,8)); l = 1/3
for e_, EIv in enumerate([1,2,1]): dd = list(range(2*e_, 2*e_+4)); Kg[np.ix_(dd,dd)] += ke(EIv, l)
fr = [2,3,4,5]; Fv = np.zeros(8); Fv[2:6] += [-0.5,-l/8,-0.5,l/8]
u = np.zeros(8); u[fr] = np.linalg.solve(Kg[np.ix_(fr,fr)], Fv[fr]); fem_fe = -(Kg@u - Fv)[1]
u = np.zeros(8); u[1] = 1; u[fr] = np.linalg.solve(Kg[np.ix_(fr,fr)], -Kg[np.ix_(fr,[1])].ravel()); R = Kg@u
k = lambda e: (e*L/E).subs({L:1,E:1})
chk("k_AA", sp.Rational(1128,265), k(K[0,0]), R[1]); chk("k_AB", sp.Rational(492,265), k(K[0,1]), R[7])
chk("k_Aψ = −(k_AA+k_AB)", -sp.Rational(324,53), -k(K[0,0]+K[0,1]), -(R[1]+R[7]))
chk("M_F,AB / PL", -sp.Rational(13,120), (FEM[0]/(P*L)), fem_fe); chk("M_F,BA / PL", sp.Rational(13,120), (FEM[1]/(P*L)), -fem_fe)
thA = I(M0*m1).subs({P:1,L:1,E:1}); thB = I(M0*m2).subs({P:1,L:1,E:1})
chk("Δ_A^(P) / (PL²/EI)", sp.Rational(13,288), thA); chk("Δ_B^(P)（與 A 反號）", -sp.Rational(13,288), thB)
mu = [(0,sp.Rational(1,2),1)] ; Iu = lambda g: sp.integrate(g,(x,0,L)).subs({L:1})
chk("均勻梁 M_F,AB / PL", -sp.Rational(1,8), sp.simplify(-((sp.Matrix([[sp.Rational(1,3),-sp.Rational(1,6)],[-sp.Rational(1,6),sp.Rational(1,3)]]).inv())*sp.Matrix([sp.integrate((M0*m1).subs({P:1,L:1}),(x,0,1)), sp.integrate((M0*m2).subs({P:1,L:1}),(x,0,1))]))[0]))

print(f"\nMISMATCHES: {len(BAD)}")
for b_ in BAD: print("  ", b_)
