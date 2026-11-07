#!/usr/bin/env python3
"""SA-2020-3：b 點反力影響線 — 解題圖解（struct-diagram，2026-11-07）

用法：python3 gen_SA-2020-3_il.py [輸出目錄]；之後以 struct-diagram 的 render.py 產生 2× PNG。

數值來源：SA-2020-3.md §4 Step 3–4（穆勒法：移除 b 支承、施加單位位移後的撓度曲線；2026-11-07 盲解比對「一致」）
  ab（0 ≤ x ≤ 2）：(−x³ + 21x)/34
  bc（2 ≤ x ≤ 4）：(x³ − 12x² + 45x − 16)/34
  cd（x₂ = x − 4，0 ≤ x₂ ≤ 3）：(x₂³ − 27x₂ + 54)/51
  b 點 = 1、最大值 19/17 @ x = 3、c 點 18/17、d 點 0
鐵則：曲線與極值由上式算出；另以單位載重法（∫ m_b·m_x / EI，cd 段 1.5EI）在 141 個載重位置獨立重算。
"""
import sys, os
from fractions import Fraction as Fr

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2020-3"

# ── 幾何（題目正本判讀清單 #1–#6）──
XA, XB, XC, XD = 0, 2, 4, 7
EI_AC, EI_CD = 1.0, 1.5
STA = [("a", XA, "（鉸支承）"), ("b", XB, "（滾支承）"), ("c", XC, "（內鉸）"), ("d", XD, "（固定端）")]


# ── §4 Step 3 影響線 ──
def By(x):
    x = Fr(x)
    if x <= XB:
        return (-x ** 3 + 21 * x) / 34
    if x <= XC:
        return (x ** 3 - 12 * x ** 2 + 45 * x - 16) / 34
    x2 = x - XC
    return (x2 ** 3 - 27 * x2 + 54) / 51


# ── 獨立檢核：單位載重法 ──
def m_b(t):                 # b 點向上單位力，基本結構（移除 b）的彎矩（下緣受拉為正）
    if t <= XB: return -0.5 * t
    if t <= XC: return 0.5 * t - 2
    return 0.5 * (t - XC)


def m_x(t, x):              # x 處向下單位力的彎矩
    if x <= XC:             # 載重在 a–c 簡支段：c 點把 x/4 傳給懸臂
        if t <= XC:
            return (1 - x / 4) * t - (t - x if t > x else 0.0)
        return -(x / 4) * (t - XC)
    return -(t - x if t > x else 0.0)   # 載重在懸臂 cd 上


def _integ(f, n=4000):
    tot = 0.0
    for a, b, ei in ((XA, XC, EI_AC), (XC, XD, EI_CD)):
        h = (b - a) / n
        tot += sum(f(a + (i + 0.5) * h) for i in range(n)) * h / ei
    return tot


F_BB = _integ(lambda t: m_b(t) ** 2)


def _selftest():
    assert abs(F_BB - 17 / 6) < 1e-6                                # f_bb = 17/(6EI)
    for i in range(141):
        x = XD * i / 140
        by = -_integ(lambda t: m_b(t) * m_x(t, x), n=1200) / F_BB
        assert abs(by - float(By(Fr(x).limit_denominator(10 ** 6)))) < 2e-4, (x, by)
    assert By(XB) == 1 and By(XC) == Fr(18, 17) and By(3) == Fr(19, 17) and By(XD) == 0
    assert By(XA) == 0
    grid = [Fr(XD) * Fr(i, 7000) for i in range(7001)]
    assert max(grid, key=By) == 3                                     # 全域最大在 x = 3


_selftest()


# ══════════════════ 版面 ══════════════════
W, PADL, PADR = 1000, 90, 90
SX = (W - PADL - PADR) / XD
PH = 360


def fig2_influence_line():
    """攔：(1) 以為反力影響線最大值一定在支承正上方（=1）——本題最大值 19/17 在 bc 段 x = 3 m；
    (2) 把 c（內鉸）以右畫成 0——cd 為懸臂，c 端隨 b 抬升而上翹，c 點 18/17；
    (3) 在內鉸 c 處畫成平滑——c 處只有位移連續、斜率不連續（折角）。"""
    cv = Canvas(W, PH, sx=SX, ox=PADL, oy=110)
    cv.panel("IL of R_{b}（b 點垂直反力，向上為正）",
             "穆勒法：移除 b 支承、b 點向上單位位移後的撓度曲線　│　縱距無因次；ab、bc 為 I，cd 為 1.5I")
    for nm, x, sup in STA:
        p = cv.X(x)
        cv.parts.append(f'<line x1="{p:.2f}" y1="72" x2="{p:.2f}" y2="{PH - 34}" '
                        f'stroke="#E6EAF0" stroke-width="1" stroke-dasharray="3 4"/>')
        cv.text_px(p, PH - 18, nm + sup, 12.5, "#9AA4B2", weight="700")
    k = 125.0 / SX
    col = C["deform"]
    segs = ((XA, XC), (XC, XD))
    for a, b in segs:
        xs = [a + (b - a) * i / 500 for i in range(501)]
        pts = [(x, float(By(Fr(x).limit_denominator(10 ** 6))) * k) for x in xs]
        cv.polygon([(a, 0.0)] + pts + [(b, 0.0)], C["fill_c"])
        cv.poly(pts, col, 2.4)
    cv.line((0, 0), (XD, 0), C["muted"], 1.6)
    keys = [("1（支承處）", XB, By(XB), -44, -16),
            ("19/17 ≈ 1.118（最大，x = 3 m）", 3, By(3), 0, -16),
            ("18/17 ≈ 1.059（c 點）", XC, By(XC), 92, -6)]
    for lab, x, v, dx, dy in keys:
        cv.dot((x, float(v) * k), 4.2, fill=C["accent"] if x == 3 else col)
        cv.text_px(cv.X(x) + dx, cv.Y(float(v) * k) + dy, lab, 13.5,
                   C["accent"] if x == 3 else col, weight="700")
    cv.text_px(cv.X(XD) - 6, cv.Y(0) + 18, "0（固定端：斜率 0）", 12.5, col, weight="700", anchor="end")
    cv.text_px(cv.X(XA) + 6, cv.Y(0) + 16, "0", 12.5, col, weight="700", anchor="start")
    cv.text_px(cv.X(XC) - 12, cv.Y(float(By(XC)) * k) + 30, "c 內鉸：斜率不連續（折角）", 12, C["muted"], anchor="end")
    return compose([cv], note="b 點抬升時 c 點不是固定點：c 由懸臂 cd 支承，跟著上翹 18/17，"
                              "使 bc 段比 b 點本身翹得更高",
                   path=f"{OUT}/{TAG}-fig-2-influence-line.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig2_influence_line()
    print("寫出", f"{TAG}-fig-2-influence-line.svg")
    print(f"f_bb·EI = {F_BB:.6f}（17/6 = {17/6:.6f}）")
    for x in (0, 1, 2, 2.5, 3, 3.5, 4, 5, 6, 7):
        print(f"  x = {x:3}   R_b = {float(By(Fr(x).limit_denominator(100))):+.4f}")
