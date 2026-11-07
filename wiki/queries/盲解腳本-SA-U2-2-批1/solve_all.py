"""SA-U2-2 批 1 盲解：每題兩條路徑（直接勁度法 fem.py ＋ 諧合變位／柔度法）"""
import numpy as np, sympy as sp
from fem import Model
BIG = 1e10
np.set_printoptions(precision=5, suppress=True)
out = {}

# ---------- 桁架柔度法（通用）：平衡矩陣 → 移除贅餘 → 諧合 ----------
def truss_force_method(xy, mem, sup, loads, EA, red, e0=None, presc=None):
    """sup: [(node, 'x'|'y')] 反力未知數；red: ('m', k) 取桿 k 為贅餘 或 ('r', idx) 取第 idx 個反力
    e0: {k: 初始伸長}；presc: {(node,'x'|'y'): 支承位移}"""
    j = len(xy); cols = []
    for (a, b) in mem:
        L = np.hypot(*(np.subtract(xy[b], xy[a]))); c, s = np.subtract(xy[b], xy[a]) / L
        v = np.zeros(2 * j); v[2*a] += c; v[2*a+1] += s; v[2*b] -= c; v[2*b+1] -= s  # 拉力對節點的作用
        cols.append(v)
    for (n, d) in sup:
        v = np.zeros(2 * j); v[2*n + (0 if d == 'x' else 1)] = 1; cols.append(v)
    A = np.array(cols).T; P = np.zeros(2 * j)
    for (n, d), val in loads.items():
        P[2*n + (0 if d == 'x' else 1)] += val
    nm = len(mem); rk = red[1] if red[0] == 'm' else nm + red[1]
    keep = [i for i in range(A.shape[1]) if i != rk]
    s0 = np.zeros(A.shape[1]); s1 = np.zeros(A.shape[1]); s1[rk] = 1
    s0[keep] = np.linalg.solve(A[:, keep], -P)
    s1[keep] = np.linalg.solve(A[:, keep], -A[:, rk])
    Ls = [np.hypot(*np.subtract(xy[b], xy[a])) for a, b in mem]
    f11 = sum(s1[k]**2 * Ls[k] / EA for k in range(nm))
    d10 = sum(s1[k] * s0[k] * Ls[k] / EA for k in range(nm))
    d10 += sum(s1[k] * (e0 or {}).get(k, 0) for k in range(nm))
    # 支承位移：虛功 Σ R1·Δ（反力對結構作功）
    for i, (n, d) in enumerate(sup):
        d10 -= s1[nm + i] * (presc or {}).get((n, d), 0)
    if red[0] == 'r':  # 贅餘反力本身處的位移條件（該處位移 = 指定值）
        d10 += 0  # 已包含在上式（s1 的該反力分量 = 1）
    X = -d10 / f11
    return s0 + X * s1

# ===== SA-2002-3 =====
P, lam, EI, AE = sp.symbols('P lambda EI AE', positive=True)
T = sp.symbols('T')
dB = sp.simplify(sp.solve(sp.Eq((P - T) * lam**3 / (3 * EI), T * lam / AE), T)[0])
Tsol = dB; Delta = sp.simplify(Tsol * lam / AE)
out['SA-2002-3'] = dict(T=sp.simplify(Tsol), Delta=sp.factor(Delta))
m = Model(); a = m.node(0, 0); b = m.node(1, 0); c = m.node(1, 1)
m.frame(a, b, BIG, 1.0); m.truss(b, c, 2.0)  # 數值例 EI=1, AE=2, λ=1, P=1
m.solve({(a, 0), (a, 1), (a, 2), (c, 0), (c, 1)}, {(b, 1): -1})
out['SA-2002-3']['check_num(EI=1,AE=2,λ=1,P=1)'] = (m.U[m.dof[b][1]], float(-Delta.subs({P: 1, lam: 1, EI: 1, AE: 2})))

