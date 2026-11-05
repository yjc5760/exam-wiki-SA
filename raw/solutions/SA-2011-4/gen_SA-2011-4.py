#!/usr/bin/env python3
"""SA-2011-4：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2011-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2011-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2011-4"

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
N_ = {"C": (0, 0), "D": (6, 0), "A": (3, 4), "B": (0, 4)}                     # #1
SPEC = dict(
    nodes=N_, members=[],
    truss=[("B", "A"), ("C", "A"), ("D", "A")],                               # #2
    joints=["A"],
    supports=[("C", "pin"), ("D", "pin"), ("B", "pin", -90)],                 # #3 #4（D 為鉸支承，非滾支承）
    labels={"A": (-16, -14), "B": (-6, 20), "C": (-20, -8), "D": (-20, -10)},
    dims=[((0, 0), (3, 0), "3 m", 64), ((3, 0), (6, 0), "3 m", 64), ((0, 0), (0, 4), "4 m", -82)],
    ptexts=[((1.05, 2.0), "AC 桿短 0.02 m", 14, "#C0392B", "end")],           # #5
    extra_pts=[(-2.0, 4.9), (7.1, -1.4)])

def _dofs(cv):                                                                # #6 自由度編號
    for nd, nx, ny in (("A", "1", "2"), ("B", "3", "4"), ("C", "5", "6"), ("D", "7", "8")):
        p = N_[nd]
        dof(cv, p, (1, 0), nx, 0.75, (10, 0)); dof(cv, p, (0, 1), ny, 0.75, (0, -10))
    cv.axes((-1.9, -1.2), 0.7, 0.7)

def fig1_problem():
    return _post(lambda: problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 520,
                 note="B 接左側牆、C 與 D 為鉸支承；無外加載重，唯一作用是 AC 桿組裝前短 0.02 m"), _dofs)

FIGURES = [(fig1_problem, "D 讀成滾支承、自由度編號對錯節點")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
