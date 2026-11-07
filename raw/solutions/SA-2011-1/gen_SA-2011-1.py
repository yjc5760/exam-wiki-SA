#!/usr/bin/env python3
"""SA-2011-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2011-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2011-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2011-1"

# ── 判讀清單 #1–#5 ──
N_ = {"D": (0, 0), "E": (4, 0), "F": (8, 0), "A": (0, 3), "B": (4, 3), "C": (8, 3)}  # #4
SPEC = dict(
    nodes=N_, members=[],
    truss=[("A", "B"), ("B", "C"), ("D", "E"), ("E", "F"), ("A", "D"), ("B", "E"),
           ("C", "F"), ("A", "E"), ("C", "E")],                               # #5 九桿
    joints=list(N_),
    supports=[("A", "roller", -90), ("D", "pin"), ("F", "roller")],          # #1 #2 #3
    labels={"A": (8, -20), "B": (0, -18), "C": (0, -18), "D": (-24, 0), "E": (0, 24), "F": (24, 0)},
    dims=[((0, 0), (4, 0), "4 m", 74), ((4, 0), (8, 0), "4 m", 74), ((8, 0), (8, 3), "3 m", 66)],
    extra_pts=[(-1.4, 3.4), (9.6, -1.4)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 620, 460,
                          note="A 滾支承靠左側牆（只約束水平）；D 鉸支承；F 滾支承（只約束垂直）")

FIGURES = [(fig1_problem, "A 讀成鉸支承、支承位置誤差方向讀錯")]

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

# ── 解題圖（階段 E，2026-11-07）：取自 SA-2011-1.md §4 Step 1、3（無外載，基本結構桿力為 0；N = u·X）──
from recipes import truss_forces
X11 = (-0.0285 + 0.016296)/0.000134375                     # Step 3：X = −90.82 kN（A 水平反力，向右為正）
U11 = {("A", "B"): -1/2, ("B", "C"): -1/2, ("D", "E"): 1, ("E", "F"): 0, ("A", "D"): 3/8, ("B", "E"): 0,
       ("C", "F"): -3/8, ("A", "E"): -5/8, ("C", "E"): 5/8}
F11 = {k: u*X11 for k, u in U11.items()}
R11 = {"A": (X11, 0), "D": (-X11, -3/8*X11), "F": (0, 3/8*X11)}

def fig2_truss():
    _truss_check(N_, F11, R11)
    _truss(N_, [(i, j, v) for (i, j), v in F11.items()],
                        supports=[("A", "roller", -90), ("D", "pin", 0), ("F", "roller", 0)],
                        loads=[], fmt=FMT,
                        title=f"圖 2　{TAG} 桿力（kN，拉＋）—— 只由溫度、製造誤差與支承偏位引起",
                        note="反力：A_x 90.82←、D_x 90.82→、D_y 34.06↑、F_y 34.06↓。BE（升溫）、EF（短 1 cm）有初始變形，仍是零桿",
                        path=f"{OUT}/{TAG}-fig-2-truss.svg", W=760, H=520)
    return f"{OUT}/{TAG}-fig-2-truss.svg"

FIGURES.append((fig2_truss, "有溫度或製造誤差的桿（BE、EF）就以為一定受力；A 偏左的符號弄反"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
