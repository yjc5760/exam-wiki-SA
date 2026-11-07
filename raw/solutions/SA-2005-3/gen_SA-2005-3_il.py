#!/usr/bin/env python3
"""SA-2005-3：BC 跨中點 D 之彎矩影響線（每隔 2.5 m）— 解題圖解（struct-diagram，2026-11-07）

用法：python3 gen_SA-2005-3_il.py [輸出目錄]；之後以 struct-diagram 的 render.py 產生 2× PNG。

數值來源：SA-2005-3.md §4 Step 2–4（三彎矩方程式；2026-11-07 盲解比對「一致」）
  AB 跨（x = 0–10）：M_B = −x(100 − x²)/400，M_D = M_B/2
  BC 跨（x' = x − 10）：M_B = −x'(10 − x')(20 − x')/400，M_D = M_D,simple + M_B/2
鐵則：九個縱距由上式以分數算出並與 §4 Step 4 總表逐一比對；
自我檢核：另以「簡支梁 AC 柔度法求 R_B，再由右側自由體求 M_D」獨立重算 401 個載重位置。
"""
import sys, os
from fractions import Fraction as Fr

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2005-3"

# ── 幾何（題目正本判讀清單 #1–#5）──
L1 = L2 = Fr(10)
XA, XB, XC = Fr(0), L1, L1 + L2
XD = XB + L2 / 2
STA = [("A", XA, "（滾支承）"), ("B", XB, "（鉸支承）"), ("D", XD, "（BC 中點）"), ("C", XC, "（滾支承）")]


# ── §4 三彎矩方程式 ──
def MB(x):
    if x <= XB:
        return -x * (L1 ** 2 - x ** 2) / (4 * (L1 + L2) * L1) * 2   # 40 M_B = −x(100−x²)/10
    xp = x - XB
    return -xp * (L2 - xp) * (2 * L2 - xp) / (4 * (L1 + L2) * L2) * 2


def MD(x):
    if x <= XB:
        return MB(x) / 2
    xp = x - XB
    simple = xp / 2 if xp <= L2 / 2 else (L2 - xp) / 2
    return simple + MB(x) / 2


# ── 獨立檢核：簡支梁 AC（L = 20）柔度法 ──
def _delta(a, b, L=XC):
    """簡支梁上 a 處單位力在 b 處的撓度 ×EI"""
    if a > b:
        a, b = b, a
    return a * (L - b) * (2 * L * b - a * a - b * b) / (6 * L)


def _selftest():
    for i in range(401):
        x = XC * Fr(i, 400)
        RB = _delta(x, XB) / _delta(XB, XB)
        RC = (x - XB * RB) / XC
        md = RC * (XC - XD) - (x - XD if x > XD else 0)
        assert md == MD(x), (x, md, MD(x))


_selftest()

GRID = [Fr(5, 2) * i for i in range(9)]
TABLE = [0, Fr(-75, 256), Fr(-15, 32), Fr(-105, 256), 0, Fr(215, 256), Fr(65, 32), Fr(245, 256), 0]
assert [MD(x) for x in GRID] == TABLE                    # §4 Step 4 總表


def fs(q):
    return "0" if q == 0 else f"{q.numerator:+d}/{q.denominator}"


# ══════════════════ 版面 ══════════════════
W, PADL, PADR = 1040, 90, 90
SX = (W - PADL - PADR) / float(XC)
PH = 400


def fig2_influence_line():
    """攔：(1) 把 AB 跨縱距畫成 0（以為載重不在 BC 跨就不影響 M_D）——連續梁的 AB 跨全為負；
    (2) 把 D 點峰值寫成簡支梁的 L/4 = 2.5（漏掉 M_B/2 的折減，正確為 65/32）；
    (3) 把 BC 跨畫成直線三角形——兩側都是曲線，只在 D 有尖點。"""
    cv = Canvas(W, PH, sx=SX, ox=PADL, oy=150)
    cv.panel("IL of M_{D}（D 為 BC 跨中點）",
             "穆勒法：D 處插入鉸並施加單位相對轉角　│　AB 跨為負、BC 跨為正、D 處尖點；縱距單位 m（tf·m/tf）")
    for nm, x, sup in STA:
        p = cv.X(float(x))
        cv.parts.append(f'<line x1="{p:.2f}" y1="72" x2="{p:.2f}" y2="{PH - 34}" '
                        f'stroke="#E6EAF0" stroke-width="1" stroke-dasharray="3 4"/>')
        cv.text_px(p, PH - 18, nm + sup, 12.5, "#9AA4B2", weight="700")
    k = 60.0 / SX
    f = lambda t: float(MD(Fr(t).limit_denominator(10 ** 6)))
    for a, b in ((0.0, float(XB)), (float(XB), float(XD)), (float(XD), float(XC))):
        xs = [a + (b - a) * i / 400 for i in range(401)]
        cv.polygon([(a, 0.0)] + [(x, f(x) * k) for x in xs] + [(b, 0.0)], C["fill_m"])
        cv.poly([(x, f(x) * k) for x in xs], C["bmd"], 2.4)          # D 處連續（尖點），不畫垂直邊
    cv.line((0, 0), (float(XC), 0), C["muted"], 1.6)
    for x, v in zip(GRID, TABLE):
        xf, vf = float(x), float(v)
        cv.parts.append(f'<line x1="{cv.X(xf):.2f}" y1="{cv.Y(0):.2f}" x2="{cv.X(xf):.2f}" '
                        f'y2="{cv.Y(vf * k):.2f}" stroke="{C["bmd"]}" stroke-width="1.2" stroke-dasharray="2 3"/>')
        cv.dot((xf, vf * k), 4.0, fill=C["bmd"])
        if v == 0:
            continue
        up = v > 0
        dx = {Fr(25, 2): -46, Fr(35, 2): 46}.get(x, 0)       # 斜線兩側的標註往外移，避免壓線
        cv.text_px(cv.X(xf) + dx, cv.Y(vf * k) + (-30 if up else 22), fs(v), 13, C["bmd"], weight="700")
        cv.text_px(cv.X(xf) + dx, cv.Y(vf * k) + (-14 if up else 38), f"{vf:+.3f}", 12, C["muted"])
    for x in GRID:
        cv.text_px(cv.X(float(x)), cv.Y(0) - 10 if x <= XB else cv.Y(0) + 14,
                   f"{float(x):g}", 11, "#9AA4B2")
    cv.text_px(cv.X(float(XD)) + 14, cv.Y(float(TABLE[6]) * k) + 2, "最大（尖點）", 12.5,
               C["accent"], weight="700", anchor="start")
    return compose([cv], note="D 點縱距 65/32 = 簡支梁 L/4 = 2.5 減去 B 點彎矩之半 15/32；"
                              "載重在 AB 跨時 BC 跨只受 B 端負彎矩，D 點取其一半，故整跨為負",
                   path=f"{OUT}/{TAG}-fig-2-influence-line.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig2_influence_line()
    print("寫出", f"{TAG}-fig-2-influence-line.svg")
    for x, v in zip(GRID, TABLE):
        print(f"  x = {float(x):5.1f}   M_D = {str(v):>9}   = {float(v):+.4f}")
