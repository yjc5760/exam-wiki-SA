#!/usr/bin/env python3
"""SA-2018-2：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2018-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2018-2_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2018-2"

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

# ── 判讀清單 #1–#4（L 取 1 個模型單位）──
SPEC = dict(
    nodes={"A": (0, 2), "B": (0, 1), "C": (1, 1), "D": (1, 0), "F": (0.5, 1)},  # #1；F 為 BC 中點
    members=[dict(ij=("A", "B")), dict(ij=("B", "C")), dict(ij=("C", "D"))],    # #2
    supports=[("A", "fixed"), ("D", "fixed")],                                  # #3
    loads=[("F", (0, -0.4), "P", (0, -14))],                                    # #4
    labels={"A": (-20, 8), "B": (-18, 10), "C": (18, -12), "D": (20, -8)},
    dims=[((0, 1), (0, 2), "L", -60), ((0, 1), (1, 1), "L", -60), ((1, 0), (1, 1), "L", 60)],
    extra_pts=[(-0.45, 2.15), (1.45, -0.15)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 520, 560,
                          note="A（上）、D（下）皆固定；B、C 剛接；P 作用於 BC 中點；各桿 EI、L 相同")

FIGURES = [(fig1_problem, "Z 字形讀成鏡射對稱、P 作用點讀錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
