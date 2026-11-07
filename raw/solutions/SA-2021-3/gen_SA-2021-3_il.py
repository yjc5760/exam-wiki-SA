#!/usr/bin/env python3
"""SA-2021-3：a 點水平反力、ab 桿、bg 桿軸力影響線 — 解題圖解（struct-diagram，2026-11-07）

用法：python3 gen_SA-2021-3_il.py [輸出目錄]；之後以 struct-diagram 的 render.py 產生 2× PNG。

數值來源：SA-2021-3.md §4 Step 3–5（柔度法，贅力取 e 點水平反力；2026-11-07 盲解比對「一致」）
  H_a：a 0、b 3/8、c 9/16、d 3/8、e 0（向右為正）
  S_ab：0、3/16、−3/16、−3/16、0（拉為正）
  S_bg：0、5/16、−5/8、−5/16、0（拉為正）
鐵則：各縱距由下方「全桁架節點法＋柔度法」以分數重新解出，與 §4 數值逐一比對後才畫；
      載重沿底弦移動、由節點傳力，節點間以直線連接。
"""
import sys, os
from fractions import Fraction as Fr

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2021-3"

# ── 幾何（題目正本判讀清單 #1–#4）──
N = {"a": (0, 0), "b": (3, 0), "c": (6, 0), "d": (9, 0), "e": (12, 0),
     "f": (3, 4), "g": (6, 4), "h": (9, 4)}
M = [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("f", "g"), ("g", "h"),
     ("a", "f"), ("h", "e"), ("f", "b"), ("g", "c"), ("h", "d"), ("b", "g"), ("g", "d")]
BOTTOM = ["a", "b", "c", "d", "e"]


def _geom(i, j):
    (xi, yi), (xj, yj) = N[i], N[j]
    dx, dy = xj - xi, yj - yi
    L = Fr(int(round((dx * dx + dy * dy) ** 0.5)))       # 本桁架桿長皆為整數（3、4、5）
    assert L * L == dx * dx + dy * dy
    return L, Fr(dx) / L, Fr(dy) / L


def _solve(A, b):
    n = len(A)
    A = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[p] = A[p], A[c]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c] / A[c][c]
                A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    return [A[i][n] / A[i][i] for i in range(n)]


def static_forces(loads):
    """基本結構（a 鉸、e 滾，靜定）：節點法聯立。loads：{節點: (Fx, Fy)}；回傳 {桿: 軸力（拉＋）}"""
    nodes = list(N)
    unk = M + ["Ax", "Ay", "Ey"]
    A = [[Fr(0)] * len(unk) for _ in range(2 * len(nodes))]
    rhs = [Fr(0)] * (2 * len(nodes))
    for k, (i, j) in enumerate(M):
        L, cx, cy = _geom(i, j)
        r, s = nodes.index(i), nodes.index(j)
        A[2 * r][k] += cx; A[2 * r + 1][k] += cy
        A[2 * s][k] -= cx; A[2 * s + 1][k] -= cy
    A[2 * nodes.index("a")][len(M)] = Fr(1)
    A[2 * nodes.index("a") + 1][len(M) + 1] = Fr(1)
    A[2 * nodes.index("e") + 1][len(M) + 2] = Fr(1)
    for n_, (fx, fy) in loads.items():
        r = nodes.index(n_)
        rhs[2 * r] -= fx; rhs[2 * r + 1] -= fy
    sol = _solve(A, rhs)
    return dict(zip(M, sol[:len(M)]))


# 單位水平力一對（a 向左、e 向右，拉開）
U = static_forces({"a": (-1, 0), "e": (1, 0)})
F_EE = sum(U[m] ** 2 * _geom(*m)[0] for m in M)                    # ×1/EA
assert F_EE == 12                                                     # §4 Step 1


def at_node(n_):
    """單位向下力在底弦節點 n_：回傳 (H_a 向右, S_ab, S_bg)"""
    S0 = static_forces({n_: (0, -1)})
    X = -sum(S0[m] * U[m] * _geom(*m)[0] for m in M) / F_EE         # 拉開方向贅力
    S = {m: S0[m] + X * U[m] for m in M}
    return -X, S[("a", "b")], S[("b", "g")]


