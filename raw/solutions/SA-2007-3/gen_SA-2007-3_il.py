#!/usr/bin/env python3
"""SA-2007-3：A 點反力、FG 桿內力影響線與卡車最不利位置 — 解題圖解（struct-diagram，2026-11-07）

用法：python3 gen_SA-2007-3_il.py [輸出目錄]；之後以 struct-diagram 的 render.py 產生 2× PNG。

數值來源：SA-2007-3.md §4 Step 1–3、§5（2026-11-07 盲解比對「一致」）
  上弦 E–I 受載（x 自 E 起算，0–48 m）
  A_y = (48 − x)/48；A_x（向右）= x/34（x ≤ 24）、(48 − x)/34（x ≥ 24），G 處 12/17
  F_FG：E 0、F −81/85、G 42/85、H 21/85、I 0（拉為正）
  卡車由右往左 ①20 ②40 ③40 ④40 kN（2.4、1.5、1.5 m）
  A_y,max = 130.25 kN（① 在 E）；同位置 A_x = 13.76、合力 130.97 kN（並列；精確 468/34 = 13.765 ⇒ 130.975）
  F_FG 壓力最大 −115.22 kN（③ 在 F）；拉力最大 59.68 kN（② 在 G）
鐵則：節點縱距另以「全桁架節點法」（A、B 兩鉸，18 式 18 未知）解出比對；
      三個極值與合力最大值另以卡車位置逐 1 cm 掃描確認。
"""
import sys, os, math
from fractions import Fraction as Fr

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2007-3"

# ── 幾何（題目正本判讀清單 #1–#5）──
N = {"A": (0, 0), "B": (48, 0), "E": (0, 17), "F": (12, 17), "G": (24, 17), "H": (36, 17),
     "I": (48, 17), "C": (12, 12), "D": (36, 12)}
M = [("E", "F"), ("F", "G"), ("G", "H"), ("H", "I"), ("A", "E"), ("I", "B"), ("F", "C"), ("H", "D"),
     ("A", "C"), ("E", "C"), ("C", "G"), ("G", "D"), ("D", "I"), ("D", "B")]
SPAN = 48
DECK = ["E", "F", "G", "H", "I"]
AXLE_OFF = [Fr(0), Fr(24, 10), Fr(39, 10), Fr(54, 10)]
AXLE_P = [20, 40, 40, 40]


def _solve(A, b):
    n = len(A)
    A = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(A[r][c]))
        A[c], A[p] = A[p], A[c]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c] / A[c][c]
                A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    return [A[i][n] / A[i][i] for i in range(n)]


def truss(node):
    """上弦節點 node 受向下單位力：回傳 (A_y, A_x 向右, F_FG 拉＋)"""
    nodes = list(N)
    unk = M + ["Ax", "Ay", "Bx", "By"]
    A = [[0.0] * len(unk) for _ in range(2 * len(nodes))]
    rhs = [0.0] * (2 * len(nodes))
    for k, (i, j) in enumerate(M):
        (xi, yi), (xj, yj) = N[i], N[j]
        L = math.hypot(xj - xi, yj - yi)
        cx, cy = (xj - xi) / L, (yj - yi) / L
        r, s = nodes.index(i), nodes.index(j)
        A[2 * r][k] += cx; A[2 * r + 1][k] += cy
        A[2 * s][k] -= cx; A[2 * s + 1][k] -= cy
    for nm, ox in (("A", 0), ("B", 2)):
        r = nodes.index(nm)
        A[2 * r][len(M) + ox] = 1.0
        A[2 * r + 1][len(M) + ox + 1] = 1.0
    rhs[2 * nodes.index(node) + 1] += 1.0
    sol = _solve(A, rhs)
    return sol[len(M) + 1], sol[len(M)], sol[M.index(("F", "G"))]


# ── §4 影響線（閉合式／節點值，節點間直線）──
def IL_Ay(x):
    return (SPAN - Fr(x)) / SPAN


def IL_Ax(x):
    x = Fr(x)
    return x / 34 if x <= 24 else (SPAN - x) / 34


FG_NODES = [(0, Fr(0)), (12, Fr(-81, 85)), (24, Fr(42, 85)), (36, Fr(21, 85)), (48, Fr(0))]


def IL_FG(x):
    x = Fr(x)
    for (x0, v0), (x1, v1) in zip(FG_NODES, FG_NODES[1:]):
        if x0 <= x <= x1:
            return v0 + (v1 - v0) * (x - x0) / (x1 - x0)
    raise ValueError(x)


