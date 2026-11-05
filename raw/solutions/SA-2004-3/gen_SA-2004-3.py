#!/usr/bin/env python3
"""SA-2004-3：題目附圖重繪（struct-diagram 規範；2026-11-05）
幾何、支承、載重逐項對應題目正本 SA-2004-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2004-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2004-3"

# ── 判讀清單 #1–#8 ──
SPEC = dict(
    nodes={"A": (0, 0), "B": (30, 0), "C": (48, 0), "D": (60, 0)},            # #5
    members=[dict(ij=("A", "B"), thick=True), dict(ij=("B", "D"))],
    supports=[("A", "fixed")],                                                # #1
    hinges=["B"],                                                             # #2
    springs=[("C", 9, "k")],                                                  # #3
    loads=[("B", (0, -9), "36t", (0, -14)), ("D", (0, -9), "36t", (0, -14))],   # #7
    labels={"A": (-20, -14), "B": (-12, 18), "C": (0, -18), "D": (16, 0)},
    mlabels=[((15, 1.6), "2EI", None, "middle"), ((39, 1.6), "EI", None, "middle"), ((54, 1.6), "EI", None, "middle")],   # #6
    dims=[((0, 0), (30, 0), "30 m", 120), ((30, 0), (48, 0), "18 m", 120), ((48, 0), (60, 0), "12 m", 120)],
    extra_pts=[(0, -16), (61, 0)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 820, 360,
                          note="A 固定；B 內鉸；C 彈簧 k = 10^4 t/m；EI = 1×10^6 t-m²", margins=(90, 90, 60, 70))

FIGURES = [(fig1_problem, "B 讀成剛接、AB 剛度 2EI 漏讀")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