VALS = {n_: at_node(n_) for n_ in BOTTOM}
HA = [VALS[n_][0] for n_ in BOTTOM]
SAB = [VALS[n_][1] for n_ in BOTTOM]
SBG = [VALS[n_][2] for n_ in BOTTOM]
assert HA == [0, Fr(3, 8), Fr(9, 16), Fr(3, 8), 0]                   # §4 Step 3
assert SAB == [0, Fr(3, 16), Fr(-3, 16), Fr(-3, 16), 0]              # §4 Step 4
assert SBG == [0, Fr(5, 16), Fr(-5, 8), Fr(-5, 16), 0]               # §4 Step 5
XS = [N[n_][0] for n_ in BOTTOM]


def fs(q):
    return "0" if q == 0 else f"{q.numerator:+d}/{q.denominator}"


# ══════════════════ 版面 ══════════════════
W, PADL, PADR = 1000, 110, 110
SX = (W - PADL - PADR) / 12
PH = 270


def il_panel(title, sub, vals, pxu, col, fill, base, notes=()):
    cv = Canvas(W, PH, sx=SX, ox=PADL, oy=base)
    cv.panel(title, sub)
    for nm, x in zip(BOTTOM, XS):
        p = cv.X(x)
        cv.parts.append(f'<line x1="{p:.2f}" y1="72" x2="{p:.2f}" y2="{PH - 34}" '
                        f'stroke="#E6EAF0" stroke-width="1" stroke-dasharray="3 4"/>')
        cv.text_px(p, PH - 18, nm, 12.5, "#9AA4B2", weight="700")
    k = pxu / SX
    pts = [(x, float(v) * k) for x, v in zip(XS, vals)]
    cv.polygon([(0, 0.0)] + pts + [(12, 0.0)], fill)
    cv.poly(pts, col, 2.4)
    cv.line((0, 0), (12, 0), C["muted"], 1.6)
    for x, v in zip(XS, vals):
        cv.dot((x, float(v) * k), 4.0, fill=col)
        if v != 0:
            cv.text_px(cv.X(x), cv.Y(float(v) * k) + (-15 if v > 0 else 18),
                       f"{fs(v)} = {float(v):+.4g}", 13, col, weight="700")
    for x, y, txt in notes:
        cv.text_px(cv.X(x), y, txt, 12.5, C["accent"], weight="700")
    return cv


def fig2_influence_lines():
    """攔：(1) 把 H_a 當成 0（以為鉸支承桁架像簡支梁）——兩端皆鉸，一度外部靜不定，底弦受推力；
    (2) S_ab 只用靜定值 9/16、6/16…（漏減推力），符號在 c、d 會整個反過來；
    (3) 以為推力也改變腹桿——推力只走底弦，S_bg 與靜定桁架相同。"""
    p1 = il_panel("IL of H_{a}（a 點水平反力，向右為正）",
                  "柔度法：H = ΣS^{0}uL ÷ Σu^{2}L（EA 相同）　│　全線為正、c 最大", HA,
                  140.0, C["deform"], C["fill_c"], base=85)
    p2 = il_panel("IL of S_{ab}（ab 桿軸力，拉為正）",
                  "S_{ab} = S^{0}_{ab} − H　│　b 為正、c–d 為負且等值（平頂）", SAB,
                  220.0, C["bmd"], C["fill_m"], base=135)
    p3 = il_panel("IL of S_{bg}（bg 桿軸力，拉為正）",
                  "推力只走底弦，與靜定桁架相同；剖面法 ΣF_{y}　│　b 為正、c、d 為負", SBG,
                  120.0, C["sfd"], C["fill_s"], base=125)
    k2 = 220.0 / SX
    y_flat = p2.Y(float(SAB[2]) * k2)
    p2.text_px(p2.X(7.5), y_flat + 40, "c–d 平頂：靜定值下降率 ＝ 推力下降率", 12.5, C["accent"], weight="700")
    return compose([p1, p2, p3], cols=1,
                   note="載重沿底弦移動、由節點傳力，節點間以直線連接；三條線端點 a、e 皆為 0",
                   path=f"{OUT}/{TAG}-fig-2-influence-lines.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig2_influence_lines()
    print("寫出", f"{TAG}-fig-2-influence-lines.svg")
    print("節點   H_a      S_ab     S_bg")
    for n_ in BOTTOM:
        print(f"  {n_}   " + "  ".join(f"{str(v):>7}" for v in VALS[n_]))
