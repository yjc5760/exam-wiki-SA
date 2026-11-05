#!/usr/bin/env python3
"""SA-2004-1：題目附圖重繪（struct-diagram 規範；2026-11-05）
幾何、支承、載重逐項對應題目正本 SA-2004-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2004-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2004-1"

# ── 判讀清單 #1–#7 ──
SPEC = dict(
    nodes={"A": (0, 0), "M": (0, 2), "B": (0, 4), "C": (4, 4), "R": (6, 4)},   # #4 #5
    members=[dict(ij=("A", "B")), dict(ij=("B", "R"))],
    supports=[("A", "fixed"), ("C", "roller")],                               # #1 #3
    hinges=["B"],                                                             # #2
    udl=[("B", "R", 0.8, "2 t/m")],                                           # #6
    loads=[("M", (1.2, 0), "4t", (-22, -14))],                                # #7
    labels={"A": (-22, 14), "B": (-18, -10), "C": (24, 20)},
    dims=[((0, 0), (0, 2), "2 m", -105), ((0, 2), (0, 4), "2 m", -105), ((0, 0), (4, 0), "4 m", 48), ((4, 0), (6, 0), "2 m", 48)],
    extra_pts=[(-1.6, 4), (6, -0.6)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 520,
                          note="A 固定；B 鉸接（柱頂與梁）；C 滾支承；2 t/m 作用於梁全長 6 m")

FIGURES = [(fig1_problem, "均布載重只算到 C、4t 作用點讀成柱頂")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
