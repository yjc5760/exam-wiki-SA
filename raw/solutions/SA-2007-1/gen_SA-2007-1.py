#!/usr/bin/env python3
"""SA-2007-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2007-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2007-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2007-1"

# ── 判讀清單 #1–#6 ──
N_ = {"A": (0, 0), "B": (4.5, 0), "C": (9, 0), "D": (0, 6), "E": (9, 6)}   # #2 #4
SPEC = dict(
    nodes=N_, members=[],
    truss=[("A", "D"), ("D", "E"), ("D", "B"), ("B", "E"), ("E", "C")],       # #3 五桿
    joints=list(N_),
    supports=[("A", "pin"), ("B", "pin"), ("C", "pin")],                       # #1
    loads=[("E", (2.0, 0), "60 kN", (36, 0), True)],                           # #6
    labels={"A": (-18, 0), "B": (18, -6), "C": (18, 0), "D": (-16, -14), "E": (12, -18)},
    dims=[((0, 0), (4.5, 0), "4.5 m", 66), ((4.5, 0), (9, 0), "4.5 m", 66), ((0, 0), (0, 6), "6 m", -62)],
    extra_pts=[(-1.4, 6.5), (12, -1.4)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 500,
                          note="A、B、C 皆鉸支承；各桿 A＝1000 mm²、E＝200 GPa")

FIGURES = [(fig1_problem, "支承讀成滾支承（變靜定）、漏掉 B 點兩斜桿交會")]

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

# ── 解題圖（階段 E，2026-11-07）：桿力與反力取自 SA-2007-1.md §4 Step 5–6（X = F_DE = 1890/72）──
from recipes import truss_forces
X7 = 1890/72
F7 = {("A", "D"): 4/3*X7, ("D", "E"): X7, ("D", "B"): -5/3*X7, ("B", "E"): 100 - 5/3*X7, ("E", "C"): -80 + 4/3*X7}
R7 = {"A": (0, -35), "B": (-60, -10), "C": (0, 45)}

def fig2_truss():
    _truss_check(N_, F7, {**R7, "E": (60, 0)})
    cv = _truss(N_, [(i, j, v) for (i, j), v in F7.items()],
                        supports=[("A", "pin", 0), ("B", "pin", 0), ("C", "pin", 0)],
                        loads=[], fmt=FMT,
                        title=f"圖 2　{TAG} 桿力（kN，拉＋）",
                        note="反力：A 35↓；B 60←、10↓；C 45↑（A、C 只接垂直桿，水平反力為 0，60 kN 全由 B 承擔）",
                        path=None, W=760, H=560)
    E = N_["E"]; cv.arrow((E[0] + 0.25, E[1]), (E[0] + 1.6, E[1]), C["load"], 3.4, 12)      # 60 kN 自 E 向右（不與 DE 重疊）
    cv.math_px(cv.X(E[0] + 0.95), cv.Y(E[1]) - 16, "60 kN", 16, C["load"], weight="700")
    cv.save(f"{OUT}/{TAG}-fig-2-truss.svg")
    return f"{OUT}/{TAG}-fig-2-truss.svg"

FIGURES.append((fig2_truss, "A、C 也分擔水平反力；B 的水平反力方向畫反"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
