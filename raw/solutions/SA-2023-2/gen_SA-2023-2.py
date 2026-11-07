#!/usr/bin/env python3
"""SA-2023-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2023-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2023-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2023-2"

# ── 判讀清單 #1–#7 ──
N_ = {"A": (0, 0), "B": (8, 0), "D": (3, -4), "C": (5, -4)}                # #3
SPEC = dict(
    nodes=N_, members=[],
    truss=[("A", "B"), ("A", "D"), ("A", "C"), ("B", "D"), ("B", "C"), ("D", "C")],  # #4 #5 交叉不相連
    joints=list(N_),
    supports=[("A", "pin", -90), ("D", "roller")],                             # #1 #2
    loads=[("B", (0, -2.0), "30 kN", (34, 0), True)],                          # #7
    labels={"A": (8, -20), "B": (12, -18), "C": (18, 8), "D": (-18, 8)},
    dims=[((0, 0), (3, 0), "3 m", -58), ((3, 0), (5, 0), "2 m", -58), ((5, 0), (8, 0), "3 m", -58),
          ((0, -4), (0, 0), "4 m", -70)],
    extra_pts=[(-1.6, 1.2), (9.5, -5.2)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 600, 480,
                          note="A–C 與 B–D 交叉處沒有節點（兩桿互不相連）；A 鉸支承、D 滾支承")

FIGURES = [(fig1_problem, "交叉點當成節點、D 讀成鉸支承")]

class _Fmt:
    """桿力標籤：零桿顯示 0，其餘帶正負號兩位小數。"""
    def format(self, N):
        return "0" if abs(N) < 1e-9 else f"{N:+.2f}"
FMT = _Fmt()

def _truss(nodes, members, **kw):
    """recipes.truss_forces 的包裝：垂直桿的桿力標籤原本置中在桿旁 17 px，文字會壓到桿件；
    這裡暫時包住 Canvas.math_px，把落在垂直桿上的標籤推到桿件外側（依文字長度），其餘不動。"""
    from structdraw import Canvas
    from recipes import truss_forces
    orig = Canvas.math_px
    verts = [(nodes[i], nodes[j]) for i, j, _ in members if abs(nodes[i][0] - nodes[j][0]) < 1e-9]
    def math_px(self, x, y, s, *a, **k):
        for p, q in verts:
            xm = self.X(p[0]); y0, y1 = sorted((self.Y(p[1]), self.Y(q[1])))
            if abs(x - xm) < 22 and y0 < y < y1:
                x = xm + (1 if x >= xm else -1)*(len(s)*4.6 + 10)
        return orig(self, x, y, s, *a, **k)
    Canvas.math_px = math_px
    try:
        return truss_forces(nodes, members, **kw)
    finally:
        Canvas.math_px = orig
def _truss_check(nodes, F, ext):
    """F: {(i, j): N}（拉＋）；ext: {節點: (Fx, Fy)}（外力＋反力）。每個節點 ΣF = 0。"""
    R = {n: [0.0, 0.0] for n in nodes}
    for (i, j), f in F.items():
        (xi, yi), (xj, yj) = nodes[i], nodes[j]; L = math.hypot(xj-xi, yj-yi)
        R[i][0] += f*(xj-xi)/L; R[i][1] += f*(yj-yi)/L; R[j][0] -= f*(xj-xi)/L; R[j][1] -= f*(yj-yi)/L
    for n, (fx, fy) in ext.items():
        R[n][0] += fx; R[n][1] += fy
    assert max(abs(v) for n in R for v in R[n]) < 1e-9, R

# ── 解題圖（階段 E，2026-11-07）：取自 SA-2023-2.md §4 Step 2–4（S、u 表與 X = F_BD）──
from recipes import truss_forces
R41 = math.sqrt(41); X23 = -(25625 - 1895*R41)/328
S23 = {("A", "B"): 22.5, ("B", "C"): -37.5, ("A", "C"): 7.5*R41, ("D", "C"): -60, ("A", "D"): -100, ("B", "D"): 0}
U23 = {("A", "B"): -2/R41, ("B", "C"): -5/R41, ("A", "C"): 1, ("D", "C"): -8/R41, ("A", "D"): -5/R41, ("B", "D"): 1}
F23 = {k: S23[k] + U23[k]*X23 for k in S23}

def fig2_truss():
    _truss_check(N_, F23, {"A": (0, -50), "D": (0, 80), "B": (0, -30)})
    assert abs(F23[("B", "D")] + 41.13) < 0.005                                   # boxed：41.13 kN 壓力
    _truss(N_, [(i, j, v) for (i, j), v in F23.items()],
                        supports=[("A", "pin", -90), ("D", "roller", 0)],
                        loads=[("B", (0, -1.4), "30 kN")], fmt=FMT,
                        title=f"圖 2　{TAG} 桿力（kN，拉＋）",
                        note="AC 與 BD 交叉處不是節點，兩桿各自受力；BD 受壓 41.13 kN。反力 A_y 50↓、D_y 80↑、A_x 0",
                        path=f"{OUT}/{TAG}-fig-2-truss.svg", W=700, H=560)
    return f"{OUT}/{TAG}-fig-2-truss.svg"

FIGURES.append((fig2_truss, "交叉點當成節點；BD 標成受拉"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
