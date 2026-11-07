#!/usr/bin/env python3
"""SA-2016-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2016-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2016-2_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2016-2"

# ── 判讀清單 ──
L = 1.0
N_ = {"A": (0, 0), "B": (0, L), "C": (L, L)}                                       # #1
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "B")}, {"ij": ("B", "C")}],
    supports=[("A", "fixed"), ("C", "roller")],                                     # #2、#3
    labels={"A": (-30, -4), "B": (-18, -16), "C": (20, -18)},
    dims=[((0, 0), (0, L), "L", -52), ((0, 0), (L, 0), "L", 60)],
    ptexts=[((0.5, 0.86), "移動載重只在 B–C 之間", 12.5, None, "middle")],           # #5
    extra_pts=[(-0.25, 1.15), (1.2, -0.2)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 600, 500,
                          note="A 固定端、B 剛接、C 滾支承（只有垂直反力）；EI 常數，不計軸向變形")

FIGURES = [(fig1_problem, "C 讀成鉸支承、漏讀移動載重只在 BC")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
