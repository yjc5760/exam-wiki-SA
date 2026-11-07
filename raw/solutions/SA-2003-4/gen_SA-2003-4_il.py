#!/usr/bin/env python3
"""SA-2003-4：B 點彎矩、剪力影響線 — 解題圖解（struct-diagram，2026-11-07）

用法：python3 gen_SA-2003-4_il.py [輸出目錄]；之後以 struct-diagram 的 render.py 產生 2× PNG。

數值來源：SA-2003-4.md §4 Step 1–3（2026-11-07 盲解比對「一致」）
  C_y(x) = (30x² − x³)/2000
  V_B = −C_y（0 ≤ x < 5）、1 − C_y（5 < x ≤ 10）
  M_B = 5C_y（0 ≤ x ≤ 5）、5C_y − (x − 5)（5 < x ≤ 10）
鐵則：縱距、跳躍、極值全部由下方函數算出；改 L 或 XB 重跑，曲線與標註一起變。
自我檢核：C_y 另以馬克士威互惠（懸臂梁端點載重撓度 ÷ δ_CC）核對；
          每個載重位置以「左側自由體」重算 V_B、M_B（含固定端反力）與右側結果一致。
"""
import sys, os
from fractions import Fraction as Fr

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2003-4"

# ── 幾何（題目正本判讀清單 #1）──
L = Fr(10)           # A(0) 固定端 — C(10) 滾支承
XB = Fr(5)           # B 為梁中點，不是內鉸
STA = [("A", 0), ("B", XB), ("C", L)]


# ── §4 Step 1：贅力 C_y ──
def Cy(x):
    return (3 * L * x ** 2 - x ** 3) / (2 * L ** 3)


# ── §4 Step 2、3：B 點內力（右側自由體 BC）──
def VB(x, right=False):
    on_BC = (x > XB) or (right and x == XB)
    return (1 if on_BC else 0) - Cy(x)


def MB(x):
    return (L - XB) * Cy(x) - (x - XB if x > XB else 0)


def _selftest():
    for i in range(201):
        x = L * Fr(i, 200)
        # 馬克士威互惠：懸臂梁 C 端單位力在 x 處撓度 x²(3L−x)/(6EI) ÷ δ_CC = L³/(3EI)
        assert Cy(x) == (x ** 2 * (3 * L - x) / 6) / (L ** 3 / 3)
        # 左側自由體 AB：固定端反力 A_y = 1 − C_y，M_A（逆時針為正）= x − C_y·L
        Ay, MA = 1 - Cy(x), x - Cy(x) * L
        left_load = 1 if x <= XB else 0     # x = 5 取 5⁻（載重在斷面左側）
        assert Ay - left_load == VB(x)                           # V_B（左側自由體）
        assert -MA + Ay * XB - left_load * (XB - x) == MB(x)    # M_B（左側自由體，下緣受拉為正）
    assert VB(XB, True) - VB(XB) == 1                            # 單位跳躍


_selftest()

V_L, V_R, M_PK = VB(XB), VB(XB, True), MB(XB)
assert (V_L, V_R, M_PK) == (Fr(-5, 16), Fr(11, 16), Fr(25, 16))   # 與 §4 關鍵影響值一致


def fs(q):
    q = Fr(q)
    return "0" if q == 0 else (f"{q.numerator:+d}" if q.denominator == 1 else f"{q.numerator:+d}/{q.denominator}")


# ══════════════════ 版面 ══════════════════
W, PADL, PADR = 1000, 90, 90
SX = (W - PADL - PADR) / float(L)
PH = 280


def guides(cv):
    for nm, x in STA:
        p = cv.X(float(x))
        cv.parts.append(f'<line x1="{p:.2f}" y1="72" x2="{p:.2f}" y2="{PH - 34}" '
                        f'stroke="#E6EAF0" stroke-width="1" stroke-dasharray="3 4"/>')
    for (nm, x), sup in zip(STA, ("（固定端）", "（梁中點）", "（滾支承）")):
        cv.text_px(cv.X(float(x)), PH - 18, nm + sup, 12.5, "#9AA4B2", weight="700")


