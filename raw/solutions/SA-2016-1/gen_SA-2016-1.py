#!/usr/bin/env python3
"""SA-2016-1：題目附圖重繪（struct-diagram 規範；2026-11-05）
幾何、支承、載重逐項對應題目正本 SA-2016-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2016-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2016-1"

# ── 判讀清單 #1–#7 ──
SPEC = dict(
    nodes={"A": (0, 0), "B": (0, 2), "C": (2, 2), "D": (4, 2), "E": (4, 0)},   # #5
    members=[dict(ij=("A", "B")), dict(ij=("B", "D")), dict(ij=("E", "D"))],
    supports=[("A", "pin"), ("E", "fixed")],                                  # #1 #2
    hinges=["C"],                                                             # #3
    loads=[("D", (1.0, 0), "50 kN", (34, 0), True)],                          # #6
    labels={"A": (-18, 0), "B": (-14, -14), "C": (0, -18), "D": (14, -14), "E": (24, -12)},
    dims=[((0, 0), (0, 2), "2 m", -60), ((0, 0), (2, 0), "2 m", 62), ((2, 0), (4, 0), "2 m", 62)],
    extra_pts=[(-0.6, 2), (5.6, 2), (0, -0.5)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 620, 440,
                          note="A 鉸支承；E 固定端（柱底直接接剖線，無三角形）；C 為梁中點內鉸；EI 為常數")

FIGURES = [(fig1_problem, "E 讀成鉸支承（本題舊版解析）、C 漏讀內鉸")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
