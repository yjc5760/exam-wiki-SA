#!/usr/bin/env python3
"""SA-2008-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2008-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2008-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2008-1"

# ── 判讀清單 #1–#8 ──
N_ = {"A": (0, 0), "C": (10, 0), "E": (20, 0), "B": (10, 5), "D": (20, 10)}  # #4 #5
SPEC = dict(
    nodes=N_, members=[],
    truss=[("A", "B"), ("B", "D"), ("A", "C"), ("C", "E"), ("B", "C"), ("B", "E"), ("D", "E")],  # #6
    joints=list(N_),
    supports=[("A", "roller"), ("E", "pin"), ("D", "roller", 90)],             # #1 #3 #2 D 靠右側牆
    loads=[("B", (0, -2.2), "10 kN", (0, -20))],                               # #8
    labels={"A": (-16, -12), "B": (-14, -16), "C": (0, 22), "D": (-16, -12), "E": (26, 16)},
    dims=[((0, 0), (10, 0), "10 m", 74), ((10, 0), (20, 0), "10 m", 74),
          ((20, 0), (20, 5), "5 m", 70), ((20, 5), (20, 10), "5 m", 70)],
    extra_pts=[(-1, 11), (23.5, -2)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 680, 480,
                          note="A 滾支承（垂直反力）；D 滾支承靠右側牆（水平反力）；E 鉸支承；A、B、D 共線")

FIGURES = [(fig1_problem, "D 讀成垂直反力、E 讀成滾支承")]

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

# ── 解題圖（階段 E，2026-11-07）：桿力與反力取自 SA-2008-1.md §4 步驟 5（X = D_x = (175√5 − 95)/44）──
from recipes import truss_forces
R5 = math.sqrt(5); X8 = (175*R5 - 95)/44
F8 = {("A", "C"): 10 - X8, ("C", "E"): 10 - X8, ("A", "B"): -5*R5 + 0.5*R5*X8, ("B", "C"): 0.0,
      ("B", "E"): -5*R5, ("B", "D"): 0.5*R5*X8, ("D", "E"): -0.5*X8}
R8 = {"A": (0, 5 - 0.5*X8), "D": (X8, 0), "E": (-X8, 5 + 0.5*X8)}

def fig2_truss():
    _truss_check(N_, F8, {**R8, "B": (0, -10)})
    _truss(N_, [(i, j, v) for (i, j), v in F8.items()],
                        supports=[("A", "roller", 0), ("E", "pin", 0), ("D", "roller", 90)],
                        loads=[("B", (0, -2.4), "10 kN")], fmt=FMT,
                        title=f"圖 2　{TAG} 桿力（kN，拉＋）",
                        note="反力：A_y 1.63↑；D_x 6.73→（牆對 D 為拉力）；E_x 6.73←、E_y 8.37↑。CB 為零桿（C 點無垂直力）",
                        path=f"{OUT}/{TAG}-fig-2-truss.svg", W=760, H=560)
    return f"{OUT}/{TAG}-fig-2-truss.svg"

FIGURES.append((fig2_truss, "CB 當成受力桿；D_x 方向畫成向左（受壓）"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