def _selftest():
    for n_ in DECK:
        ay, ax, fg = truss(n_)
        x = N[n_][0]
        assert abs(ay - float(IL_Ay(x))) < 1e-9, n_
        assert abs(ax - float(IL_Ax(x))) < 1e-9, n_
        assert abs(fg - float(IL_FG(x))) < 1e-9, n_
    # F_FG 閉合式 (12A_x − 12A_y + M_C)/5（§4 Step 2）在各段與節點直線一致
    for i in range(481):
        x = Fr(i, 10)
        mc = 12 - x if x <= 12 else 0
        assert (12 * IL_Ax(x) - 12 * IL_Ay(x) + mc) / 5 == IL_FG(x), x


_selftest()


def response(il, head):
    tot = Fr(0)
    for off, p in zip(AXLE_OFF, AXLE_P):
        x = head + off
        if 0 <= x <= SPAN:
            tot += p * il(x)
    return tot


H_AY, H_C, H_T = Fr(0), 12 - AXLE_OFF[2], 24 - AXLE_OFF[1]
AY_MAX = response(IL_Ay, H_AY)
AX_AT = response(IL_Ax, H_AY)
R_AT = math.hypot(float(AY_MAX), float(AX_AT))
FG_C = response(IL_FG, H_C)
FG_T = response(IL_FG, H_T)
assert AY_MAX == Fr(52100, 400) and AX_AT == Fr(468, 34)                     # 130.25、13.76
assert abs(R_AT - 130.97) < 0.01          # §4 130.97（以 A_x ≈ 13.76 計）；精確值 130.975
assert FG_C == Fr(-97935, 850) and FG_T == Fr(5073, 85)                       # −115.22、59.68
_heads = [Fr(i, 100) - Fr(54, 10) for i in range(0, 5341)]                   # 逐 1 cm 掃描
assert max(response(IL_Ay, h) for h in _heads) == AY_MAX
assert min(response(IL_FG, h) for h in _heads) == FG_C
assert max(response(IL_FG, h) for h in _heads) == FG_T
assert max(math.hypot(float(response(IL_Ay, h)), float(response(IL_Ax, h))) for h in _heads) == R_AT


# ══════════════════ 版面 ══════════════════
W, PADL, PADR = 1040, 80, 80
PH = 420
SX = (W - PADL - PADR) / SPAN


def base_panel(PH, oy, title, sub):
    cv = Canvas(W, PH, sx=SX, ox=PADL, oy=oy)
    cv.panel(title, sub)
    labs = {"E": "E（A 正上方）", "G": "G（上弦中央鉸接點）", "I": "I（B 正上方）"}
    for n_ in DECK:
        p = cv.X(N[n_][0])
        cv.parts.append(f'<line x1="{p:.2f}" y1="72" x2="{p:.2f}" y2="{PH - 34}" '
                        f'stroke="#E6EAF0" stroke-width="1" stroke-dasharray="3 4"/>')
        cv.text_px(p, PH - 18, labs.get(n_, n_), 12.5, "#9AA4B2", weight="700")
    return cv


def draw_il(cv, il, xs, k, col, fill):
    pts = [(x, float(il(x)) * k) for x in xs]
    cv.polygon([(0, 0.0)] + pts + [(SPAN, 0.0)], fill)
    cv.poly(pts, col, 2.4)
    cv.line((0, 0), (SPAN, 0), C["muted"], 1.6)


def draw_truck(cv, il, head, k, label_dx=-6):
    ys = [float(il(head + o)) * k for o in AXLE_OFF]
    top = max(max(ys), 0.0)
    for off, y in zip(AXLE_OFF, ys):
        x = float(head + off)
        cv.parts.append(f'<line x1="{cv.X(x):.2f}" y1="{cv.Y(0):.2f}" x2="{cv.X(x):.2f}" y2="{cv.Y(y):.2f}" '
                        f'stroke="{C["load"]}" stroke-width="1.2" stroke-dasharray="2 3"/>')
        cv.dot((x, y), 3.4, fill=C["load"])
        cv.arrow((x, top + 50 / SX), (x, top + 12 / SX), C["load"], 2.2, head=7)
    cv.text_px(cv.X(float(head)) + label_dx, cv.Y(top) - 60, "← ① 20　② 40　③ 40　④ 40 kN", 12.5,
               C["load"], weight="700", anchor="start")


