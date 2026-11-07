#!/usr/bin/env python3
"""SA-2004-2：a 點反力、bc 桿內力影響線與卡車最不利位置 — 解題圖解（struct-diagram，2026-11-07）

用法：python3 gen_SA-2004-2_il.py [輸出目錄]；之後以 struct-diagram 的 render.py 產生 2× PNG。

數值來源：SA-2004-2.md §4 Step 1–3（2026-11-07 盲解比對「一致」）
  IL R_a = 1 − x/40；IL F_bc = 3x/40（0 ≤ x ≤ 10）、1 − x/40（10 ≤ x ≤ 40），峰值 0.75 @ b
  卡車由右往左：①20 ②40 ③40 ④40 kN，軸距 2.4、1.5、1.5 m
  R_a,max = 128.3 kN（① 在 a）；F_bc,max = 96.9 kN 拉（② 在 b）
鐵則：節點縱距另以「全桁架節點法」聯立解出比對；最大值另以卡車位置逐 1 cm 掃描確認。
"""
import sys, os
from fractions import Fraction as Fr

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2004-2"

# ── 幾何（題目正本判讀清單 #1–#5）──
N = {"a": (0, 0), "b": (10, 0), "c": (20, 0), "d": (30, 0), "e": (40, 0),
     "B": (10, 10), "C": (20, 10), "D": (30, 10)}
M = [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("B", "C"), ("C", "D"),
     ("a", "B"), ("D", "e"), ("B", "b"), ("C", "c"), ("D", "d"), ("B", "c"), ("c", "D")]
SPAN = 40
DECK = ["a", "b", "c", "d", "e"]
# ── 卡車（判讀清單 #7–#9）：由車頭 ① 起算的軸位置與軸重 ──
AXLE_OFF = [Fr(0), Fr(24, 10), Fr(39, 10), Fr(54, 10)]
AXLE_P = [20, 40, 40, 40]


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


def truss(node):
    """節點 node 受向下單位力：回傳 (R_a, F_bc)。a 鉸、e 滾。"""
    nodes = list(N)
    unk = M + ["Ax", "Ay", "Ey"]
    A = [[Fr(0)] * len(unk) for _ in range(2 * len(nodes))]
    rhs = [Fr(0)] * (2 * len(nodes))
    for k, (i, j) in enumerate(M):
        (xi, yi), (xj, yj) = N[i], N[j]
        L = Fr(round(((xj - xi) ** 2 + (yj - yi) ** 2) ** 0.5 * 10 ** 9), 10 ** 9)
        cx, cy = (xj - xi) / L, (yj - yi) / L
        r, s = nodes.index(i), nodes.index(j)
        A[2 * r][k] += cx; A[2 * r + 1][k] += cy
        A[2 * s][k] -= cx; A[2 * s + 1][k] -= cy
    A[2 * nodes.index("a")][len(M)] = Fr(1)
    A[2 * nodes.index("a") + 1][len(M) + 1] = Fr(1)
    A[2 * nodes.index("e") + 1][len(M) + 2] = Fr(1)
    rhs[2 * nodes.index(node) + 1] += 1
    sol = _solve(A, rhs)
    return sol[len(M) + 1], sol[M.index(("b", "c"))]


# ── §4 影響線（閉合式）──
def IL_Ra(x):
    return 1 - Fr(x) / SPAN


def IL_Fbc(x):
    x = Fr(x)
    return 3 * x / 40 if x <= 10 else 1 - x / 40


def _selftest():
    for n_ in DECK:
        ra, fbc = truss(n_)
        x = N[n_][0]
        assert abs(float(ra - IL_Ra(x))) < 1e-9 and abs(float(fbc - IL_Fbc(x))) < 1e-9, n_


_selftest()


def response(il, head):
    """車頭 ① 在 head；只計在橋面 0–40 m 上的軸"""
    tot = Fr(0)
    for off, p in zip(AXLE_OFF, AXLE_P):
        x = head + off
        if 0 <= x <= SPAN:
            tot += p * il(x)
    return tot


RA_MAX = response(IL_Ra, 0)
FBC_MAX = response(IL_Fbc, 10 - AXLE_OFF[1])
assert RA_MAX == Fr(1283, 10) and FBC_MAX == Fr(969, 10)                       # §4：128.3、96.9
_heads = [Fr(i, 100) - Fr(54, 10) for i in range(0, 4541)]                      # 逐 1 cm 掃描
assert max(response(IL_Ra, h) for h in _heads) == RA_MAX
assert max(response(IL_Fbc, h) for h in _heads) == FBC_MAX
assert min(response(IL_Fbc, h) for h in _heads) >= 0                            # bc 桿不會受壓


# ══════════════════ 版面 ══════════════════
W, PADL, PADR = 1040, 80, 80
SX = (W - PADL - PADR) / SPAN
PH = 400