# ===== SA-2006-2 =====
m = Model(); A = m.node(0, 0); B = m.node(9, 0); C = m.node(16, 0); D = m.node(0, 12)
m.frame(A, B, BIG, 1.0, -1.0); m.frame(B, C, BIG, 1.0, -1.0); m.truss(D, B, 1.0); m.truss(D, C, 1.0)
m.solve({(A, 0), (A, 1), (D, 0), (D, 1)})
TDB, TDC = m.axial(2), m.axial(3)
# 柔度法：贅餘 X = T_DC。梁（A 鉸）與 DB 為靜定基本結構
x = sp.symbols('x'); X = sp.symbols('X')
# 基本結構：A 鉸＋DB 桿，梁受 q 與 C 處 DC 拉力 X（方向 C→D：(-16,12)/20）
def beam_sys(q, Pc_v, Pc_h):
    # 取 A 彎矩：DB 垂直分力 V_B*9 = q*16*8 - Pc_v*16 (Pc_v 向上為正)
    VB = (q * 16 * 8 - Pc_v * 16) / 9  # DB 提供向上力
    TB = VB / (12 / 15)
    return VB, TB
# 用單位載重法：
q = 1
VB0, TB0 = beam_sys(q, 0, 0); VB1, TB1 = beam_sys(0, 12 / 20, -16 / 20)
def M_expr(qq, VB, Pcv):
    RA = qq * 16 - VB - Pcv
    return sp.Piecewise((RA * x - qq * x**2 / 2, x <= 9), (RA * x - qq * x**2 / 2 + VB * (x - 9), True))
M0 = M_expr(q, VB0, 0); M1 = M_expr(0, VB1, sp.Rational(12, 20))
f11 = sp.integrate(sp.piecewise_fold(M1 * M1), (x, 0, 16)) / 1 + TB1**2 * 15 / 1 + 1**2 * 20 / 1
d10 = sp.integrate(sp.piecewise_fold(M1 * M0), (x, 0, 16)) + TB1 * TB0 * 15
Xs = float(-d10 / f11)
out['SA-2006-2'] = dict(T_DB_fem=TDB, T_DC_fem=TDC, T_DC_flex=Xs, T_DB_flex=float(TB0 + Xs * TB1),
                        RA=m.R[[m.dof[A][0], m.dof[A][1]]])

# ===== SA-2007-1 =====
xy = [(0, 0), (4.5, 0), (9, 0), (0, 6), (9, 6)]  # A B C D E
mem = [(0, 3), (3, 4), (3, 1), (1, 4), (4, 2)]   # AD DE DB BE EC
EA7 = 200e6 * 1e-3
sup = [(0, 'x'), (0, 'y'), (1, 'x'), (1, 'y'), (2, 'x'), (2, 'y')]
s = truss_force_method(xy, mem, sup, {(4, 'x'): 60}, EA7, ('m', 1))
m = Model(); nd = [m.node(*p) for p in xy]
for a_, b_ in mem: m.truss(a_, b_, EA7)
m.solve({(n, c) for n in (0, 1, 2) for c in (0, 1)}, {(4, 0): 60})
out['SA-2007-1'] = dict(names='AD DE DB BE EC', N_flex=s[:5], R_flex=s[5:], N_fem=[m.axial(i) for i in range(5)],
                        R_fem=[m.R[m.dof[n][c]] for n in (0, 1, 2) for c in (0, 1)])

# ===== SA-2008-1 =====
xy = [(0, 0), (10, 5), (10, 0), (20, 10), (20, 0)]  # A B C D E
mem = [(0, 1), (1, 3), (0, 2), (2, 4), (2, 1), (1, 4), (3, 4)]  # AB BD AC CE CB BE DE
sup = [(0, 'y'), (3, 'x'), (4, 'x'), (4, 'y')]
s = truss_force_method(xy, mem, sup, {(1, 'y'): -10}, 1.0, ('r', 2))
m = Model(); [m.node(*p) for p in xy]
for a_, b_ in mem: m.truss(a_, b_, 1.0)
m.solve({(0, 1), (3, 0), (4, 0), (4, 1)}, {(1, 1): -10})
out['SA-2008-1'] = dict(names='AB BD AC CE CB BE DE', N_flex=s[:7], R_flex='Ay Dx Ex Ey ' + str(s[7:]),
                        N_fem=[m.axial(i) for i in range(7)],
                        R_fem=[m.R[m.dof[n][c]] for n, c in ((0, 1), (3, 0), (4, 0), (4, 1))])

