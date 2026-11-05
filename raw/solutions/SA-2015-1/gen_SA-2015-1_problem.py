#!/usr/bin/env python3
"""SA-2015-1：題目附圖重繪（struct-diagram 規範；2026-11-05）
幾何、支承、載重逐項對應題目正本 SA-2015-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2015-1_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2015-1"

# ── 判讀清單 #1–#9 ──
N_ = {"A": (0, 0), "C": (4, 0), "D": (8, 0), "B": (4, 3)}                    # #1
SPEC = dict(
    nodes=N_, members=[],
    truss=[("A", "B"), ("B", "C"), ("B", "D"), ("A", "C"), ("C", "D")],        # #2
    joints=list(N_),
    supports=[("A", "pin"), ("C", "roller")],                                 # #3
    loads=[("B", (-1.6, 0), "T", (-14, 0), True), ("D", (0, -1.6), "50 kN", (34, 0), True)],   # #4 #5
    labels={"A": (-16, -10), "B": (0, -18), "C": (14, -14), "D": (16, -8)},
    ptexts=[((6.3, 2.0), "BD 縮短 0.5 cm", 13, None, "start")],
    dims=[((0, 0), (4, 0), "4 m", 70), ((4, 0), (8, 0), "4 m", 70), ((8, 0), (8, 3), "3 m", 80)],
    extra_pts=[(-1.8, 3), (9.8, 3)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 680, 440,
                          note="A 鉸、C 滾支承（C 下陷 0.4 cm）；BD 較原設計縮短 0.5 cm；EA = 2×10^5 kN；求使 D 垂直位移為零的 T")

FIGURES = [(fig1_problem, "T 方向讀反、C 支承讀成鉸")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
