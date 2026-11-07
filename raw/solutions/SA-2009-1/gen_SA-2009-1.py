#!/usr/bin/env python3
"""SA-2009-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2009-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2009-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2009-1"

# ── 判讀清單 #1–#7 ──
N_ = {"a": (0, 0), "e": (4, 0), "d": (8, 0), "b": (4, 3), "c": (8, 3)}     # #4 #5
SPEC = dict(
    nodes=N_, members=[],
    truss=[("a", "b"), ("b", "c"), ("b", "e"), ("e", "c"), ("c", "d"), ("a", "e"), ("e", "d")],  # #6 #7
    joints=list(N_),
    supports=[("a", "roller"), ("c", "pin", 90), ("d", "roller", 90)],        # #1 #2 #3
    labels={"a": (-16, -14), "b": (-14, -14), "c": (-14, -18), "d": (-14, 22), "e": (0, 22)},
    dims=[((0, 0), (4, 0), "4 m", 74), ((4, 0), (8, 0), "4 m", 74), ((8, 0), (8, 3), "3 m", 90)],
    extra_pts=[(-0.8, 3.5), (10.6, -1.4)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 620, 460,
                          note="a 滾支承（垂直）；c 鉸支承、d 滾支承皆靠右側牆；題文：a 向下沉陷 0.1 m，無外載")

FIGURES = [(fig1_problem, "d 讀成垂直反力、c 讀成滾支承、漏掉 a–b 桿")]

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

# ── 解題圖（階段 E，2026-11-07，勘誤後）：取自 SA-2009-1.md §4 Step 3、5（N = u·X_1，X_1 = 24000/661）──
X9 = 24000/661
U9 = {("a", "b"): 5/8, ("a", "e"): -1/2, ("e", "d"): -1, ("c", "d"): 0, ("e", "c"): 5/8, ("b", "e"): -3/8, ("b", "c"): 1/2}
F9 = {k: (u*X9 if u else 0.0) for k, u in U9.items()}
R9 = {"a": (0, -3/8*X9), "c": (X9, 3/8*X9), "d": (-X9, 0)}

def fig2_truss():
    _truss_check(N_, F9, R9)
    _truss(N_, [(i, j, v) for (i, j), v in F9.items()],
           supports=[("a", "roller", 0), ("c", "pin", 90), ("d", "roller", 90)], loads=[], fmt=FMT,
           title=f"圖 2　{TAG} 桿力（kN，拉＋）—— 只由 a 點下沉 0.1 m 引起",
           note="斜桿為 e–c。反力：a_y 13.62↓、c_x 36.31→、c_y 13.62↑、d_x 36.31←；cd 為零桿",
           path=f"{OUT}/{TAG}-fig-2-truss.svg", W=720, H=520)
    return f"{OUT}/{TAG}-fig-2-truss.svg"

FIGURES.append((fig2_truss, "斜桿畫成 b–d（本題舊版解析）；以為支承沉陷不產生桿力"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