# ===== SA-2009-1 =====
xy = [(0, 0), (4, 3), (8, 3), (8, 0), (4, 0)]  # a b c d e
mem = [(0, 1), (1, 2), (1, 4), (4, 2), (2, 3), (0, 4), (4, 3)]  # ab bc be ec cd ae ed
sup = [(0, 'y'), (2, 'x'), (2, 'y'), (3, 'x')]
s = truss_force_method(xy, mem, sup, {}, 1e4, ('r', 0), presc={(0, 'y'): -0.1})
m = Model(); [m.node(*p) for p in xy]
for a_, b_ in mem: m.truss(a_, b_, 1e4)
m.solve({(2, 0), (2, 1), (3, 0)}, presc={(0, 1): -0.1})
out['SA-2009-1'] = dict(names='ab bc be ec cd ae ed', N_flex=s[:7], R_flex='ay cx cy dx ' + str(s[7:]),
                        N_fem=[m.axial(i) for i in range(7)],
                        R_fem=[m.R[m.dof[n][c]] for n, c in ((0, 1), (2, 0), (2, 1), (3, 0))])

# ===== SA-2009-2 =====
EI9, k9 = 1000.0, 1000.0 / 100
y = sp.symbols('y')
# 懸臂（c 在 y=0）受 w=1 向左；a 端連桿拉力 R 向右
Rl = sp.symbols('R')
d_free = 1 * 10**4 / (8 * EI9); f_tip = 10**3 / (3 * EI9)
Rv = sp.solve(sp.Eq(d_free - Rl * f_tip, Rl / k9), Rl)[0]
def cant_uniform(yy, w=1, L=10): return w * yy**2 * (6 * L**2 - 4 * L * yy + yy**2) / (24 * EI9)
def cant_point(yy, Pp, L=10): return Pp * yy**2 * (3 * L - yy) / (6 * EI9)
db = cant_uniform(6) - cant_point(6, Rv)
m = Model(); nc = m.node(0, 0); nb = m.node(0, 6); na = m.node(0, 10); nd_ = m.node(100, 10)
m.frame(nc, nb, BIG, EI9, 1.0); m.frame(nb, na, BIG, EI9, 1.0)  # 局部 y = 全域 -x → q=+1 即向左
m.truss(na, nd_, 1000.0)
m.solve({(nc, 0), (nc, 1), (nc, 2), (nd_, 0), (nd_, 1)})
out['SA-2009-2'] = dict(R_link=float(Rv), db_left_flex=float(db), db_fem=m.U[m.dof[nb][0]], da_fem=m.U[m.dof[na][0]],
                        link_fem=m.axial(2), Mc=None)

# ===== SA-2011-1 =====
xy = [(0, 3), (4, 3), (8, 3), (0, 0), (4, 0), (8, 0)]  # A B C D E F
mem = [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5), (0, 4), (2, 4)]  # AB BC DE EF AD BE CF AE CE
al = 1.08e-5; e0 = {0: al * 60 * 4, 5: al * 60 * 3, 2: -0.015, 3: -0.010}
sup = [(0, 'x'), (3, 'x'), (3, 'y'), (5, 'y')]
s = truss_force_method(xy, mem, sup, {}, 8e4, ('r', 0), e0=e0, presc={(0, 'x'): -0.024, (5, 'y'): -0.012})
m = Model(); [m.node(*p) for p in xy]
for k_, (a_, b_) in enumerate(mem): m.truss(a_, b_, 8e4, e0.get(k_, 0))
m.solve({(3, 0), (3, 1)}, presc={(0, 0): -0.024, (5, 1): -0.012})
out['SA-2011-1'] = dict(names='AB BC DE EF AD BE CF AE CE', N_flex=s[:9], R_flex='Ax Dx Dy Fy ' + str(s[9:]),
                        N_fem=[m.axial(i) for i in range(9)],
                        R_fem=[m.R[m.dof[n][c]] for n, c in ((0, 0), (3, 0), (3, 1), (5, 1))])
