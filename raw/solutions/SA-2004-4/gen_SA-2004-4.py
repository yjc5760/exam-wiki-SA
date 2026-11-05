#!/usr/bin/env python3
"""SA-2004-4：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2004-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2004-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2004-4"

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

# ── 判讀清單 #1–#8（L 取 1 個模型單位）──
SPEC = dict(
    nodes={"A": (0, 0), "C": (1, 0), "B": (3, 0)},                           # #1 #5
    members=[dict(ij=("A", "C")), dict(ij=("C", "B"), thick=True)],          # #6 CB 為 3EI（畫粗）
    supports=[("A", "fixed"), ("B", "roller")],                               # #2 #3
    springs=[("C", 0.55, "k")],                                               # #4
    udl=[("A", "B", 0.32, "w")],                                              # #7
    labels={"A": (-30, -4), "B": (22, -16), "C": (16, 16)},
    mlabels=[((0.5, -0.14), "EI", None, "middle"), ((2.0, -0.16), "3EI", None, "middle")],   # #6
    dims=[((0, 0), (1, 0), "L", 112), ((1, 0), (3, 0), "2L", 112)],          # #5
    extra_pts=[(-0.25, 0.5), (3.2, -0.9)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 680, 400,
                          note="A 固定、B 滾支承；C 為連續節點，下接軸力彈簧 k = 12EI/L^{3}；w 作用於 A–B 全長",
                          margins=(80, 80, 60, 70))

FIGURES = [(fig1_problem, "C 讀成內鉸、CB 段 3EI 漏讀、w 只算到 C")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