def il_panel(title, sub, segs, keys, pxu, col, fill, jumps=(), base=100):
    cv = Canvas(W, PH, sx=SX, ox=PADL, oy=base)
    cv.panel(title, sub)
    guides(cv)
    k = pxu / SX
    for a, b, fn in segs:
        xs = [a + (b - a) * i / 400 for i in range(401)]
        cv.polygon([(a, 0.0)] + [(x, fn(x) * k) for x in xs] + [(b, 0.0)], fill, col, 2.4)
    for xj, v1, v2 in jumps:
        cv.line((xj, v1 * k), (xj, v2 * k), C["accent"], 2.4, dash="4 3")
    cv.line((0, 0), (float(L), 0), C["muted"], 1.6)
    for lab, x, v, dx, dy in keys:
        cv.dot((x, v * k), 4.0, fill=col)
        cv.text_px(cv.X(x) + dx, cv.Y(v * k) + dy, lab, 13.5, col, weight="700")
    return cv


def fig2_influence_lines():
    """攔：(1) 把 M_B 影響線畫成靜定梁的直線三角形（本題一度靜不定，兩段都是三次曲線）；
    (2) V_B 在 B 左側的符號——A 為固定端，載重在 AB 時 V_B 為負，不是 0；
    (3) 跳躍量必為 1，左右兩值是 −5/16 與 +11/16，不是 ∓1/2。"""
    xb, l = float(XB), float(L)
    fM = lambda x: float(MB(Fr(x).limit_denominator(10 ** 6)))
    fVl = lambda x: float(VB(Fr(x).limit_denominator(10 ** 6)))
    fVr = lambda x: float(VB(Fr(x).limit_denominator(10 ** 6), True))
    pM = il_panel("IL of M_{B}",
                  "穆勒法：B 處插入鉸並施加單位相對轉角　│　全線為正，B 處尖點；縱距單位 m",
                  [(0.0, l, fM)],
                  [(f"{fs(M_PK)} = {float(M_PK):.4f} m（最大）", xb, float(M_PK), 0, -16)],
                  80.0, C["bmd"], C["fill_m"], base=70)
    pV = il_panel("IL of V_{B}",
                  "穆勒法：B 處切開、兩側保持平行並錯動單位位移　│　縱距無因次",
                  [(0.0, xb, fVl), (xb, l, fVr)],
                  [(f"{fs(V_L)} = {float(V_L):.4f}（B 左）", xb, float(V_L), -96, 6),
                   (f"{fs(V_R)} = {float(V_R):.4f}（B 右）", xb, float(V_R), 96, -6)],
                  140.0, C["sfd"], C["fill_s"],
                  jumps=[(xb, float(V_L), float(V_R))], base=100)
    pV.text_px(pV.X(xb) + 16, pV.Y(0) + 14, "跳躍 = 1", 12.5, C["accent"], weight="700", anchor="start")
    return compose([pM, pV], cols=1,
                   note="兩條都是曲線（一度靜不定）；端點 A、C 縱距皆為 0。"
                        "剪力左段為負：載重在 AB 時，B 斷面右側只受 C 點向上反力",
                   path=f"{OUT}/{TAG}-fig-2-influence-lines.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig2_influence_lines()
    print("寫出", f"{TAG}-fig-2-influence-lines.svg")
    print(f"M_B(5) = {M_PK}   V_B(5-) = {V_L}   V_B(5+) = {V_R}")
    for x in (0, 2.5, 5, 7.5, 10):
        q = Fr(x).limit_denominator(100)
        print(f"  x = {x:4}   C_y = {float(Cy(q)):.4f}   M_B = {float(MB(q)):+.4f}   V_B = {float(VB(q, True)):+.4f}")