# 另算：支承位移符號反過來（假設題意相反）之敏感度
s_alt = truss_force_method(xy, mem, sup, {}, 8e4, ('r', 0), e0=e0, presc={(0, 'x'): +0.024, (5, 'y'): -0.012})
out['SA-2011-1']['R_if_A_right'] = s_alt[9:]

# ===== SA-2014-2 =====
EIb, EAc, w = 10000.0, 40000.0, 8.0
m = Model(); nA = m.node(0, 0); nD = m.node(6, 0); nB = m.node(12, 0); nC = m.node(0, 4.5)
m.frame(nA, nD, BIG, EIb, -w); m.frame(nD, nB, BIG, EIb, -w); m.truss(nC, nD, EAc)
m.solve({(nA, 0), (nA, 1), (nA, 2), (nB, 1), (nC, 0), (nC, 1)})
xs = np.linspace(0, 6, 6001)
M1 = [m.moment_at(0, t) for t in xs]; M2 = [m.moment_at(1, t) for t in xs]
allM = [(abs(v), v, t) for v, t in zip(M1, xs)] + [(abs(v), v, 6 + t) for v, t in zip(M2, xs)]
mx = max(allM)
# 柔度法（贅餘 R_B、T_CD；梁軸向剛性）
RB, Tc = sp.symbols('R_B T')
sv = 4.5 / 7.5  # 桿拉力垂直分量比
# D 向下撓度、B 向下撓度（懸臂 A 固定）
def cant_def(a_pt, xq):  # 單位向上點力於 a_pt，xq 處向上撓度
    return (xq**2 * (3 * a_pt - xq) if xq <= a_pt else a_pt**2 * (3 * xq - a_pt)) / (6 * EIb)
def cant_q(xq, L=12): return -w * xq**2 * (6 * L**2 - 4 * L * xq + xq**2) / (24 * EIb)
vB = cant_q(12) + RB * cant_def(12, 12) + Tc * sv * cant_def(6, 12)
vD = cant_q(6) + RB * cant_def(12, 6) + Tc * sv * cant_def(6, 6)
sol = sp.solve([sp.Eq(vB, 0), sp.Eq(-vD * sv, Tc * 7.5 / EAc)], [RB, Tc])
MA = float(-w * 12 * 6 + sol[RB] * 12 + sol[Tc] * sv * 6)
out['SA-2014-2'] = dict(Mmax=mx[1], x_at=mx[2], T_fem=m.axial(2), RB_fem=m.R[m.dof[nB][1]],
                        RB_flex=float(sol[RB]), T_flex=float(sol[Tc]), MA_flex=MA,
                        M_D=m.moment_at(0, 6), Mpos_max=max(v for _, v, _ in allM))

