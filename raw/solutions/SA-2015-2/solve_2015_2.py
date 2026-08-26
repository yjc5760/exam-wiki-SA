"""SA-2015-2：以「釋放 F 點剪力」的基本結構做完整推導（考題指定的共軛梁路徑），
並與「釋放 R_A」的獨立路徑逐點對照。EI = 1。"""
import sympy as sp

x = sp.symbols('x')
XA, XF, XB, XC, XD, XE = 0, 15, 30, 40, 50, 80

# ── 釋放 F 點剪力後的靜定結構，施加單位剪力對（F 左向下 1、右向上 1）───────
# 反力：A_y = +1, B_y = -4, D_y = +4, E_y = -1（.md §4 Step 1 已推得）
# 彎矩（下凹為正）
M = [(0, 15, x), (15, 30, x), (30, 40, 120 - 3 * x), (40, 50, 120 - 3 * x), (50, 80, x - 80)]
assert (120 - 3 * x).subs(x, XC) == 0                      # 內鉸 C 處彎矩必須為零


def piece(a, b, expr, c1, c2):
    return sp.integrate(expr, x, x) + c1 * x + c2


# 三個「y 可以獨立積分」的區段：[0,15]、[15,40]（F 處 y 跳、θ 連續）、[40,80]（C 處 θ 跳、y 連續）
c = sp.symbols('c1:7')
Y1 = sp.integrate(x, x, x) + c[0] * x + c[1]                       # [0,15]
# [15,30] 與 [30,40] 內部須 C1 連續
Y2a = sp.integrate(x, x, x) + c[2] * x + c[3]                      # [15,30]
p30 = sp.integrate(120 - 3 * x, x, x)
a2, b2 = sp.symbols('a2 b2')
Y2b = p30 + a2 * x + b2                                            # [30,40]
s = sp.solve([sp.Eq(Y2b.subs(x, 30), Y2a.subs(x, 30)),
              sp.Eq(sp.diff(Y2b, x).subs(x, 30), sp.diff(Y2a, x).subs(x, 30))],
             [a2, b2], dict=True)[0]
Y2b = sp.expand(Y2b.subs(s))
Y3a = p30 + c[4] * x + c[5]                                        # [40,50]
p50 = sp.integrate(x - 80, x, x)
a4, b4 = sp.symbols('a4 b4')
Y3b = p50 + a4 * x + b4                                            # [50,80]
s2 = sp.solve([sp.Eq(Y3b.subs(x, 50), Y3a.subs(x, 50)),
               sp.Eq(sp.diff(Y3b, x).subs(x, 50), sp.diff(Y3a, x).subs(x, 50))],
              [a4, b4], dict=True)[0]
Y3b = sp.expand(Y3b.subs(s2))

SOL = sp.solve([
    sp.Eq(Y1.subs(x, XA), 0),                              # A 支承
    sp.Eq(Y2a.subs(x, XB), 0),                             # B 支承
    sp.Eq(Y3a.subs(x, XD), 0),                             # D 支承
    sp.Eq(Y3b.subs(x, XE), 0),                             # E 支承
    sp.Eq(sp.diff(Y1, x).subs(x, XF), sp.diff(Y2a, x).subs(x, XF)),   # F 處 θ 連續
    sp.Eq(Y2b.subs(x, XC), Y3a.subs(x, XC)),               # 內鉸 C 處 y 連續
], list(c), dict=True)[0]
Y1, Y2a, Y2b, Y3a, Y3b = (sp.expand(f.subs(SOL)) for f in (Y1, Y2a, Y2b, Y3a, Y3b))


def Y(p):
    if p < XF:  return Y1.subs(x, p)
    if p == XF: return None
    if p <= XB: return Y2a.subs(x, p)
    if p <= XC: return Y2b.subs(x, p)
    if p <= XD: return Y3a.subs(x, p)
    return Y3b.subs(x, p)


yFm, yFp = Y1.subs(x, XF), Y2a.subs(x, XF)
DELTA = sp.nsimplify(yFp - yFm)
print("EI·y(F−) =", sp.nsimplify(yFm))
print("EI·y(F+) =", sp.nsimplify(yFp))
print("Δ = y(F+) − y(F−) =", DELTA)
print("EI·θ(A) =", sp.nsimplify(sp.diff(Y1, x).subs(x, 0)))
print("EI·y(C=40) =", sp.nsimplify(Y2b.subs(x, XC)), "=", sp.nsimplify(Y3a.subs(x, XC)))
print()

IL1 = sp.expand(Y1 / DELTA); IL2a = sp.expand(Y2a / DELTA)
IL2b = sp.expand(Y2b / DELTA); IL3a = sp.expand(Y3a / DELTA); IL3b = sp.expand(Y3b / DELTA)
SEG = [(0, 15, IL1), (15, 30, IL2a), (30, 40, IL2b), (40, 50, IL3a), (50, 80, IL3b)]
print("分段影響線方程（EI 消掉）")
for a, b, f in SEG:
    print(f"  {a:2d} ≤ x ≤ {b:2d} :  {sp.nsimplify(sp.factor(sp.simplify(f)))}")
print()
print("關鍵縱距")
for lab, v in [("A(0)", IL1.subs(x, 0)), ("F−(15)", IL1.subs(x, 15)),
               ("F+(15)", IL2a.subs(x, 15)), ("B(30)", IL2a.subs(x, 30)),
               ("C(40)", IL2b.subs(x, 40)), ("D(50)", IL3a.subs(x, 50)),
               ("E(80)", IL3b.subs(x, 80))]:
    print(f"  {lab:8s} {str(sp.nsimplify(v)):>10s} = {float(v): .6f}")

# 段內極值
for a, b, f in SEG:
    d = sp.diff(f, x)
    for r in sp.solve(d, x):
        if r.is_real and a < float(r) < b:
            print(f"  極值 x={float(r):.4f}  v={float(f.subs(x, r)): .6f}")

# ── 獨立路徑：釋放 R_A ─────────────────────────────────
import subprocess, sys
print("\n--- 與『釋放 R_A』路徑對照 ---")
ns = {}
exec(open("/tmp/verify_2015_2.py").read().split("print('EI·y(A)")[0], ns)
YaR, YbR, YcR, YdR, yAR, xR = ns['Ya'], ns['Yb'], ns['Yc'], ns['Yd'], ns['yA'], ns['x']


def ILRA(p):
    f = YaR if p <= 30 else YbR if p <= 40 else YcR if p <= 50 else YdR
    return f.subs(xR, p) / yAR


bad = 0
for k in range(0, 321):
    p = k * 0.25
    here = float(IL1.subs(x, p)) if p < 15 else \
        float(IL2a.subs(x, p)) if p <= 30 else float(IL2b.subs(x, p)) if p <= 40 else \
        float(IL3a.subs(x, p)) if p <= 50 else float(IL3b.subs(x, p))
    ref = float(ILRA(p)) - (1 if p < 15 else 0)
    if abs(here - ref) > 1e-9:
        bad += 1
        print("  MISMATCH", p, here, ref)
print(f"  321 個載重位置，不符點數 = {bad}")