def panel(title, sub, il, head, pxu, col, fill, peak_lab, summary):
    cv = Canvas(W, PH, sx=SX, ox=PADL, oy=100)
    cv.panel(title, sub)
    for n_ in DECK:
        p = cv.X(N[n_][0])
        cv.parts.append(f'<line x1="{p:.2f}" y1="72" x2="{p:.2f}" y2="{PH - 34}" '
                        f'stroke="#E6EAF0" stroke-width="1" stroke-dasharray="3 4"/>')
        cv.text_px(p, PH - 18, n_ + ("（鉸）" if n_ == "a" else "（滾）" if n_ == "e" else ""),
                   12.5, "#9AA4B2", weight="700")
    k = pxu / SX
    xs = [0, 10, 20, 30, 40]
    pts = [(x, float(il(x)) * k) for x in xs]
    cv.polygon([(0, 0.0)] + pts + [(SPAN, 0.0)], fill)
    cv.poly(pts, col, 2.4)
    cv.line((0, 0), (SPAN, 0), C["muted"], 1.6)
    for lab, x, dx, dy, anc in peak_lab:
        cv.dot((x, float(il(x)) * k), 4.0, fill=col)
        cv.text_px(cv.X(x) + dx, cv.Y(float(il(x)) * k) + dy, lab, 13, col, weight="700", anchor=anc)
    top = max(float(il(head + o)) for o in AXLE_OFF) * k
    for i, (off, p) in enumerate(zip(AXLE_OFF, AXLE_P)):
        x = float(head + off)
        y = float(il(head + off)) * k
        cv.parts.append(f'<line x1="{cv.X(x):.2f}" y1="{cv.Y(0):.2f}" x2="{cv.X(x):.2f}" y2="{cv.Y(y):.2f}" '
                        f'stroke="{C["load"]}" stroke-width="1.2" stroke-dasharray="2 3"/>')
        cv.dot((x, y), 3.4, fill=C["load"])
        cv.arrow((x, top + 52 / SX), (x, top + 14 / SX), C["load"], 2.2, head=7)
    cv.text_px(cv.X(float(head)) - 6, cv.Y(top) - 60, "← ① 20　② 40　③ 40　④ 40 kN", 12.5,
               C["load"], weight="700", anchor="start")
    cv.text_px(W / 2, PH - 52, summary, 13.5, C["text"], weight="700")
    return cv


def fig2_influence_lines():
    """攔：(1) R_a 把較重的 40 kN 軸放在 a、讓車頭 20 kN 離開橋面——少了 20×1.0，多不回來；
    (2) F_bc 把峰值放在跨中 c（簡支梁直覺）——斷面在 b–c 節間，對 B 取矩，峰值在 b、縱距 0.75；
    (3) 峰值上放 ① 或 ③——依載重判定準則，② 越過 b 時 dF/dx 由負轉正，② 在 b 才是最大。"""
    ra_y = [IL_Ra(o) for o in AXLE_OFF]
    fb_y = [IL_Fbc(10 - AXLE_OFF[1] + o) for o in AXLE_OFF]
    p1 = panel("IL of R_{a}（a 點垂直反力）＋ 最不利位置：車頭 ① 在 a",
               "整體 ΣM_{e} = 0　│　直線 1 → 0；縱距無因次", IL_Ra, Fr(0), 160.0, C["deform"], C["fill_c"],
               [("1.0", 0, -10, 0, "end")],
               "y = " + "、".join(f"{float(v):g}" for v in ra_y) +
               f"　⇒　R_{{a,max}} = ΣP·y = {float(RA_MAX):g} kN（↑）")
    p2 = panel("IL of F_{bc}（bc 桿內力，拉為正）＋ 最不利位置：② 在 b",
               "切 BC、Bc、bc 三桿，對 B 取矩　│　峰值 0.75 在 b（x = 10 m）；全線為正", IL_Fbc,
               10 - AXLE_OFF[1], 200.0, C["tension"], C["fill_t"],
               [("0.75（峰值，b）", 10, 120, 64, "middle"), ("0.5", 20, 0, -16, "middle")],
               "y = " + "、".join(f"{float(v):g}" for v in fb_y) +
               f"　⇒　F_{{bc,max}} = ΣP·y = {float(FBC_MAX):g} kN（拉）")
    return compose([p1, p2], cols=1,
                   note="卡車依考卷箭頭由右往左、① 為車頭；兩個最大值均經卡車位置逐 1 cm 掃描確認",
                   path=f"{OUT}/{TAG}-fig-2-influence-lines.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig2_influence_lines()
    print("寫出", f"{TAG}-fig-2-influence-lines.svg")
    print(f"R_a,max = {float(RA_MAX)} kN   F_bc,max = {float(FBC_MAX)} kN")
    for n_ in DECK:
        ra, fbc = truss(n_)
        print(f"  節點 {n_}: R_a = {float(ra):.4f}  F_bc = {float(fbc):+.4f}")