# ===== SA-2016-1 =====
m = Model(); nA = m.node(0, 0); nB = m.node(0, 2); nC1 = m.node(2, 2); nC2 = m.node(2, 2, share=nC1)
nD = m.node(4, 2); nE = m.node(4, 0)
m.frame(nA, nB, BIG, 1.0); m.frame(nB, nC1, BIG, 1.0); m.frame(nC2, nD, BIG, 1.0); m.frame(nE, nD, BIG, 1.0)
m.solve({(nA, 0), (nA, 1), (nE, 0), (nE, 1), (nE, 2)}, {(nD, 0): 50})
ef = [m.endforces(i) for i in range(4)]
# 柔度法：贅餘 Ax = X（基本結構：A 滾、C 內鉸、E 固定 → 靜定）
# 左半 A-B-C：取 C 彎矩=0 對左半：Ay*2 - X*2... 用 sympy 單位載重
Xs16 = sp.symbols('X')
# 左半自由體 A–B–C：A 反力 (X 向右, Ay 向上)。M_C(左)=0：Ay*2 + X*2 ... 取 C 點矩：Ay*(0-2)?
# 以座標：A(0,0) C(2,2)。對 C 取矩 Ay*(xA-xC) - X*(yA-yC) = Ay*(-2) - X*(-2) =0 → Ay = X
# 柱 AB 彎矩 M = X*s（距 A s，外側受拉號略），梁 BC M = 2X - Ay*u = X(2-u)
# 右半 C-D-E：C 處傳力 (−X 水平, −Ay)；D 加 50 → 柱 DE 底 E
u = sp.symbols('u')
M_AB = Xs16 * u; M_BC = Xs16 * (2 - u)
# CD 段（距 C u）：左半對右半的力 = 左半所受外力合 (X, Ay) 傳過 C：M = Ay*... 取左側自由體（含整個左半）
M_CD = Xs16 * 2 - Xs16 * (2 + u) + Xs16 * 2  # 左側：X 對 y=2 的矩 X*2，Ay 對 x=2+u: -Ay*(2+u) ... 修正見下
# 直接用整體左側自由體：在 CD 上 x=2+u 截面，左側外力 X@(0,0) 向右、Ay@(0,0) 向上
M_CD = sp.expand(Xs16 * (2 - 0) * 1 - Xs16 * (2 + u))  # 逆時針為正之一致記號：M = X*2 - Ay*(2+u)
# DE 柱（距 D 向下 t）：左側自由體 + 50 於 D(4,2)。截面 (4, 2-t)
t = sp.symbols('t')
M_DE = sp.expand(Xs16 * (2 - t) - Xs16 * 4 + 50 * (-t) * (-1))  # X 對截面矩 + Ay 對截面矩 + 50 對截面矩
# 一致記號：M_sec = Σ (r × F)_z，r 從截面指向力作用點
def Mz(px, py, fx, fy, sx, sy): return (px - sx) * fy - (py - sy) * fx
def Msec(sx, sy, inc50):
    v = Mz(0, 0, Xs16, Xs16, sx, sy)
    if inc50: v += Mz(4, 2, 50, 0, sx, sy)
    return sp.expand(v)
segs = [(lambda s_: (0, s_), 2, False), (lambda s_: (s_, 2), 2, False), (lambda s_: (2 + s_, 2), 2, False), (lambda s_: (4, 2 - s_), 2, True)]
sv_ = sp.symbols('s')
U_ = 0
for fn, Ls_, inc in segs:
    sx, sy = fn(sv_); Mexp = Msec(sx, sy, inc); U_ += sp.integrate(Mexp**2, (sv_, 0, Ls_)) / 2
Xsol = sp.solve(sp.diff(U_, Xs16), Xs16)[0]
Mvals = {}
for nm_, (fn, Ls_, inc) in zip(['A', 'B', 'C', 'D'], segs):
    pass
pts = {'B': (0, 2, False), 'C': (2, 2, False), 'D_left': (4, 2, False), 'D_col': (4, 2, False), 'E': (4, 0, True)}
Mcheck = {k: float(Msec(px, py, inc).subs(Xs16, Xsol)) for k, (px, py, inc) in pts.items()}
out['SA-2016-1'] = dict(endforces_AB=ef[0], BC=ef[1], CD=ef[2], ED=ef[3],
                        R_A=(m.R[m.dof[nA][0]], m.R[m.dof[nA][1]]),
                        R_E=(m.R[m.dof[nE][0]], m.R[m.dof[nE][1]], m.R[m.dof[nE][2]]),
                        X_flex=float(Xsol), M_flex=Mcheck, Ay=float(Xsol))

# ===== SA-2023-2 =====
xy = [(0, 0), (8, 0), (5, -4), (3, -4)]  # A B C D
mem = [(0, 1), (0, 3), (0, 2), (1, 3), (1, 2), (3, 2)]  # AB AD AC BD BC DC
sup = [(0, 'x'), (0, 'y'), (3, 'y')]
s = truss_force_method(xy, mem, sup, {(1, 'y'): -30}, 2e5, ('m', 3))
m = Model(); [m.node(*p) for p in xy]
for a_, b_ in mem: m.truss(a_, b_, 2e5)
m.solve({(0, 0), (0, 1), (3, 1)}, {(1, 1): -30})
out['SA-2023-2'] = dict(names='AB AD AC BD BC DC', N_flex=s[:6], R_flex='Ax Ay Dy ' + str(s[6:]),
                        N_fem=[m.axial(i) for i in range(6)])

for k, v in out.items():
    print('=====', k)
    for kk, vv in v.items():
        print('  ', kk, ':', vv)
