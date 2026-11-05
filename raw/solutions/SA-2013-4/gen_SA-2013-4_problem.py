#!/usr/bin/env python3
"""SA-2013-4：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2013-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2013-4_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2013-4"

def _post(fn, post):
    """在 problem_figure 存檔前補畫（自由度箭頭、彈簧符號等），不改共用程式庫。"""
    orig = Canvas.save
    def save(self, path):
        post(self); return orig(self, path)
    Canvas.save = save
    try: return fn()
    finally: Canvas.save = orig

def dof(cv, p, d, lab, L=0.55, lo=(0, 0)):
    """自由度箭頭（藍色）：p 為節點，d 為方向，lab 為編號。"""
    q = (p[0] + d[0]*L, p[1] + d[1]*L)
    cv.arrow(p, q, C["deform"], 2.2, 9)
    cv.math(q, lab, 14, C["deform"], "middle", dx=lo[0], dy=lo[1], weight="700")

# ── 判讀清單 #1–#6 ──
N_ = {"A": (0, 0), "B": (14, 0), "D": (6, 6), "C": (0, 6)}                    # #1 #2（CD = 6 m，C 在 A 正上方）
SPEC = dict(
    nodes=N_, members=[],
    truss=[("C", "D"), ("A", "D"), ("D", "B"), ("A", "B")],                   # #3
    joints=list(N_),
    supports=[("A", "pin"), ("C", "pin"), ("B", "roller")],                   # #4
    labels={"A": (-18, -10), "B": (14, -16), "C": (-18, -12), "D": (2, 20)},
    dims=[((0, 0), (6, 0), "6 m", 66), ((6, 0), (14, 0), "8 m", 66), ((0, 0), (0, 6), "6 m", -70)],
    extra_pts=[(-1.6, 8.0), (16.4, -1.0)])

def _dofs(cv):                                                                # #5
    dof(cv, N_["B"], (1, 0), "P_{1}, d_{1}", 1.6, (34, 0))
    dof(cv, N_["D"], (1, 0), "P_{2}, d_{2}", 1.6, (34, 0))
    dof(cv, N_["D"], (0, 1), "P_{3}, d_{3}", 1.6, (0, -12))

def fig1_problem():
    return _post(lambda: problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 720, 460,
                 note="A、C 鉸支承，B 滾支承；E = 200 GPa、A = 10×10^{3} mm^{2}（各桿相同）"), _dofs)

FIGURES = [(fig1_problem, "CD 長度讀錯、d₁ 位置或 d₂／d₃ 方向對錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