def fig2_influence_lines():
    """攔：(1) 把 A_x 當成 0（以為兩鉸支承桁架像簡支梁）——G 為兩半唯一共用節點，是三鉸拱，有水平推力；
    (2) F_FG 只看到 F 處的負峰值而漏掉 G–H 段為正——同一根桿件會受壓也會受拉，兩個極值都要求；
    (3) 壓力最大時把 ② 放在 F——以 ③ 在 F 才是最大（−115.22 kN），經逐點掃描確認。"""
    p1 = base_panel(PH, 110, "IL of A_{y}（A 點垂直反力）＋ 最不利位置：車頭 ① 在 E",
                    "整體對 B 取矩　│　直線 1 → 0；縱距無因次")
    k1 = 170.0 / SX
    draw_il(p1, IL_Ay, [0, 48], k1, C["deform"], C["fill_c"])
    p1.text_px(p1.X(0) - 10, p1.Y(k1), "1", 13, C["deform"], weight="700", anchor="end")
    draw_truck(p1, IL_Ay, H_AY, k1)
    p1.text_px(W / 2 + 120, PH - 76,
               f"A_{{y,max}} = {float(AY_MAX):g} kN（主答案）",
               14, C["text"], weight="700")
    p1.text_px(W / 2 + 120, PH - 52,
               f"同車位 A_{{x}} = 468/34 = {float(AX_AT):.3f} kN　⇒　合力 {R_AT:.3f} kN（並列）",
               13, C["muted"])

    p2 = base_panel(PH, 130, "IL of A_{x}（A 點水平反力，向右為正）",
                    "G 為上弦鉸接點：另半邊對 G 取矩　│　三角形，峰值在 G")
    k2 = 220.0 / SX
    draw_il(p2, IL_Ax, [0, 24, 48], k2, C["deform"], C["fill_c"])
    p2.dot((24, float(IL_Ax(24)) * k2), 4.0, fill=C["deform"])
    p2.text_px(p2.X(24), p2.Y(float(IL_Ax(24)) * k2) - 15,
               f"12/17 = {float(IL_Ax(24)):.4f}", 13, C["deform"], weight="700")

    p3 = base_panel(PH, 200, "IL of F_{FG}（FG 桿內力，拉為正）＋ 兩個最不利位置",
                    "切 FG、CG，對 C 取矩：F_{FG} = (12A_{x} − 12A_{y} + M_{C})/5　│　F 處負峰、G 處正峰")
    k3 = 130.0 / SX
    draw_il(p3, IL_FG, [x for x, _ in FG_NODES], k3, C["sfd"], C["fill_s"])
    for x, v in FG_NODES[1:-1]:
        p3.dot((x, float(v) * k3), 4.0, fill=C["sfd"])
    p3.text_px(p3.X(12) - 70, p3.Y(float(FG_NODES[1][1]) * k3) + 8, "−81/85 = −0.953（F）", 13,
               C["sfd"], weight="700", anchor="end")
    p3.text_px(p3.X(36), p3.Y(float(FG_NODES[3][1]) * k3) - 14, "21/85 = 0.247（H）", 13,
               C["sfd"], weight="700")
    p3.text_px(p3.X(24) - 18, p3.Y(float(FG_NODES[2][1]) * k3) + 4, "42/85 = 0.494（G）", 13,
               C["sfd"], weight="700", anchor="end")
    draw_truck(p3, IL_FG, H_C, k3, label_dx=-150)
    draw_truck(p3, IL_FG, H_T, k3, label_dx=-6)
    p3.text_px(p3.X(36), p3.Y(0) + 74,
               f"③ 在 F：F_{{FG}} = {float(FG_C):.2f} kN（壓力最大）", 13.5, C["text"], weight="700")
    p3.text_px(p3.X(36), p3.Y(0) + 46,
               f"② 在 G：F_{{FG}} = +{float(FG_T):.2f} kN（拉力最大）", 13.5, C["text"], weight="700")
    return compose([p1, p2, p3], cols=1,
                   note="載重在上弦 E–I 移動、由節點傳力，節點間以直線連接；卡車由右往左、① 為車頭；"
                        "四個極值均經卡車位置逐 1 cm 掃描確認",
                   path=f"{OUT}/{TAG}-fig-2-influence-lines.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig2_influence_lines()
    print("寫出", f"{TAG}-fig-2-influence-lines.svg")
    print(f"A_y,max = {float(AY_MAX)}  A_x = {float(AX_AT):.4f}  合力 = {R_AT:.4f}")
    print(f"F_FG 壓 = {float(FG_C):.4f}  拉 = {float(FG_T):.4f}")
    for n_ in DECK:
        print(f"  {n_}: " + "  ".join(f"{v:+.5f}" for v in truss(n_)))
