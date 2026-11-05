#!/usr/bin/env python3
"""SA-2025-1：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2025-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2025-1_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2025-1"

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

# ── 判讀清單 #1–#6（L 取 1 個模型單位；考卷附圖無節點字母，重繪不加）──
SPEC = dict(
    nodes={"p1": (0, 0), "p2": (0, 1), "p3": (1, 1), "p4": (1, 0)},          # #1
    members=[dict(ij=("p1", "p2")), dict(ij=("p2", "p3")), dict(ij=("p4", "p3"))],   # #3
    supports=[("p1", "fixed"), ("p4", "fixed")],                              # #4
    loads=[("p3", (0.38, 0), "P", (14, 0), True)],                            # #5
    mlabels=[((0.1, 0.5), "EI", None, "start"), ((0.9, 0.5), "EI", None, "end"), ((0.5, 0.9), "EI", None, "middle")],   # #2
    dims=[((0, 0), (0, 1), "L", -60), ((1, 0), (1, 1), "L", 60), ((0, 0), (1, 0), "L", 52)],
    extra_pts=[(-0.35, 1.1), (1.55, -0.2)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 560, 500,
                          note="兩柱底固定、梁柱垂直剛接；梁柱 EI、L 相同；P 作用於右上角點")

FIGURES = [(fig1_problem, "P 作用點或柱底支承讀錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
