#!/usr/bin/env python3
"""SA-2024-4：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2024-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2024-4_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2024-4"

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

# ── 判讀清單 #1–#6（L 取 1 個模型單位）──
SPEC = dict(
    nodes={"A": (0, 0), "B": (0, 2), "C": (1, 2), "D": (1, 0)},              # #1
    members=[dict(ij=("A", "B"), thick=True), dict(ij=("B", "C")), dict(ij=("D", "C"), thick=True)],   # #2 柱 2EI（畫粗）
    supports=[("A", "fixed"), ("D", "fixed")],                                # #4
    loads=[("B", (0.55, 0), "P", (-16, -14))],                                # #5
    labels={"A": (-20, 4), "B": (-14, -16), "C": (16, -16), "D": (20, 4)},
    mlabels=[((-0.1, 1.0), "2EI", None, "end"), ((1.1, 1.0), "2EI", None, "start"), ((0.5, 2.12), "EI", None, "middle")],
    dims=[((0, 0), (0, 2), "2L", -95), ((1, 0), (1, 2), "2L", 95), ((0, 2), (1, 2), "L", 60)],
    extra_pts=[(-0.75, 2.3), (1.6, -0.2)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 560, 560,
                          note="L = 7 m、EI = 425,000 kN-m^{2}；M_{pb} = 300、M_{pc} = 580 kN-m；A、D 固定，P 作用於 B")

FIGURES = [(fig1_problem, "柱、梁剛度或長度讀反；P 作用點讀錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
