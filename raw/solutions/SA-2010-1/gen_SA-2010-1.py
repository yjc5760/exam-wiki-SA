#!/usr/bin/env python3
"""SA-2010-1：題目附圖重繪（struct-diagram 規範；2026-11-05）
幾何、支承、載重逐項對應題目正本 SA-2010-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2010-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2010-1"

# ── 判讀清單 #1–#6 ──
N_ = {"G": (0, 0), "H": (4, 0), "C": (0, 2), "D": (2, 2), "E": (4, 2), "F": (6, 2), "A": (2, 4), "B": (6, 4)}   # #1
SPEC = dict(
    nodes=N_, members=[],
    truss=[("A", "B"), ("A", "C"), ("A", "E"), ("E", "B"), ("B", "F"), ("C", "D"), ("D", "E"), ("E", "F"),
           ("C", "G"), ("G", "D"), ("D", "H"), ("G", "H"), ("H", "F")],         # #2
    joints=list(N_),
    supports=[("G", "pin"), ("B", "roller", 90)],                             # #3 #4：B 靠右側垂直牆
    loads=[("H", (0, -1.0), "30 kN", (34, 0), True)],                         # #6
    labels={"A": (-14, -14), "B": (-6, -18), "C": (-18, 0), "D": (0, -16), "E": (0, 18), "F": (16, -10), "G": (-18, -6), "H": (16, 8)},
    dims=[((0, 0), (2, 0), "2 m", 78), ((2, 0), (4, 0), "2 m", 78), ((4, 0), (6, 0), "2 m", 78),
          ((0, 0), (0, 2), "2 m", -62), ((0, 2), (0, 4), "2 m", -62)],
    extra_pts=[(-0.8, 4), (7.0, 4), (6, -1.4)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 520,
                          note="G 鉸支承；B 為靠右側垂直牆的滾支承（反力水平）；E–H 之間沒有桿")

FIGURES = [(fig1_problem, "B 讀成垂直反力的滾支承、多畫 E–H 豎桿")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
